from bs4 import BeautifulSoup
import pandas as pd
import re

# Load and parse the HTML file
with open('lotr_2_2.html', 'r', encoding='utf-8') as file:
    soup = BeautifulSoup(file, 'html.parser')

# Find all the rows of the text
rows = soup.find_all('div', class_='dt-row')

# Lists to hold English and Russian text
english_text = []
russian_text = []

# Extract English and Russian sentences
for row in rows:
    cells = row.find_all('div', class_='dt-cell')
    if len(cells) == 2:
        english = cells[0].get_text(strip=True)
        russian = cells[1].get_text(strip=True)
    english = re.sub(r'^\d+\s*', '', english)
    russian = re.sub(r'^\d+\s*', '', russian)
    english_text.append(english)
    russian_text.append(russian)

# Create a DataFrame
data = {'English': english_text, 'Russian': russian_text}
df = pd.DataFrame(data)

# Save to Excel file
output_file = 'lotr_2_2.xlsx'
df.to_excel(output_file, index=False)

print(f'Excel file has been saved to {output_file}')