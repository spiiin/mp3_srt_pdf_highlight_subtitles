import re
import sys
import io
import argparse

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def clean_text(text):
    return re.sub(r'<[^>]+>', '', text).strip()

def read_srt_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    blocks = content.strip().split("\n\n")
    srt_data = []
    for block in blocks:
        lines = block.split("\n")
        if len(lines) >= 3:
            index = lines[0]
            timing = lines[1]
            text = " ".join(lines[2:])
            srt_data.append((index, timing, text))
    return srt_data

def read_aligned_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    aligned_data = []
    for line in lines:
        columns = line.split("\t")
        if len(columns) >= 2:
            english_phrase = columns[0].strip()
            translated_phrase = columns[1].strip()
            aligned_data.append((english_phrase, translated_phrase))
    return aligned_data

def find_matching_translation(cleaned_phrase, aligned_data):
    if not cleaned_phrase.strip():
        return ""
    for english_phrase, translated_phrase in aligned_data:
        if not english_phrase.strip(): #TODO: every time...
            continue
        if (cleaned_phrase in english_phrase) or (english_phrase in cleaned_phrase):
            #print("AAA: ", english_phrase)
            #print("BBB: ", cleaned_phrase)
            return translated_phrase
    return ""

def create_new_srt(srt_data, aligned_data, output_file):
    with open(output_file, 'w', encoding='utf-8') as file:
        for index, timing, text in srt_data:
            cleaned_phrase = clean_text(text)
            translation = find_matching_translation(cleaned_phrase, aligned_data)
            if translation:
                output_text = translation
            else:
                print(f"Translation not found: {cleaned_phrase}")
                output_text = ''
            file.write(f"{index}\n{timing}\n{output_text.strip()}\n\n")

def main():
    parser = argparse.ArgumentParser(description="Add translations to an SRT file.")
    parser.add_argument("srt_file", type=str, help="Path to the input SRT file.")
    parser.add_argument("aligned_file", type=str, help="Path to the aligned text file.")
    parser.add_argument("output_file", type=str, help="Path to the output SRT file.")
    args = parser.parse_args()

    srt_data = read_srt_file(args.srt_file)
    aligned_data = read_aligned_file(args.aligned_file)
    create_new_srt(srt_data, aligned_data, args.output_file)
    print(f"New SRT file created: {args.output_file}")

if __name__ == "__main__":
    main()