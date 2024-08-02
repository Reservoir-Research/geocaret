#!/bin/bash

# Input files and output file
file1="$1"
file2="$2"
output="merged.txt"

# Check if both files exist
if [[ ! -f "$file1" ]] || [[ ! -f "$file2" ]]; then
  echo "Both files must exist."
  exit 1
fi

# Read the contents of the second file into a variable
decrypted=$(<"$file2")

# Use diff to create a merged output with custom conflict markers
diff -D AAAAAAA "$file1" <(echo -n "$decrypted") | \
  sed -e $'s/#ifndef AAAAAAA/<<<<<<< file1/g' | \
  sed -e $'s/#endif \/\* ! AAAAAAA \*\//=======\\\n>>>>>>> file2/g' | \
  sed -e $'s/#else \/\* AAAAAAA \*\//=======/g' | \
  sed -e $'s/#ifdef AAAAAAA/<<<<<<< file1\\\n=======/g' | \
  sed -e $'s/#endif \/\* AAAAAAA \*\//>>>>>>> file2/g' > "$output"

echo "Merged file created: $output"
