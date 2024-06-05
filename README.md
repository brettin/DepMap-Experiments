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
