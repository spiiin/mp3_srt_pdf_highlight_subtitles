from pydub import AudioSegment

def trim_mp3(input_file, output_file, start_time, end_time):
    try:
        audio = AudioSegment.from_file(input_file, format="mp3")
        trimmed_audio = audio[start_time:end_time]
        trimmed_audio.export(output_file, format="mp3")
        print(f"Файл успешно сохранён: {output_file}")
    except Exception as e:
        print(f"Произошла ошибка: {e}")

#todo cmd line args
input_mp3 = "input.mp3"
output_mp3 = "output.mp3"
start = 17000
end = 37*60000 + 57000

trim_mp3(input_mp3, output_mp3, start, end)