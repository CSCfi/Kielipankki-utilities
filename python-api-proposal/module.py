# kielipankki 
# kielipankki/tools 
# kielipankki/corpora 
# kielipankki/corpora/suomi24 

class suomi24(corpus):
    self.texts = Texts() 

class Texts: 
    pass

class Sentence: 
    self.tokens = Tokens() 

class Token: 
    # is a lazy representation with access to token fields, only fetched when used
    pass
