# Giving arbitrary Python functions to run over the entire database is
# inevitably slow. These requests should be possible to make fast

from kielipankki.corpora import suomi24

results = suomi24.get_texts_by_any_word([word1, word2, word3])
results = suomi24.get_sentences_by_NER('<NERTag>')
results = suomi24.get_texts_by_time(time_interval)

results = suomi24.get_sentences_by_NER('<NERTag>').get_texts_by_time(time_interval)
