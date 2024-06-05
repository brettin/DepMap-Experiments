# to chunk for parallel execution
offset=$1 # set this to where you left off plus one.
num_chunks=4
num_files=$(( num_chunks * 256 ))

# ls model_pdfs/*.pdf | head -n 2048 > pdf.files
ls model_pdfs/*.pdf | head -n $num_files > pdf.files

for n in $(cat pdf.files)  ; do
    dir=$(( offset + c%num_chunks))
    mkdir -p chunks/$dir
    # echo "mv $n chunks/$dir/"
    mv $n chunks/$dir/
    c=$(( c+1 ))
done
