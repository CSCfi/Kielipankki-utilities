import re

#Naïve language recognizer for E-thesis

keywords = {'fi': ['ja', 'mutta', 'sekä', 'ei', 'on', 'ollut',
                   'oli', 'että', 'myös', 'tutkielma'],
            'en': ['the', 'a', 'an', 'of', 'in', 'on',
                   'from', 'at', 'not', 'was', 'were', 'thesis'],
            'sv': ['är', 'det', 'och', 'en', 'ett',
                   'från', 'i', 'att', 'var'],
            'de': ['der', 'die', 'das', 'ist', 'für', 'war', 'sind'],
            'es': ['el', 'la', 'de', 'es', 'por', 'que', 'con'],
            'ru': ['и', 'в', 'не', 'тот', 'с', 'это', 'но'],
            'fr': ['et', 'pour', 'ce', 'par', 'ne' 'pas', 'du', 'de'],
            'it': ['di', 'il', 'per', 'del', 'al', 'della', 'con', 'su']}

def recognize(text):
    counts = {l: 0 for l in keywords.keys()}
    text = re.sub('[\.,\?!\(\):;\"]', '', text)
    tokens = text.split(' ')
    for token in tokens:
        for lang in keywords.keys():
            if token.lower() in keywords[lang]:
                counts[lang] += 1

    language = max(counts, key=counts.get)
    return language


