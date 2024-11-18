import re

def process_russian_text(input_file_path, output_file_path):
    with open(input_file_path, 'r', encoding='utf-8') as file:
        text = file.read()

    text = text.replace('\n', ' ').replace('\r', ' ')
    text = re.sub(r'\s+', ' ', text).strip()

    sentence_endings = re.compile(r'([.!?…;:]+)\s+')
    sentences = sentence_endings.split(text)

    processed_sentences = []
    for i in range(0, len(sentences)-1, 2):
        sentence = sentences[i] + sentences[i+1]
        processed_sentences.append(sentence.strip())

    if len(sentences) % 2 != 0:
        processed_sentences.append(sentences[-1].strip())

    with open(output_file_path, 'w', encoding='utf-8') as output_file:
        for sentence in processed_sentences:
            if sentence:
                output_file.write(sentence + '\n')

if __name__ == '__main__':
    #todo: cmd-line arguments
    input_file = 'text.txt'
    output_file = 'text_proccessed.txt'

    process_russian_text(input_file, output_file)
    print(f'Текст успешно обработан и сохранен в {output_file}')