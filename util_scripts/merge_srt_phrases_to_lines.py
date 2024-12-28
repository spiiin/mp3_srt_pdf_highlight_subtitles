from datetime import datetime, timedelta
import re

def time_to_ms(time_str):
    h, m, s_ms = time_str.split(':')
    s, ms = s_ms.split(',')
    return (int(h) * 3600 + int(m) * 60 + int(s)) * 1000 + int(ms)


def ms_to_time(ms):
    td = timedelta(milliseconds=ms)
    time_str = str(td)
    if "." in time_str:
        time_str = time_str.replace('.', ',')[:-3]
    return time_str


def parse_srt(file):
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read().strip()
        blocks = content.split('\n\n')
        subtitles = []
        
        for block in blocks:
            lines = block.split('\n')
            index = lines[0]
            timing = lines[1]
            text = ' '.join(lines[2:])
            start, end = timing.split(' --> ')
            subtitles.append({
                'index': int(index),
                'start': time_to_ms(start),
                'end': time_to_ms(end),
                'text': text
            })
    return subtitles

def clean_text(text):
    return re.sub(r'[^a-zA-Z]', '', text).lower()

def find_longest_match(line, subtitles):
    best_match = []
    current_match = []
    clean_line = clean_text(line)
    
    for s in subtitles:
        clean_sub = clean_text(s['text'])
        if clean_sub in clean_line:
                if s["text"].strip() != "":
                    #if not current_match or s['start'] == current_match[-1]['end']:
                    current_match.append(s)
        else:
            if len(current_match) > len(best_match):
                best_match = current_match[:]
            current_match = []
    if len( current_match) > len(best_match):
        best_match = current_match
    return best_match


def merge_subtitles(lines_file, subtitles):
    with open(lines_file, 'r', encoding='utf-8') as f:
        lines = f.read().splitlines()

    merged_subtitles = []
    subtitle_index = 1

    for line in lines:
        matching_subs = find_longest_match(line, subtitles)
        if matching_subs:
            start_time = matching_subs[0]['start']
            end_time = matching_subs[-1]['end']
            #print(line, len(matching_subs), start_time, end_time)
            merged_subtitles.append({
                'index': subtitle_index,
                'start': start_time,
                'end': end_time,
                'text': line
            })
        else:
            merged_subtitles.append({
                'index': subtitle_index,
                'start': 0,
                'end': 0,
                'text': " "
            })
        subtitle_index += 1
    return merged_subtitles


def write_srt(output_file, subtitles):
    with open(output_file, 'w', encoding='utf-8') as f:
        for s in subtitles:
            f.write(f"{s['index']}\n")
            f.write(f"{ms_to_time(s['start'])} --> {ms_to_time(s['end'])}\n")
            f.write(f"{s['text']}\n\n")

srt_file = 'lotr2_1_eng.srt'
lines_file = 'lotr2_1_eng_aligned.txt'
output_file = 'lotr2_1_eng_lines.srt'

subtitles = parse_srt(srt_file)
merged_subtitles = merge_subtitles(lines_file, subtitles)
write_srt(output_file, merged_subtitles)

print("done")
