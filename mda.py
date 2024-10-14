import os
import re


def clean_text(text):
    text = re.sub(r'<[^>]*>', ' ', text)
    return text


def extract_mda_sections(text):
    mda_start_pattern = r'discussion and analysis of financial condition '
    mda_end_patterns = [
        r'quantitative and qualitative disclosures about market risk',
        r'controls and procedures'
    ]

    mda_sections = []
    current_position = 0

    while True:
        # Find the start of the MD&A section
        start_match = re.search(mda_start_pattern, text[current_position:], re.IGNORECASE)
        if not start_match:
            break

        start_index = start_match.start() + current_position
        current_position += start_match.end()

        # Find the end of the MD&A section
        end_match = None
        for pattern in mda_end_patterns:
            end_match = re.search(pattern, text[current_position:], re.IGNORECASE)
            if end_match:
                break

        if end_match:
            end_index = end_match.start() + current_position
            if (end_index - start_index) >= 100:
                mda_section = text[start_index:end_index].strip()
                mda_sections.append(mda_section)

        # Move current position beyond the end match
        current_position = end_index + len(end_match.group()) if end_match else current_position

    return mda_sections


# Process all files in the downloads directory
downloads_dir = './downloads'
cleaned_dir = './cleaned'
os.makedirs(cleaned_dir, exist_ok=True)

for filename in os.listdir(downloads_dir):
    if filename.endswith('.txt'):
        file_path = os.path.join(downloads_dir, filename)

        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            text_content = f.read()

        # Clean text by removing content within <>
        cleaned_content = clean_text(text_content)

        # Extract MDA sections
        mda_sections = extract_mda_sections(cleaned_content)

        # Save results to a new file
        output_file_path = os.path.join(cleaned_dir, filename)
        with open(output_file_path, 'w', encoding='utf-8') as f_out:
            if mda_sections:
                f_out.write("\n\n".join(mda_sections))
            else:
                f_out.write("")  # Save an empty file if no sections found

        print(f"Processed file: '{filename}' - MDA sections extracted: {len(mda_sections)}")

print("All files processed.")
