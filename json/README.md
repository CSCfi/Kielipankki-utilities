# Converting VRT to JSON #

The VRT files are expected to have a special comment before any token
line that specifies names for the fields of each token line. Only
`text`, `paragraph`, and `sentence` levels of structure are observed,
and expected to be properly nested. All tokens are expected to be in a
`sentence`. (Strictly speaking, the converter is not known to not work
without the `paragraph` level.)

To store a JSON version of a VRT document in a hierarchy of files
named with a four-digit counter, no more than one million tokens in
each JSON files (but rounded up to fill a text element), with the
`ref` and `dephead` values of each token as (natural) numbers (or
`-1`), all other values as strings:

    $ Kielipankki-utilities/json/vrt-to-json \
	     --out=/wrkdir/c31/##/part-##.json \
	     --limit=1000000 \
	     --nat=ref,dephead \
	     /corpora/e.g./c31.vrt

The `#`-characters are replaced with counter digits, overflowing to
the leftmost character. Without counter digits, all JSON objects are
written to the same stream. Without size limit, only one JSON object
is written.

So the first output file would be `/wrkdir/c31/00/part-00.json`. And
so on.

The default is to turn each token into a JSON object with named
fields. Optionally, by `--positional`, `-p`, each token is written as
an array, with the corresponding array of field names on top of the
JSON object.

To combine a whole corpus of VRT files into one JSON object file,
concatenate the corpus files into the standard input stream of the
converter.

# Not converting VRT to JSON #

There may be more material in the input than is wanted in the
output.

Positional data is easily dropped with `vrt-tools/vrt-drop`, or even
`cut` if a corresponding adjustment is made to any name commment.
Structural attributes can be similarly dropped with other means, like
`sed`, should such removal be desired.

A trick that may help to reduce the footprint of an uninteresting
structural attribute is to request that it be written as a natural
number. (The value would likely be written as `-1`, unless the value
happens to be a written representation of some natural number.)

# Reading JSON #

Python's `json.load` seems to intern the keys but not the string
values in each JSON object. It would not be difficult to use an
appropriate `object_pair_hook` to intern some of the known frequent
values, like PoS tags, for an enormous gain in the memory footprint of
the loaded object, even across loads. Sharing keys across loads, for a
moderate gain, would also be easy.

Reading more than one JSON object from the same stream is left as an
exercise to anyone who chooses to have that problem. Same goes for
reading JSON objects that would exceed available memory. Such files
are easy to create.
