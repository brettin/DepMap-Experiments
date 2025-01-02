import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--port", type=int, default=8000, help="The vLLM port number")
parser.add_argument("--host", type=str, default="localhost", help="The vLLM host name")
parser.add_argument("--model", type=str, default="mistralai/Mixtral-8x7B-Instruct-v0.1", help="repo/model")
parser.add_argument("--key", type=str, default="cmsc-35360", help="The key for vllm server")
parser.add_argument("--replicates", type=int, default=10, help="The number of times to repeat the text.")
parser.add_argument("--file", type=str, default ="./depmap/Model.csv.gz", help="Name of the DepMap file")

args = parser.parse_args()
host = args.host
port = args.port
model = args.model
key = args.key
replicates = args.replicates
f=args.file

print(f'using host: {host}')
print(f'using port: {port}')
print(f'using model: {model}')
print(f'using key: {key}')
print(f'using file: {f}')

parts = model.split("/")
if(len(parts) != 1):
    f_prefix = parts[1]
else:
    f_prefix = parts[0]
f_prefix = f_prefix + "_no_lora"

import pandas as pd
def load_data(f):
    df=pd.read_csv(f)
    print(f'done importing dataframe (rows, columns) = {df.shape}.')
    return df


import random
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
    
    # question = f'''The tumor cell line named {cell_line_name} is
    # question = f'''The tumor cell line named {cell_line_name} is a biological model for which primary disease?
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


# Main

import json
from tqdm import tqdm
from datetime import datetime
from openai import OpenAI

openai_api_base = f"http://{host}:{port}/v1"
client = OpenAI(
    api_key=key,
    base_url=openai_api_base,
)

df = load_data(f)
array = df['OncotreePrimaryDisease'].unique()

sys_reg_prompt = '''You are a cancer research scientist studying the potential
effects of various small molecules, peptides, and antibodies on tumor cell growth.
You will be presented with a series of multiple-choice questions. Please select the
correct choice. Return the answer in JSON format {"CHOICE": "choice", "ANSWER": "answer"}
where choice is only the alphabetic character associated with the full answer.'''

for i in range(0, replicates):
    num_correct = 0
    total = 0
    responses = []
    response = {}

    for i in tqdm( range(df.shape[0]) ):
        question, correct_choice, correct_answer, cell_line_name = construct_question(df, i, array)
        messages=[
            {"role": "system",
             "content": sys_reg_prompt
            },
            {"role": "user",
             "content": question
            },

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
            parse_first_json_string(chat_response.choices[0].message.content)
            response = json.loads(
                    parse_first_json_string(chat_response.choices[0].message.content)
                    )

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
            print(f"QUESTION:\n{question}")
            print(f"MODEL RESPONSE:\n{chat_response.choices[0].message.content}")
            print(f"CORRECT RESPONSE:\n{correct_choice}. {correct_answer}")

            response["CHOICE"] =  "e"
            response["ANSWER"] =  chat_response.choices[0].message.content
            response['CORRECT CHOICE'] = correct_choice
            response['CORRECT ANSWER'] = correct_answer
            response['CELL_LINE_NAME'] = cell_line_name
            response['SCORE'] = 0
            responses.append(response)

            pass
    

    print(f'{num_correct} correct responses out of {total}')
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

    response_df = pd.DataFrame(responses)
    response_df.to_csv(f'{f_prefix}_model_name_eval_{timestamp}.tsv', index=None, sep="\t")

    with open(f'{f_prefix}_model_name_eval_summary.txt', 'a') as f:
        print(f'{timestamp}\t{num_correct} correct responses out of {total}', file=f)

