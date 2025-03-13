#!/usr/bin/env bash
# Safe build script that only includes existing .md files for Pandoc

# Output file names
OUTPUT_PDF="Book.pdf"
OUTPUT_EPUB="Book.epub"

# PDF engine (change to pdflatex if preferred)
PDF_ENGINE="xelatex"

# Collect markdown files in order, only if they exist
FILES=()

# Helper function to add files if they exist
add_files() {
  for file in $1; do
    if [ -f "$file" ]; then
      FILES+=("$file")
    fi
  done
}

# Add files/folders in intended reading order
add_files "00_Frontmatter/*.md"
add_files "01_Orienterende_Bemaerkninger/*.md"
add_files "02_Oplysninger_Saltfundet_Aegtheden/*.md"
add_files "03_Geologiske_Forhold/*.md"
add_files "04_Sammenfattende_Bemaerkninger/*.md"
add_files "05_Bilag/**/*.md"  # Recursive for bilag and subfolders

# Check if there are any files to process
if [ ${#FILES[@]} -eq 0 ]; then
  echo "No Markdown files found. Nothing to do."
  exit 1
fi

# Build PDF
echo "Building PDF from ${#FILES[@]} files..."
pandoc "${FILES[@]}" --pdf-engine=$PDF_ENGINE -o "$OUTPUT_PDF"
echo "PDF created: $OUTPUT_PDF"

# Build EPUB
echo "Building EPUB from ${#FILES[@]} files..."
pandoc "${FILES[@]}" -o "$OUTPUT_EPUB"
echo "EPUB created: $OUTPUT_EPUB"

# Done
echo "All output files created successfully."
