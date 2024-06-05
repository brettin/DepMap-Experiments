offset=$1
chunks=4
start=${offset}
#end=$(( offset + 7 ))
end=$(( offset + chunks - 1 ))

echo "$(date) START"

for n in $(seq $start $end) ; do 
	device=$(( n % 8 + 16))
	echo "CUDA_VISIBLE_DEVICES=$device python ./tool_collection/pull_papers/nougat_pdf.py ./chunks/$n/"
	CUDA_VISIBLE_DEVICES=$device python -u ./tool_collection/pull_papers/nougat_pdf.py ./chunks/$n/ > ./chunks/$n/log &
done

wait

echo "$(date) FINISH"
