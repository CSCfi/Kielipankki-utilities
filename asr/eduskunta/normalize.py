# -*- coding: utf-8 -*-
import os
import re
from datehandler import *

# input: PARTICIPANT kohta eaf-tiedostosta
# output: tuple of (TIER_ID,PARTICIPANT)

def normalize(i):

    # if unknown, don't touch it
    if i == 'UNKNOWN':
        return ('UNKNOWN', 'UNKNOWN')

    # poista 'koputtaa'
    i = i.replace('koputtaa', '')

    tyyppi = ''
    rooli = ''
    nimi = ''
    puolue = ''

    # valitse puheenvuoron tyypit ja poista ne
    vp = re.search(r"([vV]astauspu-?heen-?vuo-?r+o)", i)
    if vp:
        i = i.replace(vp.group(1), '')
        tyyppi = 'VP:'

    rp = re.search(r"([rR]yh-?mä-?pu-?heen-?vuo-?ro)", i) 
    if rp:
        i = i.replace(rp.group(1), '')
        tyyppi = 'RP:'

    ep = re.search(r"([eE]si-?tte-?ly-?pu-?heen-?vuo-?ro)", i)
    if ep:
        i = i.replace(ep.group(1), '')
        tyyppi = 'EP:'

    # valitse ministeri-sanat ja poista ne
    m = re.search(r"(([A-Z][a-z]+- ja [a-zäö]+ministeri)|([A-Z][a-z]+ [a-z]+asiamies)|([a-zä]+ [a-z]+edustaja)|([A-Z][a-zäö]+ministeri))", i)
    if m:
        i = i.replace(m.group(1), '')
        rooli = "({})".format(m.group(1))

    # valitse puolue ja poista
    p = re.search(r"(\/[a-z]+)", i)
    if p:
        i = i.replace(p.group(1), '')
        puolue = p.group(1)

    # valitse puhemies ja poista
    pm = re.search(r"((([Ee]nsimmäinen\s)|[Tt]oinen\s)?[A-Za-z][a-zöä]+hemies)", i)
    if pm:
        i = i.replace(pm.group(1), '')
        rooli = "({})".format(pm.group(1))


    # valitse nimi ja kasaaa oikean muotoon
    n = re.search(r"([A-ZÄÖÅ][a-zäöåé]+(\-?[A-XÄÖÅ]?[a-zäöåé]+)?(\s[A-ZÄÖÅ]\.)?)\s+([A-ZÄÖÅ][a-zäöåé]+(\-?[A-XÄÖÅ]?[a-zäöåé]+))", i)
    if n:
        kokonimi = "{} {}".format(n.group(1), n.group(4))
        muoto = "{}{}{}{}".format(tyyppi,kokonimi,rooli,puolue)
        return (muoto, kokonimi)
    
    # Mitä jos ei löydy etunimeä + sukunimeä?
    i = re.sub(r"\s", "", i) # poista välilyönnit
    muoto = "{}{}{}{}".format(tyyppi,i,rooli,puolue)

    return (muoto, i) # palauta kokonimen sijaan se mitä jäljellä


# rename the files year-month-day.[metadata, eaf, mp4]
# normalizes the PARTICIPANTs and TIER_IDs in the eaf files
def normalizefiles():

    # for all metadata files
    for file in os.listdir("."):
        if file.endswith(".metadata"):

            currentfile = os.path.join(".", file)

            # read the file
            with open(currentfile, "r") as f:
                metafile = f.readlines()

                # get information from the metafile
                for line in metafile:
                    if "Transcript" in line:
                        transcriptlink = line.split()[1]
                    elif "Video" in line:
                        videolink = line.split()[1]
                        muutettudate = getdate(line)

            # extract the old video name from the url
            oldvidname = videolink[videolink.rfind("/")+1:]

            # the name of the old eaf is the same as the metadata without .metadata
            oldeafname = currentfile.replace("metadata","eaf")

            # the new names of the files
            videoname = "{}.mp4".format(muutettudate)
            eafname = "{}.eaf".format(muutettudate)
            metaname = "{}.metadata".format(muutettudate)

            # rename the files
            try:
                os.rename(oldvidname, videoname)
            except OSError as e:
                #print("rename {}: {}".format(oldvidname, e))
                pass
            try:
                os.rename(oldeafname, eafname)
            except OSError as e:
                print("rename {}: {}".format(oldeafname, e))
            try:
                os.rename(currentfile, metaname)
            except OSError as e:
                print("rename {}: {}".format(currentfile, e))

            # normalisoi välilyönnit eaf tiedostoissa
            with open(eafname, "r") as f:
                eaffile = f.read()
                eaffile = re.sub('\xc2\xa0', ' ', eaffile)
            with open(eafname, "w") as f:
                f.write(eaffile)

            # read all participants from the eaf file
            with open(eafname, "r") as f:
                eaflines = f.readlines()

            # muuta tier_id ja participant kohdat
            index = 0
            for line in eaflines:
                if "PARTICIPANT" in line:
                    # split the line a bit so its easier to regex
                    linesplit = line.split("PARTICIPANT=")[1]
                    
                    # choose participant and tier_id with regex
                    kohdat = re.search(r'^\"([^\"]*)\"(?:[^\"]*)\"([^\"]*)\"', linesplit)
                    if not kohdat:
                        print("Couldn't extract parts from [{}]".format(linesplit))
                        exit(0)
                    participant = kohdat.group(1)
                    tierid = kohdat.group(2)

                    # normalize the participant
                    # (0) is the tier id
                    # (1) is the participant
                    normalizedpair = normalize(participant)
                    
                    # replace the old participant with new one
                    if participant in eaflines[index] and tierid in eaflines[index]:
                        eaflines[index] = eaflines[index].replace(participant, normalizedpair[1], 1)
                        eaflines[index] = eaflines[index].replace(tierid, normalizedpair[0], 1)
                    else:
                        print("[{}] or [{}] not found in [{}}".format(tierid, participant, eaflines[index]))
                        exit(0)
                index = index + 1 # increment index

            # write the fixed eaf lines to file
            with open(eafname, "w") as f:
                f.write("".join(eaflines))


