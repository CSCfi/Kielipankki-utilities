import sqlite3
import enum
import sys

from xml.sax.saxutils import unescape

import enum
def _is_comment(s): return s.startswith('<!--') and s.endswith('-->')

def _is_opening_tag(s):
    return s.startswith('<') and (not s.startswith('</')) and s.endswith('>')

def _is_closing_tag(s):
    return s.startswith('</') and s.endswith('>')

def _make_plural(s): return s + 's'

def _first(l): return l[0]
def _second(l): return l[1]
def _third(l): return l[2]
def _last(l): return l[-1]

def _get_tag_name_and_attribs(tag):
    # We assume that the tag name and attribute names don't have escaped
    # characters, spaces or equals signs. We do parse escaping etc. in the values.
    class parse_state(enum.Enum):
        outside_name, inside_name, outside_value, inside_value = range(4)
    if not _is_opening_tag(tag):
        raise Exception("Failed to read XML tag from {}".format(tag))
    tag = tag[1:-1] # strip <>
    if ' ' not in tag:
        return (tag.strip(), {}) # Just a tag name
    name = tag[:tag.index(" ")]
    tag = tag[tag.index(" ") + 1:] # remove name part, the rest is an attrib list
    attribs = {}
    next_sym_is_escaped = False
    state = parse_state(parse_state.outside_name)
    for i, c in enumerate(tag):
        if state == parse_state.outside_name:
            if c != ' ':
                state = parse_state.inside_name
                start = i
        elif state == parse_state.inside_name:
            if c == '=':
                attrib_name = tag[start:i]
                state = parse_state.outside_value
        elif state == parse_state.outside_value:
            if c == '"':
                start = i + 1
                state = parse_state.inside_value
        else:
           if next_sym_is_escaped:
               next_sym_is_escaped = False
           elif c == '"':
               attribs[attrib_name] = unescape(tag[start:i])
               state = parse_state.outside_name
           elif c == '\\':
               next_sym_is_escaped = True
    return (name, attribs)

