import os
import re
from urllib2 import urlopen, URLError, HTTPError
from cgi import escape

class FetchPDFs:

    def __init__(self):
        self.pdflist = list()
        self.logs = list()

    def download_file(self):
        """ Download each PDF file found from source url """
        logfile = ''
        strippedname = re.sub(r'\W+', '', self.sourceurl)
        
        for entry in self.pdflist:
            logfile += entry['filename'].lstrip('/') + '\t' + entry['url'] + '\n'
            url = entry['url']
            try:
                f = urlopen(url)
                print("downloading " + url)

                """ Create subdir if it doesn't exist """
            # errors
            except HTTPError, e:
                print("HTTP Error:", e.code, url)
            except URLError, e:
                print("URL Error:", e.reason, url)
            finally:
                pass

              # open local file for writing
            with open(entry['filename'], "wb") as local_file:#os.path.join(os.path.basename(url))
                local_file.write(f.read())
                
        """ Write a log file that contains each filename """
        """ and their corresponding urls """
        with open(os.path.join('logfile.txt'), 'a') as log_file:
            log_file.write('\n'.join(self.logs))

    def format_line(self, l):
        l = l.strip()
        l = l.strip('\n')
        return l

    def parse_sublinks(self, html):
        
        def get_content(l):
            cont = re.sub('.*content="(.+?)".*', r'\1', line)
            lang = re.sub('.*xml:lang="(.+?)".*', r'\1', line)            
            return [cont, lang]
            
        meta_keys = ['citation_abstract_html_url',
                     'citation_title',
                     'citation_authors',
                     'citation_language',
                     'citation_date',
                     'citation_pdf_url',
                     'citation_keywords']

        name_keys = ['DC.contributor', 'DCTERMS.abstract']
        
        metadata = {}
        contributor = {}
        abstracts = []
        types = {}
        subject = {}
        
        for line in html:
            line = self.format_line(line)
            if line.startswith('<meta content'):
                for k in meta_keys:
                    if k in line:
                        metadata[k] = re.sub('.*content="(.+?)".*',
                                             r'\1', line)
            if 'DC.contributor' in line:
                x = get_content(line)
                contributor[x[1]] = x[0]
            if 'DCTERMS.abstract' in line:
                x = get_content(line)
                abstracts.append(x[0])
            if 'DC.type' in line and not "Text" in line:
                x = get_content(line)
                types[x[1]] = x[0]
            if 'DC.subject' in line:
                x = get_content(line)
                subject[x[1]] = x[0]

        #dummyt metadatalle jota ei olemassa
        for meta in meta_keys:
            if meta not in metadata.keys():
                metadata[meta] = ''

        d = [] #perusdata
        for k in metadata.keys():
            d.append(k.replace('_', '') + '="%s"' % escape(metadata[k]))

        #
        lang = metadata['citation_language']
        if lang in contributor.keys():
            d.append('faculty="%s"' %contributor[lang])
        else:
            d.append('faculty=""')

        if lang in subject.keys():
            d.append('subject="%s"' %subject[lang])
        else:
            d.append('subject=""')

        if lang in types.keys():
            d.append('type="%s"' %types[lang])
        else:
            d.append('type=""')


        year = re.sub('.*(\d\d\d\d).*', r'\1', metadata['citation_date'])
        d.append('datefrom="%s0101" dateto="%s1231"' % (year, year))
            
        pdfname = re.sub('.+\/(.+?)', r'%s_\1_%s' % (lang, metadata['citation_date']), metadata['citation_pdf_url'])

        absit = '@@@'.join(abstracts)

        if metadata['citation_title']:
            log = pdfname + '|||' + '<text ' + ' '.join(d) + '>' + '|||' + absit
            if metadata['citation_pdf_url']:
                self.pdflist.append({'url': metadata['citation_pdf_url'], 'filename': pdfname})
            self.logs.append(log)
        else:
            pass

        
    def get_sublinks(self, source, relative_url):
        """ Get all sub-urls from the E-Thesis source url """
        self.sourceurl = source
        sublinks = []
    
        if not relative_url:
            relative_url = re.sub('(http:\/\/.+?\/).*', r'\1', source)

        f = urlopen(source)
        for line in f:
            line = self.format_line(line)
            if re.match('<a href="\/handle\/\d+?\/\d+?">.*', line):
                sublink = re.sub('.*href="\/(handle\/\d+?\/\d+?)".*', r'\1', line)
                sublinks.append(relative_url + sublink)

        for sublink in sublinks:
            g = urlopen(sublink)
            self.parse_sublinks(g)
           
def main():
    relative_url = ''
    source_urls = []
    
    def read_urls(urlfile):
        u = open(urlfile, 'r')
        s = u.readlines()
        u.close()
        return s

    sourcet = read_urls("urlit.txt")
    
    for line in sourcet:
        if not line.startswith('#') or len(line) < 2:
            source_urls.append(line.strip('\n'))
        else:
            relative_url = re.sub('#', '', line.strip('\n'))

    for source_url in source_urls:
        f = FetchPDFs()
        f.get_sublinks(source_url, relative_url)
        f.download_file()

if __name__ == "__main__":
    main()
