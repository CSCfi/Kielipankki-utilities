import os
import sys

""" Generate definitions for Oracc2021 """

projects = set([x.replace('.vrt', '').split('-')[0] for x in os.listdir('../vrt/')])

descriptions = {'adsd': 'ADsD: Astronomical Diaries Digital',
                'ario': 'ARIo: Achaemenid Royal Inscriptions online',
                'blms': 'blms: Bilinguals in Late Mesopotamian Scholarship',
                'caspo': 'CASPo: Corpus of Akkadian Shuila-Prayers online',
                'cams': 'CAMS: Corpus of Ancient Mesopotamian Scholarship',
                'ctij': 'CTIJ: Cuneiform Texts Mentioning Israelites, Judeans, and Other Related Groups',
                'dcclt': 'DCCLT: Digital Corpus of Cuneiform Lexical Texts',
                'dccmt': 'DCCMT: Digital Corpus of Cuneiform Mathematical Texts',
                'ecut': 'eCUT: Electronic Corpus of Urartian Texts', 'etcsri':
                'ETCSRI: Electronic Text Corpus of Sumerian Royal Inscriptions',
                'hbtin': 'HBTIN: Hellenistic Babylonia: Texts, Iconography, Names',
                'obmc': 'OBMC: Old Babylonian Model Contracts',
                'riao': 'RIAo: Royal Inscriptions of Assyria online',
                'ribo': 'RIBo: Royal Inscriptions of Babylonia online',
                'rimanum': 'Rīm-Anum: The House of Prisoners',
                'rinap': 'RINAP: Royal Inscriptions of the Neo-Assyrian Period',
                'saao': 'SAAo: State Archives of Assyria Online',
                'aemw': 'AEMW: Akkadian in the Eastern Mediterranean World',
                'akklove': 'Akkadian Love Literature',
                'lacost': 'LaOCOST: Law and Order: Cuneiform Online Sustainable Tool',
                'ccpo': 'CCPo: Cuneiform Commentaries Project on Oracc',
                'obta': 'OBTA: Old Babylonian Tabular Accounts',
                'ckst': 'CKST: Corpus of Kassite Sumerian Texts',
                'cmawro': 'CMAwRo: Corpus of Mesopotamian Anti-witchcraft Rituals',
                'epsd2': 'EPSD2: Electronic Pennsylvania Sumerian Dictionary 2',
                'suhu': 'Suhu: The Inscriptions of Suhu online',
                'atae': 'ATAE: Archival Texts of the Assyrian Empire',
                'glass': 'Glass: Corpus of Glass Technological Texts',
                'btto': 'BTTo: Babylonian Topographical Texts Online',
                'dsst': 'DSSt: Datenbank sumerischer Streitliteratur'}


contents = str(['oracc2021_'+x for x in sorted(projects)]).replace("'", '"')

corporafolders = """
// corporafolders
settings.corporafolders.oracc2021 = {
    title: "Oracc",
    description: "Oracc – Open Richly Annotated Cuneiform Corpus, Korp Version, 2021-06",
    contents: %s,
    info: {
        metadata_urn: "urn:nbn:fi:lb-2019060601",
        urn: "urn:nbn:fi:lb-2019060602",
        licence: settings.licenceinfo.CC_BY_SA_30,
        iprholder: {
            name: "Open Richly Annotated Cuneiform Corpus Project",
            url: "http://oracc.museum.upenn.edu/doc/about/licensing/index.html",
        },
        cite_id: "oracc-korp-2019-05",
        infopage_url: "https://www.kielipankki.fi/corpora/oracc/",
    }
};""" % contents

if projects != descriptions.keys():
    print(projects - descriptions.keys())
    sys.exit('Above projects not defined')

end = '''\tcontext : settings.spContext,
\twithin : settings.spWithin,
\tattributes: attrlist.oracc2021,
\tstruct_attributes : sattrlist.oracc2021
};'''
            
for p in sorted(projects):
    print('settings.corpora.oracc2021_%s = {' % p)
    print('\tid : "oracc2021_%s",' % p)
    print('\ttitle : "%s",' % descriptions[p])#.split(':')[1].lstrip())
    print('\tdescription : "%s",' % descriptions[p])
    print(end)
    
print(corporafolders)

