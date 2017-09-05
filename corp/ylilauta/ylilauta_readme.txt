@asahala/fin-clarin/2015

Requires vrt_tools.py for tokenizing and sentence
splitting.

How to use:

$python ylilauta_parse_warc.py < file.warc > file.tmp
$python ylilauta_make_vrt.py < file.tmp > file.vrt

_parse_warc.py beautifies the WARC file so that it is
easier to convert into VRT.

_make_vrt.py produces the VRT file.

For Heritrix WARC files, please contact Heidi Jauhiainen
or Tommi Jauhiainen.
