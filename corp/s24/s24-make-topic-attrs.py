#! /usr/bin/env python3


import csv
import re
import sys

# libpaths adds local library paths to sys.path (korpimport)
import libpaths

from korpimport import scriptutil


class TopicAttributeMaker(scriptutil.ArgumentRunner):

    DESCRIPTION = """
    Output a TSV file mapping a comma-separated list of Suomi24 topic
    numbers to text attributes containing the corresponding
    information in a human-readable form.
    """

    ARGSPECS = [
        ('topic_mapping_file',
         'TSV file mapping single topic numbers to topic names (titles)'),
        ('full_topics_file',
         'a file listing comma-separated lists of topics numbers (topics and'
         ' their ancestors)'),
    ]

    def __init__(self):
        super().__init__()

    def main(self):
        topic_map = {}
        full_topics = []
        bool_map = {'0': 'false', '1': 'true'}

        def read_topic_map():
            with open(self._args.topic_mapping_file, 'r') as tmf:
                reader = csv.DictReader(tmf, delimiter='\t')
                for row in reader:
                    topic_map[row['topic_id']] = row

        def make_topic_attrs(topics):
            topic_list = list(reversed(topics.split(',')))
            topic_names = [topic_map[topic]['name'] for topic in topic_list]
            attrs = [
                'topic_name_leaf="{}"'.format(topic_names[-1]),
                'topic_name_top="{}"'.format(topic_names[0]),
                'topic_names="{}"'.format(' &gt; '.join(topic_names)),
                'topic_names_set="|{}|"'.format('|'.join(topic_names)),
                'topics_set="|{}|"'.format('|'.join(topic_list)),
                'topic_adultonly="{}"'.format(
                    bool_map[topic_map[topic_list[-1]]['adultonly']]),
            ]
            return ' '.join(attrs)

        read_topic_map()
        with open(self._args.full_topics_file, 'r') as inf:
            for line in inf:
                topics = line.strip()
                if topics:
                    sys.stdout.write(
                        topics + '\t' + make_topic_attrs(topics) + '\n')


if __name__ == '__main__':
    TopicAttributeMaker().run()