def parse_file(fobj, n_texts = None):
    text_count = 0
    xml_stack = [['', {}, []]] # this will contain triples of name, attribs and tokens
    
    for line in fobj:
        line = line.rstrip('\n')
        if _is_comment(line) or line == '':
            # Handle new positional arg lines?
            continue
        elif _is_opening_tag(line):
            name, attribs = _get_tag_name_and_attribs(line)
            _id = int(attribs["id"])
            if name == "text":
                title = attribs["title"]
                # datefrom = attribs["datefrom"]
                # dateto = attribs["dateto"]
                date = attribs["date"]
                clock = attribs["clock"]
                sec = attribs["sec"]
                date_parts = date.split('.')
                year = date_parts[2]
                month = int(date_parts[1])
                day = int(date_parts[0])
                timestring = "{}-{:02}-{:02}T{}".format(year, month, day, clock)
                db_cursor.execute('INSERT INTO texts VALUES (?, strftime("%s", "{}"), ?, ?)'.format(timestring),
                                  (title, _id, sec))
                # db_cursor.execute('INSERT INTO texts VALUES (?, ?, ?, ?, ?, strftime("%s", "{}"), ?, ?)'.format(timestring),
                #                   (title, datefrom, dateto, date, clock, _id, sec))
                parent = db_cursor.lastrowid
            elif name == "paragraph":
                db_cursor.execute("INSERT INTO paragraphs VALUES (?, last_insert_rowid())", (_id,))
            elif name == "sentence":
                db_cursor.execute("INSERT INTO sentences VALUES (?, last_insert_rowid())", (_id,))
            else:
                assert(False)

            xml_stack.append([name, attribs, []])
        elif _is_closing_tag(line):
            name = line[2:-1].strip()
            if name != _first(_last(xml_stack)):
                # if there are out-of-order tags, we try to unwind to the most
                # recent match, and if that isn't present, we ignore the tag
                if name in map(_first, xml_stack):
                    collected_tokens = []
                    while name != _first(_last(xml_stack)):
                        collected_tokens = _third(xml_stack.pop()) + collected_tokens
                    # now we're at the matching position, put the tokens here
                    _last(xml_stack)[2] += collected_tokens
                else:
                    continue
            name, attribs, tokens = xml_stack.pop()

            if len(tokens) > 0:
                parent_of_tokens = db_cursor.lastrowid
                # positional_args = ["surface", "id", "lemma", "pos", "morpho", "head", "dep", "ner"]
                for token in tokens:
                    token[0] = stringstore(token[0])
                    token[2] = stringstore(token[2])
                    db_cursor.execute("INSERT INTO tokens VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                                      [parent_of_tokens] + token)
#                    parent_of_morphos = db_cursor.lastrowid
#                    db_cursor.executemany("INSERT INTO morpho VALUES (?, ?)", ((parent_of_morphos, m) for m in token[4].split("|")))
#            _second(_last(xml_stack)).setdefault(_make_plural(name), []).append(attribs)
            if name == 'text':
                text_count += 1
                if n_texts != None and text_count >= n_texts:
                    return
        else:
            # Should be a token, are there self-closing tags in vrt?
            try:
                token_parts = unescape(line).split('\t')
                for i in range(3, 8):
                    if token_parts[i] == '_':
                        token_parts[i] = ''
                _third(_last(xml_stack)).append(token_parts)
            except Exception as ex:
                raise Exception("Couldn't parse presumed token line: {}\n  Exception was: {}".format(line, str(ex)))
#    assert len(xml_stack) == 1

conn = sqlite3.connect('ylilauta.db')
db_cursor = conn.cursor()
db_cursor.execute('CREATE TABLE IF NOT EXISTS texts(title TEXT, time INTEGER, id INTEGER, sec TEXT)')
#db_cursor.execute('CREATE TABLE IF NOT EXISTS texts(title TEXT, datefrom TEXT, dateto TEXT, date TEXT, clock TEXT, time INTEGER, id INTEGER, sec TEXT)')
db_cursor.execute('CREATE TABLE IF NOT EXISTS paragraphs(parent INTEGER NOT NULL, id INTEGER, FOREIGN KEY(parent) REFERENCES texts(rowid) ON DELETE CASCADE)')
db_cursor.execute('CREATE TABLE IF NOT EXISTS sentences(parent INTEGER NOT NULL, id INTEGER, FOREIGN KEY(parent) REFERENCES paragraphs(rowid) ON DELETE CASCADE)')
db_cursor.execute('CREATE TABLE IF NOT EXISTS tokens(parent INTEGER NOT NULL, surface INTEGER, id INTEGER, lemma INTEGER, pos TEXT, morpho TEXT, head INTEGER, dep TEXT, ner TEXT, FOREIGN KEY(parent) REFERENCES sentences(rowid) ON DELETE CASCADE)')
db_cursor.execute('CREATE TABLE IF NOT EXISTS strings(string TEXT UNIQUE)')
db_cursor.execute('CREATE UNIQUE INDEX string_index ON strings(string)')
db_cursor.execute('CREATE INDEX paragraph_parent_index ON paragraphs(parent)')
db_cursor.execute('CREATE INDEX sentence_parent_index ON sentences(parent)')
db_cursor.execute('CREATE INDEX token_parent_index ON tokens(parent)')
#db_cursor.execute('CREATE TABLE IF NOT EXISTS morpho(parent INTEGER NOT NULL, value TEXT, FOREIGN KEY(parent) REFERENCES tokens(rowid) ON DELETE CASCADE)')

def stringstore(s):
    db_cursor.execute(
        'SELECT rowid FROM strings WHERE string = ?', (s,))
    # db_cursor.execute(
    #     'SELECT rowid FROM strings WHERE EXISTS(SELECT 1 FROM strings WHERE string = ?)', (s,))
    stringres = db_cursor.fetchone()
    if stringres is None:
        db_cursor.execute('INSERT INTO strings VALUES (?)', (s,))
        return db_cursor.lastrowid
    else:
        return _first(stringres)

filename = sys.argv[1]
n = None
if len(sys.argv) > 2:
    n = int(sys.argv[2])
parse_file(open(filename), n)
conn.commit()
