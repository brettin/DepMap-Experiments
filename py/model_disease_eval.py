#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
from openai import OpenAI
import random


# In[2]:


# Arguments
infile='../depmap/Model.csv.gz'
host='127.0.0.1'
host='localhost'
port='9999'
#port='8000'
model='meta-llama/Meta-Llama-3-70B-Instruct'
model='meta-llama/Meta-Llama-3-8B-Instruct'
model='meta-llama/Meta-Llama-3.1-70B-Instruct'
model='llama31-405b-fp8'  # first time server was started with --served-model-name
# --model deepseek-ai/DeepSeek-V3
# --served-model-name deepseekV3
model='deepseekV3'

openai_api_key = 'cmsc-35360'
openai_api_key = 'CELS'
openai_api_base = f"http://{host}:{port}/v1"


# In[3]:


#f_prefix = model.split("/")[1]
# using --served-model-name messed up my code
f_prefix = model

f_prefix = f_prefix + "_no_lora"
f_prefix




# In[4]:


client = OpenAI(
    api_key=openai_api_key,
    base_url=openai_api_base,
)


# In[5]:


def load_data(f):
    df=pd.read_csv(f)
    return df


# In[6]:


def select_random_element_not_equal_to(array, correct):
    '''
    Given an array of unique answers, select an answer not equal to the correct answer.
    '''
    if len(array) == 0:
        raise ValueError("The array is empty")

    # Filter out elements equal to `correct`
    filtered_array = [element for element in array if element != correct]
    
    if not filtered_array:
        raise ValueError("No valid elements to choose from")

    # Select a random element from the filtered list
    return random.choice(filtered_array)


# In[7]:


def remove_correct_cell_line_answers(disease, df):
    '''
    Returns a list of unique cell line names not associated with disease.
    '''
    
    filtered = df[df['OncotreePrimaryDisease'] != disease]
    array = filtered['CellLineName'].unique()
    
    # debug
    # print(f'{df.shape}\t{filtered.shape}')
    # print(f'{len(array)}')
    
    return array


# In[8]:


def construct_question(df, index):
    '''
    Construct a multiple choice question from df using row at index.
    Row at index will have the correct answer.
    The incorrect answers are randomly selected from array.
    '''
    if index < 0 or index >= len(df):
        raise IndexError("Index out of bounds")
    
    disease = df.iloc[index]['OncotreePrimaryDisease']
    correct_answer = df.iloc[index]['CellLineName']
    wrong_answers = remove_correct_cell_line_answers(disease, df)
    
    wrong_answer_1 = select_random_element_not_equal_to(wrong_answers, correct_answer)
    wrong_answer_2 = select_random_element_not_equal_to(wrong_answers, correct_answer)
    wrong_answer_3 = select_random_element_not_equal_to(wrong_answers, correct_answer)

    while wrong_answer_1 == wrong_answer_2 or wrong_answer_1 == wrong_answer_3 or wrong_answer_2 == wrong_answer_3:
        wrong_answer_1 = select_random_element_not_equal_to(wrong_answers, correct_answer)
        wrong_answer_2 = select_random_element_not_equal_to(wrong_answers, correct_answer)
        wrong_answer_3 = select_random_element_not_equal_to(wrong_answers, correct_answer)
        
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
    
    question = f'''The primary disease {disease} can be best studied using which cell line?
a) {d['a']}
b) {d['b']}
c) {d['c']}
d) {d['d']}'''
    
    return question, correct_choice, correct_answer, disease
    


# In[9]:


def debug(index, disease, df, answer):
    '''
    The answer is the name of the cell line associated that can be used as a model for the disease.
    We get all cell lines associated with that disease, and check if answer is in that list.
    '''
    filtered_df = df[df['OncotreePrimaryDisease'] == disease]
    cell_line_names = filtered_df['CellLineName'].values
    filtered_array = [element for element in cell_line_names if element == answer]
    
    #print(cell_line_names)
    #print(filtered_array)

    return filtered_array

