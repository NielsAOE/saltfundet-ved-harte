import csv
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

def parse_csv_to_toc(filename):
    """
    Parse the CSV file and group data into a hierarchical dictionary.
    The structure is:
      sections[section_number] = {
          'title': section_title,
          'appendices': [(appendix_number, appendix_title), ...],
          'subsections': {
              subsection_enum: {
                  'title': subsection_title,
                  'appendices': [(appendix_number, appendix_title), ...]
              }
          }
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

            # Create the section if it doesn't exist
            if section_num not in sections:
                sections[section_num] = {
                    'title': section_title,
                    'appendices': [],
                    'subsections': OrderedDict()
                }

            # If a subsection is provided, group under the subsection
            if subsection_enum:
                if subsection_enum not in sections[section_num]['subsections']:
                    sections[section_num]['subsections'][subsection_enum] = {
                        'title': subsection_title,
                        'appendices': []
                    }
                sections[section_num]['subsections'][subsection_enum]['appendices'].append((appendix_num, appendix_title))
            else:
                # Otherwise, add directly under the section
                sections[section_num]['appendices'].append((appendix_num, appendix_title))
    return sections

def generate_markdown_toc(sections):
    """
    Generate the Markdown table of contents from the sections data.
    Section numbers are replaced with Roman numerals.
    """
    lines = []
    lines.append("# BILAGSFORTEGNELSE\n")
    
    # Sort sections numerically by section number
    for section_num in sorted(sections.keys(), key=lambda x: int(x)):
        section = sections[section_num]
        roman_section = to_roman(int(section_num))
        lines.append(f"{section_num}. **{section['title']}**")
        
        # Direct appendices (if any)
        if section['appendices']:
            for app in section['appendices']:
                app_num, app_title = app
                lines.append(f"   - **{app_num}:** {app_title}")
        
        # Appendices under subsections
        if section['subsections']:
            # Sort subsections by their enumeration (usually letters)
            for sub_enum in sorted(section['subsections'].keys()):
                subsec = section['subsections'][sub_enum]
                lines.append(f"   - **{sub_enum}. {subsec['title']}**")
                for app in subsec['appendices']:
                    app_num, app_title = app
                    lines.append(f"      - **{app_num}:** {app_title}")
        lines.append("")  # Ensure a blank line between sections
    return "\n".join(lines)

def main():
    if len(sys.argv) < 2:
        print("Usage: python generate_toc.py <csv_file>")
        sys.exit(1)
        
    filename = sys.argv[1]
    sections = parse_csv_to_toc(filename)
    markdown_toc = generate_markdown_toc(sections)
    print(markdown_toc)

if __name__ == "__main__":
    main()