# DepMap-Experiments
Experiments preparing data for fine-tuning and RAG using DepMap data

Aside from the cell-line name, these are of interest:
df[['OncotreeLineage','OncotreePrimaryDisease','OncotreeSubtype','Age','Sex','PatientRace', 'PrimaryOrMetastasis']]


# to chunk for parallel execution

    ls model_pdfs/*.pdf | head -n 2048 > pdf.files

    offset=8  # set this to where you left off plus one.
 
    for n in $(cat pdf.files)  ; do
	dir=$(( offset + c%8)
	echo "mkdir -p chunks/$dir"
	echo "mv $n chunks/$dir/"
	c=$(( c+1 ))
    done

    for n in $(seq 8 14 ) ; do
	 
	CUDA_VISIBLE_DEVICES=$n 
	python ./tool_collection/pull_papers/nougat_pdf.py ./chunk/$n/
    done

# Files
```
mixtral8x22B.ipynb	This is a simple example of one shot learning. Can				probably be deleted.

model_disease_eval.ipynb
The primary disease {disease} can be best studied using which cell line?

model_name_eval.ipynb
The cell line named {cell_line_name} is a biological model for which primary disease?
** Does not have one shot learing built into the prompt.

model_name_eval-mixtral8x22B-Instruct-v0.1.ipynb
The cell line named {cell_line_name} is a biological model for which primary disease?
** Has one shot learning built into the prompt. TODO: Depricate OSL or include in other tests.


```

