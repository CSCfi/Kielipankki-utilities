import ylilauta

def text_has_political_org(text):

    def word_has_political_org(word):
        return word.get_NER() == '<EnamexOrgPlt>'

    return text.token_match(word_has_political_org)

#documents = filter(text_has_political_org, ylilauta.get_texts())
documents = ylilauta.get_texts(token_condition = ("NER", "<EnamexOrgPlt>"))
for document in documents:
    print(document.get_text())
