#!/bin/bash

# Check if pandoc is installed
if ! command -v pandoc &> /dev/null
then
    echo "Pandoc could not be found. Please install pandoc first."
    exit 1
fi

# Directory to search for .md files, default to current directory
DIRECTORY=${1:-.}

# Find and convert all .md files to .rst
find "$DIRECTORY" -type f -name "*.md" | while read -r mdfile; do
    rstfile="${mdfile%.md}.rst"
    pandoc -s "$mdfile" -o "$rstfile"
    echo "Converted $mdfile to $rstfile"
done

echo "Conversion completed."

