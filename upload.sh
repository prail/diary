#!/bin/zsh
KEY=$(cut -d " " -f 2 key.txt)
python3.8 gen.py
for file in output/(*.html|*.rss)
do
	req="$(basename -a $file)=@${file}"
	curl -H "Authorization: Bearer ${KEY}" -F $req "https://neocities.org/api/upload"
done
