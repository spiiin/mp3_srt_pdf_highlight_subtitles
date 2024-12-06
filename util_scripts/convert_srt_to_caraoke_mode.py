import re
import sys
import io
import argparse
from nltk.tokenize import sent_tokenize

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

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


def read_text_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()
    return sent_tokenize(text)


def find_matching_sentence(phrase, sentences):
    for sentence in sentences:
        if phrase in sentence:
            highlighted_sentence = re.sub(
                re.escape(phrase), f"<b>{phrase}</b>", sentence, flags=re.IGNORECASE
            )
            return highlighted_sentence
    return None


def create_new_srt(srt_data, sentences, output_file):
    with open(output_file, 'w', encoding='utf-8') as file:
        for index, timing, phrase in srt_data:
            matching_sentence = find_matching_sentence(phrase, sentences)
            if matching_sentence:
                file.write(f"{index}\n{timing}\n{matching_sentence.strip()}\n\n")
            else:
                print(f"Phrase not found: {phrase}")
                file.write(f"{index}\n{timing}\n{phrase}\n\n")


def main():
    parser = argparse.ArgumentParser(description="Create a new SRT file with highlighted text.")
    parser.add_argument(
        "srt_file", 
        type=str, 
        help="Path to the input SRT file."
    )
    parser.add_argument(
        "text_file", 
        type=str, 
        help="Path to the input text file for matching sentences."
    )
    parser.add_argument(
        "output_srt", 
        type=str, 
        help="Path to the output SRT file."
    )

    args = parser.parse_args()

    srt_data = read_srt_file(args.srt_file)
    sentences = read_text_file(args.text_file)

    create_new_srt(srt_data, sentences, args.output_srt)
    print(f"Output file created: {args.output_srt}")


if __name__ == "__main__":
    main()
