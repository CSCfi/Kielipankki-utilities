#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# What it does?
# - normalizes .eaf and .mp4 filenames into year-month-day.ending format
# - normalizes the PARTICIPANTS in the eaf files
#
# What it expects?
# - the script expects to be in same directory with .metadata, .eaf and .mp4 files
#
# the links to transcripts or videos are currently not added to the imdi files
# this is because arbil cannot import them then
#
# 
#



import os
import re
import shutil
import sys
sys.dont_write_bytecode = True

from normalize import *
from templates import *
from datehandler import *


if __name__ == "__main__":

    # First do some preliminary work...
    normalizefiles()

    corplinks = []

    # create the root dir
    if not os.path.exists("Eduskunta"):
        os.mkdir("Eduskunta")
    else:
        print("Directory Eduskunta already exists!")
        exit(0)

    # list of tuples (year, month, day, transcriptlink, mp4)
    sessions = []

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

            # valitse teidoston nimi ilman päätettä
            filename = re.search(r"([^/]+).metadata", currentfile).group(1)

            # append session to the sessions
            # (year, month, day, transcript, mp4, filename)
            search = re.search(r"(\d\d\d\d)-(\d\d)-(\d\d)", filename)
            year = search.group(1)
            month = search.group(2)
            day = search.group(3)

            onesession = (year, month, day, transcriptlink, videolink, filename)
            sessions.append(onesession)

    # dictionary with keys 'year-season', value is list of sessions in that moment
    sessionDict = {}

    # create dictionary sessionDict['2010-kevat'] -> [], sessionDict['2010-syksy'] -> []
    for session in sessions:
        year = session[0]
        month = session[1]

        # init the lists if they dont exist yet
        if not sessionDict.get("{}-kevat".format(year)):
            sessionDict["{}-kevat".format(year)] = []
        if not sessionDict.get("{}-syksy".format(year)):
            sessionDict["{}-syksy".format(year)] = []

        # split the sessions into spring and fall
        if int(month) <= 6:
            sessionDict["{}-kevat".format(year)].append(session) # kevät
        else:
            sessionDict["{}-syksy".format(year)].append(session) # syksy

    # Debug info
    k = 0
    for year in range(2008, 2017):
        print("{}: kevat {} syksy {}".format(year, len(sessionDict.get("{}-kevat".format(year))), len(sessionDict.get("{}-syksy".format(year)))))
        k = k + len(sessionDict.get("{}-kevat".format(year))) + len(sessionDict.get("{}-syksy".format(year)))
    print("total sessions: {}".format(k))


    # for each year 2008-2016
    for year in range(2008, 2017):

        # for both seasons
        for season in ["kevat", "syksy"]:

            # if there are sessions in this season
            if len(sessionDict.get("{}-{}".format(year, season))) > 0:

                # append every new node to list of corpuslinks
                corplinks.append('<CorpusLink Name="">CORPUSLINK-PH</CorpusLink>'.replace("CORPUSLINK-PH","{}-{}/{}-{}.imdi".format(year,season,year,season)))

                # create directory structure
                os.mkdir("Eduskunta/{}-{}".format(year,season))
                os.mkdir("Eduskunta/{}-{}/Media".format(year,season))
                os.mkdir("Eduskunta/{}-{}/Annotations".format(year, season))
                os.mkdir("Eduskunta/{}-{}/Metadata".format(year, season))

                with open("Eduskunta/{}-{}/{}-{}.imdi".format(year, season, year, season), "w") as f:

                    # create list of all sessions in this year and season
                    sessionlinks = []
                    # for every session in this year and season
                    for session in sessionDict.get("{}-{}".format(year, season)):
                        transcriptlink = session[3].replace('&', '&amp;') # link to transcript
                        videolink = session[4].replace('&', '&amp;') # link to original video
                        basefname = session[5] # base of the filename
                        month = session[1] # extract month from date
                        day = session[2] # extract the day from the line
                        sessionlinks.append('<CorpusLink Name="">CORPUSLINK-PH</CorpusLink>'.replace("CORPUSLINK-PH","Metadata/{}.imdi".format(basefname)))

                        # kirjota sessiot levylle (Metadata/{sessio})
                        # and replace the placeholders
                        with open("Eduskunta/{}-{}/Metadata/{}.imdi".format(year,season, basefname), "w") as sessionfile:
                            sessionfile.write(sessionnode\
                                    .replace('NAME-PH', '{}'.format(basefname))\
                                    .replace('DATE-PH', '{}-{}-{}'.format(year, month, day))\
                                    .replace('VIDEO-PH', '../Media/{}.mp4'.format(basefname))\
                                    .replace('ANNOTATION-PH', '../Annotations/{}.eaf'.format(basefname)))
                                    #.replace('DESCRIPTION-PH', 'Istunnon pöytäkirja i<![CDATA[{}]]>, Alkuperäinen video <![CDATA[{}]]>'.format(transcriptlink, videolink)))
                                    # ^ otettu pois, koska arbil ei pysty käsittelemään linkkejä syystä x

                        # siirrä video ja eaf oikeille paikoille (Media/{sessio.mp4} och Annotations/{sessio.eaf})
                        try:
                            shutil.move("{}.eaf".format(basefname), "Eduskunta/{}-{}/Annotations/{}.eaf".format(year,season, basefname)) # (source, destination)
                        except IOError, e:
                            print("Error moving file: {}".format(e))
                        try:
                            shutil.move("{}.mp4".format(basefname), "Eduskunta/{}-{}/Media/{}.mp4".format(year,season, basefname)) # (source, destination)
                        except IOError, e:
                            print("Error moving file: {}".format(e))

                    # replace the placeholders and add the sessionlinks
                    f.write(node.replace('<!--<CorpusLink Name=""></CorpusLink>-->',"\n".join(sessionlinks))\
                            .replace('NAME-PH', '{}-{}'.format(year,season)))


    # create the imdi file into root directory with links to all other nodes
    with open("Eduskunta/Eduskunta.imdi", "w") as f:
        f.write(node.replace('<!--<CorpusLink Name=""></CorpusLink>-->',"\n".join(corplinks))\
                .replace('NAME-PH', 'Eduskunta'))




