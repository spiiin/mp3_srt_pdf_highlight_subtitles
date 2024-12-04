def correct_file_encoding(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()
    
    try:
        # Корректируем текст с неправильной кодировкой
        corrected_content = content.encode('cp1252', errors='replace').decode('utf-8', errors='replace')
    except UnicodeEncodeError as e:
        print(f"Ошибка перекодировки: {e}")
        return
    
    # Сохраняем результат в новый файл
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(corrected_content)
    
    print(f"Файл успешно преобразован и сохранен как {output_file}")

input_file = "lotr_12.srt"
output_file = "lotr_12.srt"

correct_file_encoding(input_file, output_file)
