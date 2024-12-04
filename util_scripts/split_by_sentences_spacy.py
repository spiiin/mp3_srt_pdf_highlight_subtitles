import spacy

INPUT_EN = 'lotr_12_unaligned.txt'
OUTPUT_EN = 'lotr_12_aligned.txt'
INPUT_RU = 'lotr_12_rus_unaligned.txt'
OUTPUT_RU = 'lotr_12_rus_aligned.txt'

nlp_en = spacy.load("en_core_web_sm")
nlp_ru = spacy.load("ru_core_news_sm")

def split_sentences_spacy(nlp, text):
    doc = nlp(text)
    sentences = [sent.text.strip() for sent in doc.sents]
    return sentences

with open(INPUT_EN, 'r', encoding='utf-8') as file:
    text = file.read()

sentences1 = split_sentences_spacy(nlp_en, text)
with open(OUTPUT_EN, 'w', encoding='utf-8') as f:
    for s in sentences1:
        f.write(s + '\n')
        
with open(INPUT_RU, 'r', encoding='utf-8') as file:
    text2 = file.read()

sentences2= split_sentences_spacy(nlp_ru, text2)
sentences2 = list([s for s in sentences2 if s.strip("–-")!=""]) #SpaCy treats it as separate sentences for the Russian language

with open(OUTPUT_RU, 'w', encoding='utf-8') as f:
    for s in sentences2:
        f.write(s + '\n')