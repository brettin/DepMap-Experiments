import sys
import pandas as pd
import time
import datetime
import requests
import json
import subprocess

# Make a GET request for each term to get a list of pmc ids for a given search term
# https://www.ncbi.nlm.nih.gov/pmc/?term=open%20access%5Bfilter%5D
def get_pmcids(term):
    url = f'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?'
    url = url + f'db=pmc&term={term}+AND+free+fulltext%5bfilter%5d&retmode=json'

    response = requests.get(url, ) #headers=headers, data=data)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Print the response
        json_response = response.json()
        arr = json_response['esearchresult']['idlist']

    else:
        # Print the error message
        print(f"Error: {response.status_code} - {response.text}")
        arr = []

    return arr

def get_pdf(pmcid):
    PMCLink="http://www.ncbi.nlm.nih.gov/pmc/articles/"
    #user_agent = "Mozilla/5.0 (Windows NT 5.2; rv:2.0.1) Gecko/20100101 Firefox/4.0.1"

    pdf_url = PMCLink + pmcid + '/pdf/'
    print (pdf_url)
    response = requests.get(pdf_url, ) #headers={'User-Agent': user_agent})

    wget_command = [f'/usr/bin/wget',
           f'--user-agent="Mozilla/5.0 (Windows NT 5.2; rv:2.0.1) Gecko/20100101 Firefox/4.0.1"',
           f'-q',
           f'-l1',
           f'--no-parent',
           f'-A.pdf',
           f'-O{pmcid}.pdf',
           pdf_url,
           # '2>/dev/null'
          ]
    # Execute the wget command
    try:
        subprocess.run(wget_command, check=True, ) #stderr=subprocess.DEVNULL)
        print(f"{pmcid} PDF downloaded successfully!")
    except subprocess.CalledProcessError as e:
        print(" ".join(wget_command), "failed")
        print(f"Failed to download {pmcid} PDF. Error: {e}")

    return

def restart(term, df):
    column_name = 'CellLineName'
    search_string = term
    # Finding the first occurrence of the string in the specified column
    mask = df[column_name] == term # exact match
    first_occurrence_index = mask.idxmax() if any(mask) else None
    # Getting the row if needed
    first_occurrence_row = df.loc[first_occurrence_index] if first_occurrence_index is not None else None
    if first_occurrence_index is not None:
        new_df = df.loc[first_occurrence_index + 1:]
    else:
        new_df = pd.DataFrame()  # Return an empty DataFrame if no occurrence is found
    # Output the result
    print(f"First occurrence index: {first_occurrence_index}")
    print(f'New shape: {new_df.shape}')
    return new_df

F="depmap/Model.csv.gz"
df=pd.read_csv(F)

if len(sys.argv) > 1:
    print (f'Restarting immediately after {sys.argv[1]}')
    df=restart(sys.argv[1], df)

start = datetime.datetime.now()
for term in df['CellLineName']:
    pmcids = get_pmcids(term)
    for pmcid in pmcids:
        get_pdf(pmcid)
        time.sleep(1)

    print(f'Done dowloading pdfs for {term}')

stop = datetime.d
atetime.now()
