#! /usr/bin/env python
# -*- coding: utf-8 -*-


""" """


import sys
import re

from cStringIO import StringIO

import pandas as pd
from pandas.core.indexing import IndexingError

# Package python-docx: https://python-docx.readthedocs.io/en/latest/
import docx
from docx.shared import Pt, Mm

import korpimport.util as korputil
import korpimport.xmlutil as xmlutil


class DictTable(list):

    def __init__(self):
        super(DictTable, self).__init__()

    def add_row(self, row=None):
        self.append(row or {})

    def add_cell(self, key, value):
        if not len(self):
            self.append({})
        if not isinstance(value, dict):
            value = {'value': value}
        self[-1][key] = value


class StatsMaker(korputil.InputProcessor):

    _localities = [
        ('North', [
            'Moray',
            #'Invernesshire',
            'Sutherland',
            'Ross',]),
        ('North-East', [
            'Aberdeenshire',
            'Angus',]),
        ('Central', [
            'Perthshire',
            'Lanarkshire',]),
        ('South-East', [
            'Fife',
            'Lothian',
            'Borders',
            'Stirlingshire',]),
        ('South-West', [
            'Ayrshire',
            'Argyllshire',
            'South-West',]),
        ('Professional', ['Professional']),
        ('Unlocalised', ['unlocalised']),
    ]
    _periods = [u'1540–1599', u'1600–1649', u'1650–1699', u'1700–1749']

    def __init__(self):
        super(StatsMaker, self).__init__()
        self._letter_info = None
        self._output_tables = []
        self._locality_order = [(loc, reg) for reg, locs in self._localities
                                for loc in locs]
        writer_class = getattr(
            self, 'OutputWriter' + self._opts.output_format.title())
        self._writer = writer_class(write_fn=self.output)

    def process_input_stream(self, stream, filename=None):
        self._read_wordcount_file(stream)
        self._generate_output()
        self._write_output()

    def _read_wordcount_file(self, stream):
        self._letter_info = pd.read_csv(
            stream, sep='\t', encoding=self._input_encoding, index_col='fn')
        self._letter_info = self._letter_info[
            ['period', 'gender', 'lcinf', 'largeregion', 'wc_new', 'from']]
        self._letter_info = self._letter_info.rename(columns={'wc_new': 'wc'})

    def _generate_output(self):
        for gender in ['male', 'female']:
            self._output_tables.append(self._make_by_locality(gender))

    def _make_by_locality(self, gender):

        def make_counts(df, group_cols):
            counts = {}
            groups = df.groupby(group_cols)
            counts['letters'] = groups.count()['wc']
            counts['tokens'] = groups['wc'].sum()
            # Hint for this from
            # http://stackoverflow.com/questions/17679089/pandas-dataframe-groupby-two-columns-and-get-counts
            counts['informants'] = (
                groups['from']
                .value_counts()
                .groupby(level=range(len(group_cols)))
                .count())
            return counts

        def get_counts(counts, key):
            # print key
            try:
                # for count_type in counts.iterkeys():
                #     print count_type, key, type(counts[count_type]), repr(counts[count_type].ix[key] if isinstance(key, basestring) else counts[count_type].ix[key[0]][key[1]]).decode('utf-8')
                return dict([(count_type, counts[count_type].ix[key])
                             for count_type in counts.iterkeys()])
            except (KeyError, IndexingError):
                # print "KeyError"
                return {}

        table = DictTable()
        letters = self._letter_info.query(
            'gender == "{gender}"'.format(gender=gender))
        counts = make_counts(letters, ['lcinf', 'period'])
        loc_counts = make_counts(letters, ['lcinf'])
        lr_counts = make_counts(letters, ['largeregion'])
        total_counts = make_counts(letters, ['period'])
        token_count_total_all = lr_counts['tokens'].sum()
        token_count_total_geodef = (
            letters.query('lcinf != "Professional" and lcinf != "unlocalised"')
            ['wc'].sum())
        prev_lr = None

        def add_larger_region_totals(table, region):
            table[-1]['Larger region']['bold'] = True
            table.add_cell('Larger region total', get_counts(lr_counts, region))
            table.add_cell(
                'Larger region total %',
                (lr_counts['tokens'][region] * 1.0
                 / token_count_total_all * 100.0))

        def add_totals(table):
            table.add_row()
            table.add_cell('Locality', 'Total')
            table.add_cell('Larger region', '')
            cnts = dict((key, loc_counts[key].sum())
                        for key in ['informants', 'letters', 'tokens'])
            table.add_cell('N Writers', cnts['informants'])
            table.add_cell('N Letters', cnts['letters'])
            table.add_cell('Total', cnts['tokens'])
            table.add_cell('Larger region total', cnts)
            table.add_cell('Larger region total %', 100.0)
            for period in self._periods:
                table.add_cell(period, get_counts(total_counts, period))
            table.add_row()
            table.add_cell('Locality', 'Total %')
            for period in self._periods:
                table.add_cell(period,
                               (get_counts(total_counts, period)['tokens'] * 1.0
                                / token_count_total_all * 100.0))
            table.add_cell('Larger region total %', 100.0)

        for locality, larger_region in self._locality_order:
            if not loc_counts['informants'].get(locality):
                continue
            if larger_region != prev_lr and prev_lr is not None:
                add_larger_region_totals(table, prev_lr)
            table.add_row()
            table.add_cell('Locality', locality)
            table.add_cell('Larger region', larger_region)
            # print repr(counts['informants']).decode('utf-8')
            table.add_cell('N Writers', loc_counts['informants'].ix[locality])
            table.add_cell('N Letters', loc_counts['letters'].ix[locality])
            token_cnt = loc_counts['tokens'].ix[locality]
            table.add_cell('Total', token_cnt)
            if locality not in ['unlocalised', 'Professional']:
                table.add_cell(
                    '% of geographically defined',
                    token_cnt * 1.0 / token_count_total_geodef * 100.0)
            for period in self._periods:
                table.add_cell(period, get_counts(counts, (locality, period)))
            prev_lr = larger_region
        add_larger_region_totals(table, prev_lr)
        add_totals(table)
        # print repr(table).decode('utf-8')
        formatted_table = self._format_table(
            table, (['Locality', 'N Writers'] + self._periods
                    + ['Total', 'N Letters', '% of geographically defined',
                       'Larger region', 'Larger region total',
                       'Larger region total %']),
            headings='bold')
        return {
            'table': formatted_table,
            'title': gender.title() + (u' informants in the Helsinki Corpus of'
                                       u' Scottish Correspondence 1540–1750'),
        }

    def _format_table(self, table, col_order, headings=None):
        formatted_table = []
        formatted_table.append([{'value': colhead} for colhead in col_order])
        for row in table:
            formatted_row = []
            for key in col_order:
                cell = row.get(key)
                if cell is None:
                    cell = {'value': ''}
                elif 'value' not in cell:
                    if cell.get('tokens'):
                        cell['value'] = (
                            u'{tokens}\n{informants} / {letters}'
                            .format(**dict((key, str(cell.get(key)))
                                           for key in ['tokens', 'informants',
                                                       'letters'])))
                    else:
                        cell['value'] = u'–'
                    cell['class'] = 'num'
                else:
                    value = cell.get('value')
                    cell['value'] = ('{0:.1f}'.format(value)
                                     if isinstance(value, float) 
                                     else str(value))
                    if isinstance(value, float) or isinstance(value, int):
                        cell['class'] = 'num'
                formatted_row.append(cell)
            formatted_table.append(formatted_row)
        # print repr(formatted_table)
        if headings != None:
            for col in formatted_table[0]:
                col[headings] = True
            for row in formatted_table:
                row[0][headings] = True
        return formatted_table

    def _write_output(self):
        self._writer.output(self._output_tables)
        # print self._output_tables

    class OutputWriter(object):

        _tags = {
            'none': ('', ''),
            'bold': ('<b>', '</b>'),
        }

        def __init__(self, write_fn=None):
            self._write_fn = write_fn or self._default_write_fn

        def _default_write_fn(self, text):
            sys.stdout.write(text)

        def output(self, tables_info):
            self._output_header()
            for table_info in tables_info:
                self._output_heading(table_info['title'], 2)
                self._output_table(table_info['table'])
            self._output_footer()

        def _output_header(self):
            self._write_fn(u'''<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8"/>
<style>
th {text-align: left; vertical-align: top;  max-width: 10em; padding: 0.5em;}
td {vertical-align: top; padding-right: 0.5em; padding-bottom: 0.25em;}
td.num {text-align: right;}
</style>
</head>
<body>
''')

        def _output_footer(self):
            self._write_fn(u'</body>\n</html>\n')

        def _output_heading(self, heading, level):
            self._write_fn(self._make_heading(heading, level))

        def _make_heading(self, data, level):
            tagname = u'h' + unicode(level)
            return xmlutil.make_elem(tagname, data) + '\n'

        def _output_table(self, table):
            self._write_fn(self._make_table(table))

        def _make_table(self, table):
            return xmlutil.make_elem('table', self._make_table_rows(table),
                                     newlines=True)

        def _make_table_rows(self, table):
            result = [
                (xmlutil.make_elem('tr', self._make_table_row(row, rownum))
                 + '\n') for rownum, row in enumerate(table)]
            return ''.join(result)

        def _make_table_row(self, row, rownum):
            result = [
                xmlutil.make_elem(
                    'th' if rownum == 0 or colnum == 0 else 'td',
                    self._make_table_cell(cell),
                    attrs=[('class', cell['class'])] if 'class' in cell else [])
                for colnum, cell in enumerate(row)]
            return ''.join(result)

        def _make_table_cell(self, cell):
            value = cell['value'].replace('\n', '<br/>')
            return (xmlutil.make_elem('strong', value) if cell.get('bold')
                    else value)

    class OutputWriterHtml(OutputWriter):

        pass

    class OutputWriterDocx(OutputWriter):

        def __init__(self, write_fn=None):

            def reset_font(style):
                font = style.font
                font.color.rgb = None
                font.name = 'Times New Roman'
                if font.size < Pt(12):
                    font.size = Pt(12)

            def move_space_after(style):
                parfmt = style.paragraph_format
                if parfmt.space_before > 0:
                    parfmt.space_after = parfmt.space_before
                    parfmt.space_before = 0

            self._write_fn = self._default_write_fn
            self._write_final_fn = write_fn or sys.stdout.write
            self._doc = docx.Document()
            styles = self._doc.styles
            for style_name in ['Heading 1', 'Heading 2', 'Heading 3', 'Normal']:
                reset_font(styles[style_name])
                move_space_after(styles[style_name])
            styles['Heading 1'].font.small_caps = True
            sect = self._doc.sections[0]
            sect.page_height = Mm(297)
            sect.page_width = Mm(210)
            sect.left_margin = sect.right_margin = sect.top_margin

        def _default_write_fn(self, text):
            import sys
            # sys.stderr.write(repr(text) + '\n')
            text = text.rstrip('\n')
            self._curr_para = self._doc.add_paragraph(text)

        def _output_heading(self, data, level):
            self._doc.add_heading(data, level)

        def output(self, output_data):
            super(StatsMaker.OutputWriterDocx, self).output(output_data)
            outf = StringIO()
            self._doc.save(outf)
            self._write_final_fn(outf.getvalue())
            
    def getopts(self, args=None):
        self.getopts_basic(
            dict(usage="%prog [options] [input] > output",
                 description=(
""" """)
             ),
            args,
            ['output-format = FORMAT', dict(
                type='choice',
                choices=['html', 'docx'],
                default='html',
                help='output in FORMAT: text or docx (default: %default)')]
        )
        if self._opts.output_format == 'docx':
            self._output_encoding = None


if __name__ == "__main__":
    StatsMaker().run()
