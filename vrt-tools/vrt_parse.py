import sys
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
    # characters, spaces or equals signs
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
               attribs[attrib_name] = tag[start:i]
               state = parse_state.outside_name
           elif c == '\\':
               next_sym_is_escaped = True
    return (name, attribs)

def parse_file(fobj):
    firstline = fobj.readline().strip()
    if not _is_comment(firstline) or ':' not in firstline:
        raise Exception(
            "Couldn't find positional argument comment in first line")
    positional_args_start = firstline.index(':') + 1
    positional_args_stop = firstline.rindex('-->')
    positional_args = firstline[positional_args_start:positional_args_stop].strip().split()
    xml_stack = [['', {}, []]] # this will contain triples of name, attribs and tokens
    
    for line in fobj:
        line = line.strip()
        if _is_comment(line) or line == '':
            # Handle new positional arg lines?
            continue
        elif _is_opening_tag(line):
            name, attribs = _get_tag_name_and_attribs(line)
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
                assert "tokens" not in attribs
                attribs["tokens"] = tokens
            _second(_last(xml_stack)).setdefault(_make_plural(name), []).append(attribs)
        else:
            # Should be a token, are there self-closing tags in vrt?
            try:
                _third(_last(xml_stack)).append(
                    {positional_args[i]: col for i, col in enumerate(line.split('\t'))})
            except Exception as ex:
                raise Exception("Couldn't parse presumed token line: {}\n  Exception was: {}".format(line, str(ex)))
    assert len(xml_stack) == 1
    return _second(_first(xml_stack))

if __name__ == '__main__':
    import json
    print(json.dumps(parse_file(open(sys.argv[1]))))
