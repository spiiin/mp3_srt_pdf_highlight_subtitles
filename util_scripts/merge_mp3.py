from pydub import AudioSegment

def merge_mp3(input_file1, input_file2, output_file):
    try:
        audio1 = AudioSegment.from_file(input_file1, format="mp3")
        audio2 = AudioSegment.from_file(input_file2, format="mp3")
        combined_audio = audio1 + audio2
        combined_audio.export(output_file, format="mp3")
        print(f"Склеенный файл сохранён: {output_file}")
    except Exception as e:
        print(f"Произошла ошибка при склеивании: {e}")
        
file1 = "11.mp3"
file2 = "12.mp3"
merged_output = "merged.mp3"
merge_mp3(file1, file2, merged_output)
