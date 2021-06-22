#!/usr/bin/python
# -*- coding: utf-8 -*-

import errno
import os
import urllib.request
import sys

""" ============================================================
Oracc JSON downloader                     asahala 2021-06-14
                                          github.com/asahala
  
How to use:

   od = OraccDownloader(subcorpora, output_directory)
   od.download()

Project file format:

   One sub-corpus per line. Use # in the beginning of the line
   to exclude it from the list, e.g.
   
   cams/barutu
   cams/gkab
   #cdli
   ...

============================================================ """

class OraccDownloader:

    """
    :param   projects       file containing names of projects
                            to be downloaded, or a list of
                            project names.
    :param   zip_folder     where to save zipped JSONs

    :type    projects       str or list
    :type    zip_folder     str

    """

    def __init__(self, projects=, zip_folder):
        if type(projects) == list:
            self.projects = projects
        else:
            self.projects = self.parse_projects(projects)
        self.base_url = "http://oracc.org/json/{}.zip"
        self.folder = zip_folder
        
    def _makedir(self):
        """ Create directory for zip files """
        try:
            os.mkdir(f'../{self.folder}')
        except FileExistsError:
            pass
        
    def parse_projects(self, filename):
        """ Parse projects from source file """
        with open(filename, 'r', encoding='utf-8') as f:
            for p in f.read().splitlines():
                if not p.startswith('#') and p:
                    yield p.replace('/', '-')

    def download(self):
        """ Download files from Oracc """
        self._makedir()
        
        for p in self.projects:
            out_file = self.folder + f'/{p}.zip'
            url = self.base_url.format(p)
            print('> {:<20s} -> {:<0s}'.format(p, out_file))
            try:
                with urllib.request.urlopen(url) as f:
                    file = f.read()
                    with open(out_file, 'wb') as f:
                        f.write(file)
            except urllib.error.HTTPError:
                print('> Warning: Unable to download {p}')
                continue

#od = OraccDownloader('../projectlist/projects.txt', '../jsonzip')
#od.download()