def parse_first_json_string(json_string):
    # Find the indicies of the first json_string
    start_index = json_string.find('{')
    end_index = json_string.find('}') + 1

    # Extract the substring between the curly brackets
    extracted_json = json_string[start_index:end_index]

    return extracted_json

# main

import json
from tqdm import tqdm
from datetime import datetime

df = load_data(infile)


sys_reg_prompt = '''You are a cancer research scientist studying the potential effects of various small molecules, peptides, and 
antibiodies on tumor cell growth. You will be presented with a series of multiple choice questions. Please select the correct
choice. Return the answer in json format {"CHOICE": "choice", "ANSWER": "answer"} where choice is only the alphabetic character 
associated with the full answer.'''
# Note, I quoted choice and answer when model upgraded to llama31-405b-fp8

# This is not working yet because the experts talk to each other thus making the
# parsing of the final answer different from the sys_reg_prompt.
sys_tot_prompt = '''Imagine three experts are answering this question.
They will brainstorm the answer step by step, reasoning carefully and taking all facts into consideration.
All experts will write down one step of their thinking, then share it with the group.
They will each critique their response and all the responses of others.
They will check their answer based on science, laws of physics and logic.
Then all experts will go on to the next step and write down this step of their thinking.
They will keep going through steps until they reach their conclusions taking into account the thoughts of the other experts.
If at anytime they realize that there is a flaw in their logic they will backtrack to where the flaw occurred.
If any expert realizes they are wrong at any point they acknowledge this and start another train of thought.
Each expert will assign a likelihood of their current assertion being correct.
Continue until the experts agree on the single most likely choice. Return the response in json format FINAL_ANSWER={"DISCUSSION": discussion, "CHOICE": choice, "ANSWER": answer} where choice is only the alphabetic character 
associated with the full answer.'''
 
for i in range(0, 10): # 9):
    num_correct = 0
    total = 0
    responses = []


    for i in tqdm( range(df.shape[0]) ):
        # get question, correct choice and answer
        question, correct_choice, correct_answer, disease = construct_question(df, i)

        # For debugging.
        #print(f'{question}')
        #print(f'The correct choice is {correct_choice}. {correct_answer}')
        #print(f'The df row has {df.iloc[i]["OncotreePrimaryDisease"]} {df.iloc[i]["CellLineName"]}')
    
        # construct message
        messages=[
            {"role": "system", 
             "content": sys_reg_prompt
            },
            {"role": "user",
             "content": question
            }
        ]
    
        chat_response = client.chat.completions.create(
            model=model,
            # logprobs=1,
            # top_logprobs=1,
            messages=messages,
            temperature=0.0,
            max_tokens=2560,
        )
        
        
        try:
            response = json.loads(
                    parse_first_json_string(chat_response.choices[0].message.content)
                    )

            response['CORRECT CHOICE'] = correct_choice
            response['CORRECT ANSWER'] = correct_answer
            response['PRIMARY_DISEASE'] = disease
    
            if response['CHOICE'] == correct_choice:
                response['SCORE'] = 1
                num_correct = num_correct + 1
            else:
                response['SCORE'] = 0

            total = total + 1
            responses.append(response)

        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            print(f"QUESTION:\n{question}")
            print(f"MODEL RESPONSE:\n{chat_response.choices[0].message.content}")
            print(f"CORRECT RESPONSE:\n{correct_choice}. {correct_answer}")

            response["CHOICE"] =  "e"
            response["ANSWER"] =  chat_response.choices[0].message.content
            response['CORRECT CHOICE'] = correct_choice
            response['CORRECT ANSWER'] = correct_answer
            response['PRIMARY_DISEASE'] = disease
            response['SCORE'] = 0
            responses.append(response)

            pass
            

    print(f'{num_correct} correct responses out of {total}')
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

    response_df = pd.DataFrame(responses)
    response_df.to_csv(f'{f_prefix}_disease_eval_{timestamp}.tsv', index=None, sep="\t")

    with open(f_prefix + '_disease_eval_summary.txt', 'a') as f:
        print(f'{timestamp}\t{num_correct} correct responses out of {total}', file=f)

