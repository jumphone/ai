DIR=$1

for file in ${DIR}/*.pdf; do
    echo ${file}
    pdftotext -layout "$file" "${file%.pdf}.txt"
done


