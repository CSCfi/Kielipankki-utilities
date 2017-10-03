# -*- coding: utf-8 -*-
import re

pvmt = []

# takes the line with video name as argument
# returns unique date in format year-month-day[_runningnumber]
#
# selvittää videon päivämäärän.
# jos useammassa sama päivämäärä, laittaa juoksevan numeron toiseen. Kumpaan, riippuu kumman lukee ensin. Ajan mukaan sorttaaminen inte värt
#
# input: link to the original video 
# output: recording date of the video in format year-month-day[-running_number]
def getdate(line):
    sline = line.strip()
    
    if 'ncode' in line:
        if 'sessio' in sline:
            # vidin nimestä
            vidname = line.split('/')[6]
            search = re.search(r"_(\d\d)_(\d\d)_(\d\d\d\d)",vidname)
            year = search.group(3)
            month = search.group(2)
            day = search.group(1)
            date = "{}-{}-{}".format(year,month,day)


        elif 'upload' in sline:
            # pubdate
            date = line.split('/')[5]
            search = re.search(r"(\d\d\d\d)-(\d\d)-(\d\d)",date)
            year = search.group(1)
            month = search.group(2)
            day = search.group(3)
            date = "{}-{}-{}".format(year,month,day)
        else:
            print("Unknown type! {}".format(sline))
            exit()

    else:
        vidname = sline[sline.rfind("/")+1:]
        
        # nappaa pvm[]kuukausi[]vuosi
        vidname = re.search(r"_(?:[^_]*)_(.*\d\d\d\d)(?:.*\.mp4)",vidname)

        # nappaa päivä, kuukausi, vuosi
        vidname = re.search(r"(\d+)(?:[\._]+)([^\._]+)(?:[\._]+)(\d\d\d\d)", vidname.group(1))

        day = vidname.group(1)
        month = vidname.group(2)
        year = vidname.group(3)

        # muuta sana numeroksi
        month = re.sub(r"tammikuuta", "01", month)
        month = re.sub(r"helmikuuta", "02", month) 
        month = re.sub(r"maalisk[u]+ta", "03", month)
        month = re.sub(r"huhtikuuta", "04", month)
        month = re.sub(r"toukokuuta", "05", month)
        month = re.sub(r"kes.kuuta", "06", month)
        month = re.sub(r"hein.kuuta", "07", month)
        month = re.sub(r"elokuuta", "08", month)
        month = re.sub(r"syyskuuta", "09", month)
        month = re.sub(r"lokakuuta", "10", month)
        month = re.sub(r"marraskuuta", "11", month)
        month = re.sub(r"joulukuuta", "12", month)

        if len(day) == 1:
            day = "0{}".format(day)

        date = "{}-{}-{}".format(year,month,day)

    # lisää juokseva numero jos pvm löytyy jo
    olddate = date
    nro = 0
    while date in pvmt:
        date = "{}-{}".format(olddate,nro)
        nro = nro+1

    pvmt.append(date) # append the date to the list
    
    return date
