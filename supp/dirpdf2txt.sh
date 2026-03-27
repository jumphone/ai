DIR=$1

for file in ${DIR}/*.pdf; do
    echo ${file}
    pdftotext "$file" -raw "${file%.pdf}.txt"
done


