import spacy, argparse

LANG_MODELS = {
    'en': 'en_core_web_sm',
    'ru': 'ru_core_news_sm'
}

def split_sentences_spacy(nlp, text):
    doc = nlp(text)
    sentences = [sent.text.strip() for sent in doc.sents]
    return sentences

def main():
    parser = argparse.ArgumentParser(description="Split text into sentences using spaCy.")
    parser.add_argument('lang_code', type=str, choices=LANG_MODELS.keys(), help="Language code ('en' or 'ru').")
    parser.add_argument('input_file', type=str, help="Path to the input text file.")
    parser.add_argument('output_file', type=str, help="Path to the output text file.")
    args = parser.parse_args()

    lang_code = args.lang_code
    model_name = LANG_MODELS[lang_code]
    nlp = spacy.load(model_name)

    with open(args.input_file, 'r', encoding='utf-8') as file:
        text = file.read()

    sentences = split_sentences_spacy(nlp, text)

    if lang_code == 'ru':
        sentences = [s for s in sentences if s.strip("–-") != ""]

    with open(args.output_file, 'w', encoding='utf-8') as f:
        for sentence in sentences:
            f.write(sentence + '\n')

if __name__ == "__main__":
    main()
