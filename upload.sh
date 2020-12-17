#!/bin/zsh
key=$(grep -Po "(?<=^key ).*" key.txt)
python3.8 gen.py
for file in output/(*.html|*.rss)
do
	req="$(basename -a $file)=@${file}"
	curl -H "Authorization: Bearer ${key}" -F $req "https://neocities.org/api/upload"
done
