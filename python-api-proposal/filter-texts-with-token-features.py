from kielipankki.corpora import suomi24
import lda

model = lda.Lda(categories = 10)

def text_has_political_org(text):
    def word_has_poltical_org(word):
        return word.NER == '<EnamexOrgPlt>'
    return text.word_match(word_has_political_org)

documents = suomi24.filter_texts(text_has_political_org)
model.train(documents.get_running_texts())
