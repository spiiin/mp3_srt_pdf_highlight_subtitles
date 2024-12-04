import re


def clean_text(text):
    """
    Очищает текст от нежелательных символов и тегов.
    """
    return re.sub(r'<[^>]+>', '', text).strip()


def read_srt_file(file_path):
    """
    Считывает содержимое SRT файла и разделяет его на блоки.
    """
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
    """
    Считывает файл с разделением табуляцией и возвращает список строк.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    aligned_data = []
    for line in lines:
        columns = line.split("\t")
        if len(columns) >= 2:  # Убедимся, что есть как минимум 2 колонки
            english_phrase = columns[0].strip()
            translated_phrase = columns[1].strip()
            aligned_data.append((english_phrase, translated_phrase))
    return aligned_data


def find_matching_translation(cleaned_phrase, aligned_data):
    """
    Находит перевод для очищенной фразы из aligned файла.
    """
    for english_phrase, translated_phrase in aligned_data:
        if cleaned_phrase in english_phrase:
            return translated_phrase
    return ""


def create_new_srt(srt_data, aligned_data, output_file):
    """
    Создаёт новый SRT файл с добавленными переводами.
    """
    with open(output_file, 'w', encoding='utf-8') as file:
        for index, timing, text in srt_data:
            cleaned_phrase = clean_text(text)
            translation = find_matching_translation(cleaned_phrase, aligned_data)
            if translation:
                # Добавляем перевод в новую строку
                output_text = translation
            else:
                output_text = ''
            file.write(f"{index}\n{timing}\n{output_text.strip()}\n\n")


def main():
    srt_file_path = 'lotr_12_karaoke.srt'
    aligned_file_path = 'aligned_lotr_12_aligned-lotr_12_rus_aligned.txt'
    output_srt_path = 'lotr_12_karaoke_translated.srt'

    # Считываем данные
    srt_data = read_srt_file(srt_file_path)
    aligned_data = read_aligned_file(aligned_file_path)

    # Создаём новый SRT файл с переводами
    create_new_srt(srt_data, aligned_data, output_srt_path)
    print(f"Новый SRT файл создан: {output_srt_path}")


if __name__ == "__main__":
    main()