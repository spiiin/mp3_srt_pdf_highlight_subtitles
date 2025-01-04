from bs4 import BeautifulSoup

# Load the original HTML file
with open('lotr_2_2.html', 'r', encoding='utf-8') as file:
    html_content = file.read()

# Parse the HTML using BeautifulSoup
soup = BeautifulSoup(html_content, 'html.parser')

# Read the audio filenames from 1.txt
with open('1.txt', 'r', encoding='utf-8') as file:
    file_paths = file.readlines()

# Clean the paths from unnecessary whitespace or newline characters
file_paths = [path.strip() for path in file_paths]

# Get all the paragraph rows
dt_rows = soup.find_all('div', class_='dt-row')

# Iterate through the rows and add the audio players to the paragraphs
audio_no = 0
for i, row in enumerate(dt_rows):
    # Check if there are enough audio files to match the rows
        # Find the two language columns (English and Russian)
        cells = row.find_all('div', class_='par')
        if len(cells) == 2:
            if audio_no < len(file_paths):
                audio_link = file_paths[audio_no]
                audio_no+=1
                # Create the HTML for the audio player
                audio_html = f'<br><audio controls><source src="file:///{audio_link}" type="audio/mp3">Your browser does not support the audio element.</audio>'
                # Add the audio player to both the English and Russian columns
                cells[0].append(BeautifulSoup(audio_html, 'html.parser'))

# Save the modified HTML content to a new file
with open('lotr_2_2_audio.html', 'w', encoding='utf-8') as output_file:
    output_file.write(str(soup))

print("Updated HTML file saved as lotr_2_2_audio.html")
