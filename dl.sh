#!/bin/zsh
SPATH=$(readlink -f "$0")
DIR=$(dirname "$SPATH")

source "$DIR/.keys.sh"

xvfb-run --server-args="-screen 0 800x600x16" ruby "$DIR/carelink/carelink_dl.rb"

for f in ~/Downloads/CareLink*.csv; do
  echo "Uploading $f"
  python "$DIR/post_to_parse.py" $f
  rm $f
done
