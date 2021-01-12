import xml.etree.ElementTree as ET
from sys import stderr

def get_namespaces(xml_file):
    ns = dict([ x[1] for x in ET.iterparse(xml_file, events=['start-ns']) ])
    return ns

def get_val(tag, element, ns={}, i=0):
    try:
        retval = element.findall('.//'+tag, ns)[i].text
        if retval is None:
            return ''
        return retval
    except IndexError:
        if tag != 'MODS:partName':
            stderr.write('WARNING: element "%s" not found in METS file!\n' % (tag))
        return ''

def get_mets(filename):

    ns = get_namespaces(filename)
    element = ET.parse(filename).getroot()

    mets = {
        'label'       : " ".join(element.get('LABEL').split()),
        'issue_title' : " ".join(get_val('MODS:title', element, ns, 1).split()),
        'issue_date'  : " ".join(get_val('MODS:dateIssued', element, ns).split()),
        'issue_no'    : " ".join(get_val('MODS:partNumber', element, ns).split()),
        'part_name'   : " ".join(get_val('MODS:partName', element, ns).split()),
        'publ_title'  : " ".join(get_val('MODS:title', element, ns).split()),
        'publ_id'     : " ".join(get_val('MODS:identifier', element, ns).split()),
        'language'    : " ".join(get_val('MODS:languageTerm', element, ns).split()),
        'elec_date'   : " ".join(get_val('MODS:dateCreated', element, ns).split()),
        }

    return mets
