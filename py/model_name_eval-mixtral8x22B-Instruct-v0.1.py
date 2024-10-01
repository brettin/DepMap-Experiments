#!/usr/bin/env python
# coding: utf-8

# In[1]:


# Arguments
infile='./depmap/Model.csv.gz'
host='127.0.0.1'
port='8000'
model='mistral-community/Mixtral-8x22B-v0.1'
model='mistralai/Mixtral-8x7B-Instruct-v0.1'


# In[2]:


from openai import OpenAI

# Set OpenAI's API key and API base to use vLLM's API server.
openai_api_key = 'EMPTY'
openai_api_base = f"http://{host}:{port}/v1"

client = OpenAI(
    api_key=openai_api_key,
    base_url=openai_api_base,
)


# In[3]:


#from mylib import select_random_element_not_equal_to
#from mylib import load_depmap_data
#from mylib import construct_question
#from mylib import parse_first_json_string

def select_random_element_not_equal_to(array, correct):
    '''
    Given an array of unique answers, select an answer not
    equal to the correct answer.
    '''
    if len(array) == 0:
        raise ValueError("The array is empty")

    # Filter out elements equal to `correct`
    filtered_array = [element for element in array if element != correct]
    
    if not filtered_array:
        raise ValueError("No valid elements to choose from")

    # Select a random element from the filtered list
    return random.choice(filtered_array)


def load_depmap_data(f):
    df=pd.read_csv(f)
    print(f'done importing dataframe (rows, columns) = {df.shape}.')
    return df

def construct_question(df, index, array):
    '''
    Construct a multiple choice question from df using row at index.
    '''
    if index < 0 or index >= len(df):
        raise IndexError("Index out of bounds")
    
    cell_line_name = df.iloc[index]['CellLineName']
    correct_answer = df.iloc[index]['OncotreePrimaryDisease']

    wrong_answer_1 = select_random_element_not_equal_to(array, correct_answer)
    wrong_answer_2 = select_random_element_not_equal_to(array, correct_answer)
    wrong_answer_3 = select_random_element_not_equal_to(array, correct_answer)

    while wrong_answer_1 == wrong_answer_2 or wrong_answer_1 == wrong_answer_3 or wrong_answer_2 == wrong_answer_3:
        wrong_answer_1 = select_random_element_not_equal_to(array, correct_answer)
        wrong_answer_2 = select_random_element_not_equal_to(array, correct_answer)
        wrong_answer_3 = select_random_element_not_equal_to(array, correct_answer)
        
    answers = [correct_answer,
               wrong_answer_1,
               wrong_answer_2,
               wrong_answer_3]
    random.shuffle(answers)

    d = {"a": answers[0],
         "b": answers[1],
         "c": answers[2],
         "d": answers[3],
        }

    for choice in d.keys():
        if d[choice] == correct_answer:
            correct_choice = choice
    
    question = f'''The cell line named {cell_line_name} is a biological model for which primary disease?

a) {d['a']}
b) {d['b']}
c) {d['c']}
d) {d['d']}'''
    
    return question, correct_choice, correct_answer, cell_line_name

def parse_first_json_string(json_string):
    # Find the indicies of the first json_string
    start_index = json_string.find('{')
    end_index = json_string.find('}') + 1

    # Extract the substring between the curly brackets
    extracted_json = json_string[start_index:end_index]

    return extracted_json


# In[ ]:


import json
from tqdm import tqdm
from datetime import datetime

df = load_data(infile)
array = df['OncotreePrimaryDisease'].unique()

sys_reg_prompt = '''You are a cancer research scientist studying the potential effects of various small molecules, peptides, and 
antibiodies on tumor cell growth. You will be presented with a series of multiple choice questions. Please select the correct
choice. Return the answer in json format {"CHOICE": choice, "ANSWER": answer} where choice is only the alphabetic character 
associated with the full answer.'''

_question = '''The cell line named 253J is a biological model for which primary disease?
   
a) Bladder Urothelial Carcinoma
b) Cervical Adenocarcinoma
c) Intracholecystic Papillary Neoplasm
d) Prostate Adenocarcinoma'''

_answer=''' {"CHOICE": "a", "ANSWER": "Bladder Urothelial Carcinoma"}'''


for i in range(0, 1):
    num_correct = 0
    total = 0
    responses = []

    for i in range(df.shape[0]):
        messages = []
        # get question, correct choice and answer
        question, correct_choice, correct_answer, cell_line_name = construct_question(df, i, array)
    
        # construct message
        #messages.append(
        #    {"role": "system",
        #     "content": sys_reg_prompt
        #    }
        #)
        messages.append(
            {"role": "user",
             "content": _question
            }
        )
        messages.append(
            {"role": "assistant",
            "content": _answer
            }
        )
        messages.append(
            { "role": "user",
            "content": question
            }
        )

        chat_response = client.chat.completions.create(
            model=model,
            # logprobs=1,
            # top_logprobs=1,
            messages=messages,
            #temperature=0.0,
            max_tokens=256,
            #stream=False,
        )

        json_string = chat_response.choices[0].message.content.split('[INST]')[0].strip()
        #print(question)
        
        #print(f"Correct answer: {correct_answer}")
        #print(f"Correct coice: {correct_choice}")
        #print(f"Cell line name {cell_line_name}")
        print(f"Model answer: {json_string}\nDone model answer")

        try:
            response = json.loads(json_string)
            response['CORRECT CHOICE'] = correct_choice
            response['CORRECT ANSWER'] = correct_answer
            response['CELL_LINE_NAME'] = cell_line_name
    
            if response['CHOICE'] == correct_choice:
                response['SCORE'] = 1
                num_correct = num_correct + 1
            else:
                response['SCORE'] = 0
    
            total = total + 1
            responses.append(response)
        
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            print(f"The question was: {question}")
            print(f"The response was: {chat_response.choices[0].message.content}")
            print(f"The message was:{messages}")

            response = {}
            response["CHOICE"] =  "e"
            response["ANSWER"] =  chat_response.choices[0].message.content
            response['CORRECT CHOICE'] = correct_choice
            response['CORRECT ANSWER'] = correct_answer
            response['CELL_LINE_NAME'] = cell_line_name
            response['SCORE'] = 0 #  consider making -1
            
            responses.append(response)
            pass

    print(f'{num_correct} correct responses out of {total}')
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

    response_df = pd.DataFrame(responses)
    response_df.to_csv(f'mixtral-8x22B-instruct-v0.1_model_name_eval_{timestamp}.tsv', index=None, sep="\t")

    with open('mixtral-8x22B-instruct-v0.1_model_name_eval_summary.txt', 'a') as f:
        print(f'{timestamp}\t{num_correct} correct responses out of {total}', file=f)


# In[ ]:




