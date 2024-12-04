def read_srt_text_lines(file_path):
    lines = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            stripped_line = line.strip()
            # Игнорируем пустые строки, номера и строки с таймингами
            if stripped_line and not stripped_line.isdigit() and "-->" not in stripped_line:
                lines.append(stripped_line)
    return lines


def read_file_content(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()
        return text.replace('\n', '').lower()


def find_unmatched_lines(srt_lines, text_content):
    unmatched = []
    for srt_line in srt_lines:
        if srt_line.lower() not in text_content:  # Проверяем подстроками
            unmatched.append(srt_line)
    return unmatched

def main():
    srt_file_path = 'lotr_12.srt'
    text_file_path = 'lotr_12_aligned.txt'

    srt_lines = read_srt_text_lines(srt_file_path)
    text_lines = read_file_content(text_file_path)

    unmatched_lines = find_unmatched_lines(srt_lines, text_lines)

    if unmatched_lines:
        print("Несовпадающие строки:")
        for line in unmatched_lines:
            print(line)
    else:
        print("Все строки найдены в тексте.")


if __name__ == "__main__":
    main()