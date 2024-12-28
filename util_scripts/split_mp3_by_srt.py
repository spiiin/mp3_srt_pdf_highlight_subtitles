from datetime import datetime, timedelta
import re
from pydub import AudioSegment

def time_to_ms(time_str):
    try:
        parts = time_str.split(':')
        if len(parts) == 2:
            m, s_ms = parts
            h = 0
        else:
            h, m, s_ms = parts
        
        s, ms = s_ms.split(',') if ',' in s_ms else (s_ms, '000')
        return (int(h) * 3600 + int(m) * 60 + int(s)) * 1000 + int(ms)
    except ValueError:
        print(f"Ошибка при разборе времени: {time_str}")
        return 0


def ms_to_time(ms):
    td = timedelta(milliseconds=ms)
    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    return f"{hours:02}{minutes:02}{seconds:02}"

def parse_srt(file):
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read().strip()
        blocks = content.split('\n\n')
        subtitles = []
        
        for block in blocks:
            lines = block.split('\n')
            if len(lines) < 3:
                continue
            index = lines[0]
            timing = lines[1]
            start, end = timing.split(' --> ')
            start_ms, end_ms = time_to_ms(start), time_to_ms(end)
            text = ' '.join(lines[2:])
            try:
                subtitles.append({
                    'index': int(index),
                    'start': start_ms,
                    'end': end_ms,
                    'text': text
                })
            except ValueError:
                print(f"Ошибка при обработке блока: {block}")
    return subtitles

def extract_audio_segments(audio_file, subtitles):
    audio = AudioSegment.from_mp3(audio_file)
    
    for i, s in enumerate(subtitles):
        start_ms = s['start']
        end_ms = s['end']
        segment = audio[start_ms:end_ms]
        filename = f"CROPPED_MP3/lotr2_1_{i+1:03}_{ms_to_time(start_ms)}-{ms_to_time(end_ms)}.mp3"
        segment.export(filename, format="mp3")
        print(f"Вырезан фрагмент: {filename}")

srt_file = 'lotr2_1_eng_lines.srt'
audio_file = 'lotr2_1_eng.mp3'

subtitles = parse_srt(srt_file)
extract_audio_segments(audio_file, subtitles)

print("Аудио фрагменты успешно сохранены.")
