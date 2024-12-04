import re

def fix_srt_file(file_path):
    """
    Исправляет в srt-файле:
    1. ".буква" заменяет на ". буква".
    2. Если строка начинается с '’', переносит этот символ в конец предыдущей фразы.
    
    :param file_path: Путь к .srt файлу.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    
    fixed_lines = []
    previous_phrase_index = -1
    
    for i, line in enumerate(lines):
        stripped_line = line.strip()
        
        if stripped_line.startswith('’') and previous_phrase_index > 0:
            fixed_lines[previous_phrase_index-1] = fixed_lines[previous_phrase_index-1].strip() + "’\n"
            stripped_line = stripped_line[1:].strip()
        
        if not stripped_line.isdigit() and '-->' not in stripped_line:
            stripped_line = re.sub(r'(?<=\.)\b([a-zA-Z])', r' \1', stripped_line)
            previous_phrase_index = len(fixed_lines)
        fixed_lines.append(stripped_line + '\n')
    
    with open(file_path+".fixed", 'w+', encoding='utf-8') as file:
        file.writelines(fixed_lines)

fix_srt_file("lotr_12.srt")