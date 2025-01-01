# Python Environment
The python environment is set up for for my host and should be changed according to your host environment.

	sh/env.sh
 

# Multiple Choice Experiments
Running a multiple choice evaluation of the model's understanding of DepMap cell lines.

	py/model_name_eval.py
	py/model_disease_eval.py

Aside from the cell-line name, these are of interest:
df[['OncotreeLineage','OncotreePrimaryDisease','OncotreeSubtype','Age','Sex','PatientRace', 'PrimaryOrMetastasis']]


# DepMap-Experiments
Experiments preparing data for fine-tuning and RAG using DepMap data

## to chunk for parallel execution

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

The cell line named {cell_line_name} is a biological model for which primary disease?
** Has one shot learning built into the prompt. TODO: Depricate OSL or include in other tests.
```

