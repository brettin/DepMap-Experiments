# to chunk for parallel execution
offset=$1 # set this to where you left off plus one.

ls model_pdfs/*.pdf | head -n 2048 > pdf.files

for n in $(cat pdf.files)  ; do
    dir=$(( offset + c%8))
    mkdir -p chunks/$dir
    mv $n chunks/$dir/
    c=$(( c+1 ))
done
