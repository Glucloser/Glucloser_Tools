#!/bin/zsh
SPATH=$(readlink -f "$0")
DIR=$(dirname "$SPATH")

source "$DIR/.keys.sh"
python $DIR/download_reports.py
