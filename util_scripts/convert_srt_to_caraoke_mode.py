import re
from nltk.tokenize import sent_tokenize

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
    srt_file_path = 'lotr_12.srt.fixed'
    text_file_path = 'lotr_12_aligned.txt'
    output_srt_path = 'lotr_12_karaoke.srt'

    srt_data = read_srt_file(srt_file_path)
    sentences = read_text_file(text_file_path)

    create_new_srt(srt_data, sentences, output_srt_path)
    print(f"Новый SRT файл создан: {output_srt_path}")


if __name__ == "__main__":
    main()
