#!/usr/bin/env bash
# Enable nullglob so that non-matching globs expand to nothing.
shopt -s nullglob

# Output file names
OUTPUT_PDF="Book.pdf"
OUTPUT_EPUB="Book.epub"

# PDF engine (change to pdflatex if preferred)
PDF_ENGINE="xelatex"

# Array to hold the collected Markdown files
FILES=()

# Recursive function to collect .md files in depth-first order.
collect_md_files() {
  local dir="$1"
  # List items in lexicographical order.
  for item in "$dir"/*; do
    if [ -d "$item" ]; then
      # Recursively process directories.
      collect_md_files "$item"
    elif [ -f "$item" ] && [[ "$item" == *.md ]]; then
      FILES+=("$item")
    fi
  done
}

collect_md_files "00_Frontmatter"
collect_md_files "01_Orienterende_Bemaerkninger"
collect_md_files "02_Oplysninger_Saltfundet_Aegtheden"
collect_md_files "03_Geologiske_Forhold"
collect_md_files "04_Sammenfattende_Bemaerkninger"
collect_md_files "05_Bilag"
collect_md_files "06_Bilag_ToC"

# Print out all the found Markdown files.
echo "Markdown files found in depth-first order:"
for mdfile in "${FILES[@]}"; do
  echo "$mdfile"
done

# Exit if no files were found.
if [ ${#FILES[@]} -eq 0 ]; then
  echo "No Markdown files found. Nothing to do."
  exit 1
fi

# Build PDF using Pandoc.
echo "Building PDF from ${#FILES[@]} files..."
pandoc "${FILES[@]}" --pdf-engine="$PDF_ENGINE" -o "$OUTPUT_PDF"
echo "PDF created: $OUTPUT_PDF"

# Build EPUB using Pandoc.
echo "Building EPUB from ${#FILES[@]} files..."
pandoc "${FILES[@]}" -o "$OUTPUT_EPUB"
echo "EPUB created: $OUTPUT_EPUB"

echo "All output files created successfully."