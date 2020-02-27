# Kielipankki Python API proposal

This directory is intended to contain non-runnable examples of scripts we would
like to be able to run through a Python API and sketches for the structure of
the API.

Current work is exploring per-corpus custom Python classes (which can inherit from shared baseclasses), each using a per-corpus SQL database. Current variations on the database (all are sqlite3 databases):

ylilauta: based on ylilauta_20150304.vrt, including all information, also computing a unix timestamp, no indices. One table per hierarchy level: texts, paragraphs, sentences, tokens, each having a unique parent in the table above.
_noredundant: omitting redundant fields, like startdate and enddate, just keeping unix timestamp.
_parindex: calculating an index for each parent field in each hierarchy level.
_stringstore: store strings (surfaces, lemmas, full morphology fields, ner fields) in an indexed string table
_textlemmaidx: as an experiment, precompute a table which indexes lemmas to texts, allowing for immediate access to texts which contain a particular lemma

Current variations on querying the database:
text.token_match: give a boolean Python function to be applied to iterators of (ultimately) tokens to see eg. which texts contain a particular field, or whatever you want to do with Python
text.has_lemma: construct a SQL query to find texts with a certain field faster. If we have eg. a _lextlemmaidx table, use that.
