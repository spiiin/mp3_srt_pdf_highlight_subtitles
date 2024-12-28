import os
src_dir = r'c:\src\mp3_srt_pdf_highlight_subtitles\util_scripts\LOTR_2\CROPPED_MP3'
files = [f for f in os.listdir(src_dir) if f.endswith('.mp3')]
for file in files:
    full_path = os.path.join(src_dir, file).replace('\\', '/')
    file_name = os.path.splitext(file)[0] 
    print(f'=HYPERLINK("{full_path}"; "{file_name}")')
