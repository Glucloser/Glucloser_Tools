#!/bin/zsh

source .keys.sh

ruby ./carelink/carelink_dl.rb

for f in ~/Downloads/Carelink*.csv; do
  echo "Uploading $f"
  python post_to_parse.py $f
  rm $f
done
