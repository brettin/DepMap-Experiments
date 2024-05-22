offset=$1
start=${offset}
end=$(( offset + 7 ))

echo "$(date) START"

for n in $(seq $start $end) ; do 
	device=$(( n % 8 ))
	echo "CUDA_VISIBLE_DEVICES=$device python ./tool_collection/pull_papers/nougat_pdf.py ./chunks/$n/"
	CUDA_VISIBLE_DEVICES=$device python -u ./tool_collection/pull_papers/nougat_pdf.py ./chunks/$n/ > ./chunks/$n/log &
done

wait

echo "$(date) FINISH"
