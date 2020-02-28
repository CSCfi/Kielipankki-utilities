import sqlite3

_db_path = 'ylilauta.db'
_db_connection = sqlite3.connect('file:{}?immutable=1'.format(_db_path), uri = True)
_first = lambda x: x[0]

class Text:

    def __init__(self, rowid):
        self.rowid = rowid

    def get_paragraphs(self, in_order = False):
        c = _db_connection.cursor()
        if not in_order:
            c.execute('''
            SELECT rowid FROM paragraphs
            WHERE parent = ?''', (self.rowid,))
        else:
            c.execute('''
            SELECT rowid FROM paragraphs
            WHERE parent = ? ORDER BY id ASC''', (self.rowid,))
        return map(Paragraph, map(_first, c))

    def token_match(self, fun):
        for paragraph in self.get_paragraphs():
            for sentence in paragraph.get_sentences():
                for token in sentence.get_tokens():
                    if fun(token):
                        return True
        return False

    def get_text(self):
        paragraphs = []
        for paragraph in self.get_paragraphs(in_order = True):
            para_text = []
            for sentence in paragraph.get_sentences(in_order = True):
                sentence_text = []
                for token in sentence.get_tokens(in_order = True):
                    sentence_text.append(token.get_surface())
                para_text.append(' '.join(sentence_text))
            paragraphs.append(' '.join(para_text))
        return '\n'.join(paragraphs)

class Paragraph:

    def __init__(self, rowid):
        self.rowid = rowid

    def get_sentences(self, in_order = False):
        c = _db_connection.cursor()
        if not in_order:
            c.execute('''
            SELECT rowid FROM sentences
            WHERE parent = ?''', (self.rowid,))
        else:
            c.execute('''
            SELECT rowid FROM sentences
            WHERE parent = ? ORDER BY id ASC''', (self.rowid,))
        return map(Sentence, map(_first, c))

class Sentence:

    def __init__(self, rowid):
        self.rowid = rowid

    def get_tokens(self, in_order = False):
        c = _db_connection.cursor()
        if not in_order:
            c.execute('''
            SELECT rowid FROM tokens
            WHERE parent = ?''', (self.rowid,))
        else:
            c.execute('''
            SELECT rowid FROM tokens
            WHERE parent = ? ORDER BY id ASC''', (self.rowid,))
        return map(Token, map(_first, c))

class Token:

    def __init__(self, rowid):
        self.rowid = rowid

    def get_surface(self):
        c = _db_connection.cursor()
        c.execute('''
        SELECT string FROM strings
        JOIN tokens ON tokens.surface = strings.rowid
        WHERE tokens.rowid = ?''', (self.rowid,))
        return _first(c.fetchone())

    def get_NER(self):
        c = _db_connection.cursor()
        c.execute('''
        SELECT ner FROM tokens
        WHERE tokens.rowid = ?''', (self.rowid,))
        return _first(c.fetchone())

def get_texts(token_condition = None):
    if token_condition is None:
        return map(Text(map(_first,
                            _db_connection.cursor().execute('SELECT rowid FROM texts'))))
    field, value = token_condition
    sql_query = '''
    SELECT DISTINCT texts.rowid FROM texts
    JOIN paragraphs ON paragraphs.parent = texts.rowid
    JOIN sentences ON sentences.parent = paragraphs.rowid
    JOIN tokens ON tokens.parent = sentences.rowid
    WHERE tokens.{} = "{}"'''.format(field, value)
    return map(Text, map(_first, _db_connection.cursor().execute(sql_query)))
