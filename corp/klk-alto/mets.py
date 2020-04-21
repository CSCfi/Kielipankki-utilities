import xml.etree.ElementTree as ET
from sys import stderr

def get_namespaces(xml_file):
    ns = dict([ x[1] for x in ET.iterparse(xml_file, events=['start-ns']) ])
    return ns

def get_val(tag, element, ns={}, i=0):
    try:
        return element.findall('.//'+tag, ns)[i].text
    except IndexError:
        stderr.write('WARNING: element "%s" not found in METS file!\n' % (tag))
        return ''

def get_mets(filename):

    ns = get_namespaces(filename)
    element = ET.parse(filename).getroot()

    mets = {
        'label'       : element.get('LABEL').replace('  ',' '),
        'issue_title' : get_val('MODS:title', element, ns, 1),
        'issue_date'  : get_val('MODS:dateIssued', element, ns),
        'issue_no'    : get_val('MODS:partNumber', element, ns),
        'part_name'   : get_val('MODS:partName', element, ns),
        'publ_title'  : get_val('MODS:identifier', element, ns),
        'publ_id'     : get_val('MODS:identifier', element, ns),
        'language'    : get_val('MODS:languageTerm', element, ns),
        'elec_date'   : get_val('MODS:dateCreated', element, ns),
        }

    return mets
