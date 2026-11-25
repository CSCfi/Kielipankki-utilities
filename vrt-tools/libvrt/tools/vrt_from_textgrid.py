import re
from pathlib import Path
import html
from libvrt.args import transput_args

class Interval:
    interval_number: int
    text: str
    xmin: float
    xmax: float

    def __init__(self, interval_number: int, text: str, xmin: float, xmax: float):
        self.interval_number = interval_number
        self.text = text
        self.xmin = xmin
        self.xmax = xmax

def parsearguments(argv, *, prog = None):
    description = '''

    Translates TextGrid to vrt.

    '''

    parser = transput_args(description = description,
                           inplace = False)

    parser.add_argument('--pause', metavar = 'SECONDS',
                        default = '1.0',
                        help = '''

                        length of the pause separating sentences in seconds as a float, 
                        1.0 by default.

                        ''')
    
    parser.add_argument('--length', metavar = '',
                        default = '70',
                        help = '''

                        maximum length of a sentence, 70 tokens by default

                        ''')
    
    args = parser.parse_args()
    args.prog = prog or parser.prog
    return args

def main(args, ins, ous):
    text = ins.read()
    pause_length = float(args.pause)
    sentence_max_len = int(args.length)
    intervals = get_interval_segments(text)
    sentences = get_sentences(intervals, pause_length)
    # limiting the length of sentences to 70 by default
    while any(len(sentence) >= sentence_max_len for sentence in sentences):
        if pause_length < 0.01: break
        pause_length = pause_length * 0.9
        sentences = get_sentences(intervals, pause_length)

    print_vrt(sentences, ous, args)

def get_sentences(intervals: list[Interval], pause_length: float) -> list[list[Interval]]:
    sentences = []
    sentence = []

    for interval in intervals:
        is_first = interval.interval_number == 1
        is_last = interval.interval_number == len(intervals)
        is_empty = interval.text.strip() == ''

        if is_empty:
            if not is_first and not is_last and interval.xmax - interval.xmin >= pause_length:
                if sentence:
                    sentences.append(sentence)
                    sentence = []

        else:
            sentence.append(interval)

    if sentence:
        sentences.append(sentence)
        
    return sentences

def print_vrt(sentences: list[list[Interval]], ous, args):
    print("<!-- #vrt positional-attributes: word xmin xmax -->", file=ous)
    if args.infile is None:
        filename = ""
    else:
        filename = Path(args.infile).name

    print(f'<text filename="{filename}">', file=ous)
    for sentence in sentences:
        print_sentence(sentence, ous)

    print("</text>", file=ous)

def print_sentence(sentence: list[Interval], ous):
    print(f'<sentence xmin="{sentence[0].xmin}" xmax="{sentence[-1].xmax}">', file=ous)
    for interval in sentence:
        print(f"{interval.text}\t{interval.xmin}\t{interval.xmax}", file=ous)
    print("</sentence>", file=ous)

def get_interval_segments(file_content: str) -> list[Interval]:
    # Matches intervals [n]: and 3 subsequent rows 
    interval_pattern = re.compile(
        r"(intervals \[\d+\]:)\n(.*)\n(.*)\n(.*)",
        re.MULTILINE
    )
    interval_matches = re.findall(interval_pattern, file_content)
    intervals = []
    for match in interval_matches:
        interval = make_interval(match)
        intervals.append(interval)

    return intervals

def make_interval(match: list[str]) -> Interval:
    interval_number = get_interval_number(match[0])
    xmin = get_xmin(match[1])
    xmax = get_xmax(match[2])
    text = get_text(match[3])

    text_processed = process_text(text)

    interval = Interval(interval_number=interval_number, text=text_processed, xmin=xmin, xmax=xmax)
    return interval

def process_text(text: str) -> str:
    processed_text1 = html.unescape(text)
    processed_text2 = processed_text1.replace("&", "&amp;")
    processed_text3 = processed_text2.replace("<", "&lt;")
    processed_text4 = processed_text3.replace(">", "&gt;")
    processed_text5 = processed_text4.strip()
    processed_text6 = " ".join(processed_text5.split())
    # removes soft hyphens
    processed_text7 = processed_text6.replace("\u00AD", "")
    return processed_text7

def get_xmax(text: str) -> float:
    pattern = r"xmax = (\d+\.\d+)"
    match = re.search(pattern, text)
    if match:
        return float(match.group(1))
    raise ValueError("xmax not found")

def get_xmin(text: str) -> float:
    pattern = r"xmin = (\d+\.\d+)"
    match = re.search(pattern, text)
    if match:
        return float(match.group(1))
    raise ValueError("xmin not found")

def get_text(text: str) -> str:
    pattern = r"text = \"(.*?)\""
    match = re.search(pattern, text)
    if match:
        return match.group(1)
    raise ValueError("text not found")

def get_interval_number(interval_number: str) -> int:
    pattern = r"intervals \[(\d+)\]"
    match = re.search(pattern, interval_number)
    if match:
        return int(match.group(1))
    raise ValueError("intervals not found")

def get_interval_size(file_content: str) -> int:
    pattern = r"intervals: size = (\d+)"
    match = re.search(pattern, file_content)
    if match:
        return match.group(1)
    raise ValueError("interval size not found")

def load_file(filepath: str) -> str:
    with open(filepath, "r") as file:
        return file.read()