import subprocess
import requests
import time

ids=["11073819"]
PMCLink="http://www.ncbi.nlm.nih.gov/pmc/articles/"
#user_agent = "Mozilla/5.0 (Windows NT 5.2; rv:2.0.1) Gecko/20100101 Firefox/4.0.1"


for id in ids:
    pdf_url = PMCLink + id + '/pdf/'
    print (pdf_url)
    response = requests.get(pdf_url, ) #headers={'User-Agent': user_agent})

    wget_command = [f'/usr/local/bin/wget',
           f'--user-agent="Mozilla/5.0 (Windows NT 5.2; rv:2.0.1) Gecko/20100101 Firefox/4.0.1"',
           f'-l1',
           f'--no-parent',
           f'-A.pdf',
           f'-O{id}.pdf',
           pdf_url,
           # '2>/dev/null'
          ]
    # Execute the wget command
    try:
        subprocess.run(wget_command, check=True, ) #stderr=subprocess.DEVNULL)
        print("PDF downloaded successfully!")
    except subprocess.CalledProcessError as e:
        print(" ".join(wget_command), "failed")
        print(f"Failed to download PDF. Error: {e}")
    
# Check if the request was successful (status code 200)
#if response.status_code == 200:
#    # Open a file in binary write mode to save the PDF
#    with open(id + ".pdf", "wb") as pdf_file:
#        # Write the contents of the response to the file
#        pdf_file.write(response.content)
#    print("PDF downloaded successfully!")
#else:
#    print(f"Failed to download PDF. Status code: {response.status_code}")
    time.sleep(3)

