import os
import csv
import re
import sys
from collections import OrderedDict

def to_roman(num):
    """
    Convert an integer to a Roman numeral.
    """
    val = [
        1000, 900, 500, 400,
        100, 90, 50, 40,
        10, 9, 5, 4,
        1
    ]
    syms = [
        "M", "CM", "D", "CD",
        "C", "XC", "L", "XL",
        "X", "IX", "V", "IV",
        "I"
    ]
    roman_num = ''
    i = 0
    while num > 0:
        count = num // val[i]
        roman_num += syms[i] * count
        num -= val[i] * count
        i += 1
    return roman_num

def sanitize_name(s, max_length=30):
    """
    Remove special characters (only allow alphanumerics and spaces),
    trim whitespace, replace spaces with underscores, and limit length.
    """
    s = re.sub(r'[^A-Za-z0-9 ]+', '', s)
    s = s.strip().replace(' ', '_')
    if len(s) > max_length:
        s = s[:max_length]
    return s

def parse_csv_to_structure(filename):
    """
    Parse the CSV file and build a hierarchical dictionary:
    
    {
      section_number: {
          'title': section_title,
          'appendices': [ { 'num': appendix_number, 'title': appendix_title }, ... ],
          'subsections': {
               subsection_enum: {
                    'title': subsection_title,
                    'appendices': [ { 'num': appendix_number, 'title': appendix_title }, ... ]
               },
               ...
          }
      },
      ...
    }
    """
    sections = OrderedDict()
    with open(filename, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            section_num = row['Section Number'].strip()
            section_title = row['Section Title'].strip()
            subsection_enum = row['Subsection Enumeration'].strip()
            subsection_title = row['Subsection Title'].strip()
            appendix_num = row['Appendix Number'].strip()
            appendix_title = row['Appendix Title'].strip()

            # Create section entry if not exists.
            if section_num not in sections:
                sections[section_num] = {
                    'title': section_title,
                    'appendices': [],
                    'subsections': OrderedDict()
                }

            # Group by subsection if provided; otherwise add directly under the section.
            if subsection_enum:
                if subsection_enum not in sections[section_num]['subsections']:
                    sections[section_num]['subsections'][subsection_enum] = {
                        'title': subsection_title,
                        'appendices': []
                    }
                sections[section_num]['subsections'][subsection_enum]['appendices'].append({
                    'num': appendix_num,
                    'title': appendix_title
                })
            else:
                sections[section_num]['appendices'].append({
                    'num': appendix_num,
                    'title': appendix_title
                })
    return sections

def create_index_md(file_path, title, level, prefix=""):
    """
    Create a Markdown index file that contains only a header with the title.
    The header level is determined by the 'level' parameter.
    The prefix (e.g. Section Number or Subsection Enumeration) will be added before the title.
    """
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(f"{'#' * level} {prefix}{title}\n")

def create_markdown_file(file_path, title, level, appendix_num=None):
    """
    Create a Markdown file for an appendix with a header at the specified level
    and placeholder content.
    
    If 'appendix_num' is provided, a line "Bilag <appendix_num>." is inserted before the content.
    """
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(f"{'#' * level} {title}\n\n")
        if appendix_num:
            f.write(f"Bilag {appendix_num}.\n\n")
        f.write("(Content goes here)\n")

def create_structure(sections, output_dir):
    """
    Create directories and Markdown files based on the parsed CSV structure.
    The Markdown header levels reflect the depth in the hierarchy.
    For section and subsection index files, the Section Number or Subsection Enumeration
    is included in the header. The section number is transformed into a Roman numeral.
    """
    # Create the base output directory if it does not exist.
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Create a top-level index file in the output directory with level 1.
    top_title = os.path.basename(os.path.abspath(output_dir))
    top_index_file = os.path.join(output_dir, "00_INDEX.md")
    create_index_md(top_index_file, top_title, level=1)
    
    # Process sections in sorted order (by section number).
    for sec_key in sorted(sections.keys(), key=lambda x: int(x)):
        section = sections[sec_key]
        # Create section directory (e.g. "01_Undergrundslove_Eneretsbevilling_mm")
        sec_dir_name = f"{int(sec_key):02d}_{sanitize_name(section['title'])}"
        sec_dir_path = os.path.join(output_dir, sec_dir_name)
        os.makedirs(sec_dir_path, exist_ok=True)
        
        # Create an index file for the section with level 2,
        # including the section number as a Roman numeral.
        roman_sec = to_roman(int(sec_key))
        sec_index_file = os.path.join(sec_dir_path, f"00_{sanitize_name(section['title'])}.md")
        create_index_md(sec_index_file, section['title'], level=2, prefix=f"{roman_sec}. ")
        
        # If there are appendices directly under the section, create Markdown files with level 3.
        if section['appendices']:
            sorted_appendices = sorted(section['appendices'], key=lambda x: int(x['num']))
            for idx, appendix in enumerate(sorted_appendices, start=1):
                file_prefix = f"{idx:02d}"
                file_name = f"{file_prefix}_{sanitize_name(appendix['title'])}.md"
                file_path = os.path.join(sec_dir_path, file_name)
                create_markdown_file(file_path, appendix['title'], level=3, appendix_num=appendix['num'])
        
        # Process subsections, if any.
        if section['subsections']:
            # Enumerate subsections sequentially (sorted by the subsection key).
            for sub_index, sub_key in enumerate(sorted(section['subsections'].keys()), start=1):
                subsection = section['subsections'][sub_key]
                sub_dir_name = f"{sub_index:02d}_{sanitize_name(subsection['title'])}"
                sub_dir_path = os.path.join(sec_dir_path, sub_dir_name)
                os.makedirs(sub_dir_path, exist_ok=True)
                
                # Create an index file for the subsection with level 3,
                # including the subsection enumeration.
                sub_index_file = os.path.join(sub_dir_path, f"00_{sanitize_name(subsection['title'])}.md")
                create_index_md(sub_index_file, subsection['title'], level=3, prefix=f"{sub_key}. ")
                
                # Create appendix files in the subsection with level 4.
                sorted_appendices = sorted(subsection['appendices'], key=lambda x: int(x['num']))
                for idx, appendix in enumerate(sorted_appendices, start=1):
                    file_prefix = f"{idx:02d}"
                    file_name = f"{file_prefix}_{sanitize_name(appendix['title'])}.md"
                    file_path = os.path.join(sub_dir_path, file_name)
                    create_markdown_file(file_path, appendix['title'], level=4, appendix_num=appendix['num'])
                    
def main():
    if len(sys.argv) < 2:
        print("Usage: python generate_structure.py <csv_file> [output_directory]")
        sys.exit(1)
    
    csv_file = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "output"
    
    sections = parse_csv_to_structure(csv_file)
    create_structure(sections, output_dir)
    print("Directory structure and Markdown files created successfully.")

if __name__ == "__main__":
    main()