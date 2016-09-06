#!/bin/zsh
SPATH=$(readlink -f "$0")
DIR=$(dirname "$SPATH")

source "$DIR/.keys.sh"
reportFile=$(python $DIR/download_reports.py)
reportFilePDF="$reportFile.pdf"
mv $reportFile $reportFilePDF
echo "" | mutt -s "Daily Report" n.lefler@gmail.com -a $reportFilePDF
