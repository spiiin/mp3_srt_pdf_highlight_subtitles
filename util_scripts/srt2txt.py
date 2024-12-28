import argparse

def extract_text_from_srt(srt_file_path, output_text_file_path):
    with open(srt_file_path, 'r', encoding='utf-8') as srt_file:
        lines = srt_file.readlines()

    text_lines = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.isdigit():
            i += 1

            while i < len(lines) and lines[i].strip() == '':
                i += 1
            if i < len(lines) and '-->' in lines[i]:
                i += 1

            subtitle_text = ''
            while i < len(lines) and lines[i].strip() != '':
                subtitle_text += lines[i]
                i += 1
            if subtitle_text:
                text_lines.append(subtitle_text.strip())
        else:
            i += 1

    with open(output_text_file_path, 'w', encoding='utf-8') as text_file:
        for line in text_lines:
            text_file.write(line + '\n')

def replace_text_in_srt(srt_file_path, input_text_file_path, output_srt_file_path):
    with open(srt_file_path, 'r', encoding='utf-8') as srt_file:
        srt_lines = srt_file.readlines()

    with open(input_text_file_path, 'r', encoding='utf-8') as text_file:
        text_lines = text_file.readlines()
        text_lines = [line.strip() for line in text_lines]

    new_srt_lines = []
    i = 0
    text_line_index = 0

    while i < len(srt_lines):
        line = srt_lines[i]
        stripped_line = line.strip()
        new_srt_lines.append(line)
        i += 1

        if stripped_line.isdigit():
            while i < len(srt_lines) and srt_lines[i].strip() == '':
                new_srt_lines.append(srt_lines[i])
                i += 1
            if i < len(srt_lines) and '-->' in srt_lines[i]:
                new_srt_lines.append(srt_lines[i])
                i += 1
            subtitle_text = ''
            while i < len(srt_lines) and srt_lines[i].strip() != '':
                if text_line_index < len(text_lines):
                    new_srt_lines.append(text_lines[text_line_index] + '\n')
                    text_line_index += 1
                else:
                    new_srt_lines.append('\n')
                i += 1
            if i < len(srt_lines):
                new_srt_lines.append('\n')

    with open(output_srt_file_path, 'w', encoding='utf-8') as output_file:
        output_file.writelines(new_srt_lines)

def create_srt_from_text(text_file_path, output_srt_file_path):
    with open(text_file_path, 'r', encoding='utf-8') as text_file:
        lines = text_file.readlines()

    with open(output_srt_file_path, 'w', encoding='utf-8') as srt_file:
        for i, line in enumerate(lines):
            srt_file.write(f"{i + 1}\n")
            srt_file.write("00:00:00,000 --> 00:00:00,000\n")
            srt_file.write(f"{line.strip()}\n\n")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Инструмент для извлечения, замены и создания файлов .srt.')
    subparsers = parser.add_subparsers(dest='command', help='Доступные команды')

    parser_extract = subparsers.add_parser('extract', help='Извлечь текст из файла .srt')
    parser_extract.add_argument('srt_file', help='Путь к входному файлу .srt')
    parser_extract.add_argument('text_file', help='Путь к выходному текстовому файлу')

    parser_replace = subparsers.add_parser('replace', help='Заменить текст в файле .srt')
    parser_replace.add_argument('srt_file', help='Путь к входному файлу .srt')
    parser_replace.add_argument('text_file', help='Путь к текстовому файлу с новым текстом')
    parser_replace.add_argument('output_srt_file', help='Путь к выходному файлу .srt')

    parser_create = subparsers.add_parser('create', help='Создать srt файл из текстового файла')
    parser_create.add_argument('text_file', help='Путь к текстовому файлу')
    parser_create.add_argument('output_srt_file', help='Путь к выходному файлу .srt')

    args = parser.parse_args()

    if args.command == 'extract':
        extract_text_from_srt(args.srt_file, args.text_file)
        print(f'Текст успешно извлечен из {args.srt_file} в {args.text_file}')
    elif args.command == 'replace':
        replace_text_in_srt(args.srt_file, args.text_file, args.output_srt_file)
        print(f'Текст в {args.srt_file} успешно заменен текстом из {args.text_file}. Результат сохранен в {args.output_srt_file}')
    elif args.command == 'create':
        create_srt_from_text(args.text_file, args.output_srt_file)
        print(f'SRT файл успешно создан из {args.text_file} и сохранен в {args.output_srt_file}')
    else:
        parser.print_help()

#python srt2txt.py extract input.srt output.txt
#python srt2txt.py replace input.srt new_text.txt output.srt
#python srt2txt.py create input.txt output.srt