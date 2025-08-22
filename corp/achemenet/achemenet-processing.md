
# Processing Achemenet data for Korp

## Resource information

- *Resource name*: Achemenet Babylonian texts – Kielipankki version
  2020-12, Korp
- *Resource short name*: achemenet-2020-12-korp
- *Persistent identifier*: http://urn.fi/urn:nbn:fi:lb-2023062101

## Initial VRT format

The Achemenet corpus data had been converted to an initial VRT format,
one file per subcorpus, by Aleksi Sahala. This original VRT data is
[in IDA](https://ida.fairdata.fi/f/88855861).

The VRT data was then post-processed in several steps on Puhti in
February–March 2025 by Jyrki Niemi, with feedback from Tero Alstola.

## Post-processing VRT

The following post-processing steps are Bash command lines on Puhti.
They assume that the original VRT files are in subdirectory
`achemenet-orig_20250206` and the converted VRT files in `input-vrt`.

Note that the steps have been documented afterwards, based on Bash
command-line history.

1. Convert CR+LF newlines to LF:
   ```bash
   for f in achemenet-orig_20250206/*.vrt; do tr -d '\r' < $f > input-vrt/$(basename $f); done
   ```

2. Remove leading and trailing whitespace in `text` attribute `museumno`:
   ```bash
   perl -pi.bak -e 's/ (museumno=")\s*(.*?)\s*"/ $1$2"/' input-vrt/*.vrt
   ```

3. Add `text` attributes `timefrom` and `timeto`:
   ```bash
   perl -i.bak2 -pe 'if (/^<text/) {s/>/ timefrom="" timeto="">/}' input-vrt/*.vrt
   ```

4. Remove sentence translation attribute:
   ```bash
   for f in input-vrt/*.vrt; do vrt-drop-attrs --backup .bak3 --structure sentence --drop translation; done
   ```

5. Add a positional-attributes comment:
   ```bash
   for f in input-vrt/*.vrt; do vrt-name -b.bak4 --map "$(echo "word lemma translation sense transcription pos oraccpos normname lang msd autolemma autopos url" | tr ' ' '\n' | awk '{print "v" NR "=" $0}' | tr '\n' ' ')" $f; done
   ```

6. Add a dummy token to completely empty texts:
   ```bash
   for f in input-vrt/*.vrt; do vrt-add-dummy -b.bak5 $f; done
   ```
   (Note that `vrt-add-dummy` was an experimental tool at this stage.)

7. Add text attribute `url_orig` for the original URL (in the original
   VRT, as a positional attribute):
   ```bash
   for f in input-vrt/*.vrt; do awk -F' ' '{print $NF}' $f | grep -v '^<[!/ps]' | grep -A1 --group-sep="" '^<' | grep -v '^$' | perl -ne 'if (/^<text.*primarypub="(.*?)"/) {print "$1\t"} else {print}' > urls/$(basename $f .vrt)-urls.tsv; done
   for f in input-vrt/*.vrt; do vrt-add-struct-attrs --data urls/$(basename $f .vrt)-urls.tsv --attribute 'primarypub url_orig' --backup .bak6 $f; done
   ```

8. Add Archive.org URL as text attribute `url`:
   ```bash
   for f in input-vrt/*.vrt; do cp -p $f{,.bak7}; done
   perl -e 'while (<>) {if (/^</) {$vrt = 1} if (! $vrt) {chomp; @f = split("\t"); $u{$f[0]} = $default = $f[1]; next } if (/^<text.* primarypub="(.*?)".* url_orig="(.*?)"/) { $pub = $1; $url = $2; if ($url eq "_") {$newurl = "_"} else { ($urlid) = ($url =~ /(?:.*)\/(\d+)/); $newurl = ""; for $k (keys(%u)) { if ($pub =~ /^\Q$k/) { $newurl = "$u{$k}$urlid"; last } } if ($newurl eq "") { print STDERR "URL not found for $pub, using default\n"; $newurl = "$default$urlid" } } s/>/ url="$newurl">/; } print }' <(grep '^CT' achemenet-archive-links.tsv) input-vrt/ach_ct55.vrt.bak7 > input-vrt/ach_ct55.vrt
   perl -e 'while (<>) {if (/^</) {$vrt = 1} if (! $vrt) {chomp; @f = split("\t"); $u{$f[0]} = $f[1]; next } if (/^<text.* primarypub="(.*?)".* url_orig="(.*?)"/) { $pub = $1; $url = $2; if ($url eq "_") {$newurl = "_"} else { ($urlid) = ($url =~ /(?:.*)\/(\d+)/); for $k (keys(%u)) { if ($pub =~ /^\Q$k/) { $newurl = "$u{$k}$urlid"; last } } } s/>/ url="$newurl">/; } print }' <(grep '^YOS' achemenet-archive-links.tsv) input-vrt/ach_yos7.vrt.bak7 > input-vrt/ach_yos7.vrt
   perl -e 'while (<>) {if (/^</) {$vrt = 1} if (! $vrt) {chomp; @f = split("\t"); $u{$f[0]} = $default = $f[1]; next } if (/^<text.* primarypub="(.*?)".* url_orig="(.*?)"/) { $pub = $1; $url = $2; if ($url eq "_") {$newurl = "_"} else { ($urlid) = ($url =~ /(?:.*)\/(\d+)/); $newurl = ""; for $k (keys(%u)) { if ($pub =~ /^\Q$k/) { $newurl = "$u{$k}$urlid"; last } } if ($newurl eq "") { print STDERR "URL not found for $pub, using default\n"; $newurl = "$default$urlid" } } s/>/ url="$newurl">/; } print }' <(grep '^Bel-' achemenet-archive-links.tsv | awk '{print "Jursa, " $0}') input-vrt/ach_belremanni.vrt.bak7 > input-vrt/ach_belremanni.vrt
   perl -e 'while (<>) {if (/^</) {$vrt = 1} if (! $vrt) {chomp; @f = split("\t"); $u{$f[0]} = $f[1]; next } if (/^<text.* primarypub="(.*?)".* url_orig="(.*?)"/) { $pub = $1; $url = $2; if ($url eq "_") {$newurl = "_"} else { ($urlid) = ($url =~ /(?:.*)\/(\d+)/); $newurl = ""; for $k (keys(%u)) { if ($pub =~ /^\Q$k/) { $newurl = "$u{$k}$urlid"; last } } if ($newurl eq "") { print STDERR "URL not found for $pub\n"; } } s/>/ url="$newurl">/; } print }' <(grep '^Strass' achemenet-archive-links.tsv) input-vrt/ach_strassmaier.vrt.bak7 > input-vrt/ach_strassmaier.vrt
   perl -e 'while (<>) {if (/^</) {$vrt = 1} if (! $vrt) {chomp; @f = split("\t"); $u{$f[0]} = $f[1]; next } if (/^<text.* primarypub="(.*?)".* url_orig="(.*?)"/) { $pub = $1; $url = $2; if ($url eq "_") {$newurl = "_"} else { ($urlid) = ($url =~ /(?:.*)\/(\d+)/); $newurl = ""; for $k (keys(%u)) { if ($pub =~ /^\Q$k/) { $newurl = "$u{$k}$urlid"; last } } if ($newurl eq "") { print STDERR "URL not found for $pub\n"; } } s/>/ url="$newurl">/; } print }' <(grep -vE '^(Strassmaier|CT 55|YOS|Bel-remanni)' achemenet-archive-links.tsv) input-vrt/ach_murashu.vrt.bak7 > input-vrt/ach_murashu.vrt
   ```
   This was done because the direct Achemenet URLs had not been
   working for some time.

9. Remove positional attribute `url` (now in text attribute `url`):
   ```bash
   for f in input-vrt/*.vrt; do vrt-drop --backup .bak8 -f url $f; done
   ```

10. Convert missing text `url` and `url_orig` values from underscore
    to empty string:
    ```bash
    perl -pi.bak9 -e 'if (/^<text/) {s/( url(?:_orig)?=")_"/$1"/g}' input-vrt/ach_*.vrt
    ```

11. Convert text `_geo_provenience` attributes values to feature sets:
    ```bash
    perl -i.bak10 -pe 'if (/^<text/) { s/(_geo_provenience=")(.*?)"/$1|$2|"/; s/\|_\|/|/ }' input-vrt/*.vrt
    ```

12. Convert `_geo_provenience` values `|undefined;XX;0;0|` to `|`:
    ```bash
    perl -i.bak11 -pe 'if (/^<text.*/) { s/( _geo_provenience="\|)undefined;XX;0;0\|"/$1"/ }' input-vrt/*.vrt
    ```

13. Convert missing text `cdlilink` attribute values from underscore
    to empty string:
    ```bash
    perl -i.bak12 -pe 'if (/^<text.*/) { s/( cdlilink=")_"/$1"/ }' input-vrt/*.vrt
    ```

14. Convert all the rest of text attribute values with a single
    underscore to empty string:
    ```bash
    perl -i.bak13 -pe 'if (/^<text/) { s/="_"/=""/g }' input-vrt/*.vrt
    ```

15. Remove from text `cdlinumber` the information also available in
    `primarypub`:
    ```bash
    perl -i.bak14 -pe 'if (/<text/) { s/( cdlinumber=".*?):(.*?)"/$1"/ }' input-vrt/*.vrt
    ```

16. Remove a duplicate text:
    ```bash
    vrt-select -v -b .bak15 --drop --test 'cdlinumber=X002195' input-vrt/ach_strassmaier.vrt
    ```

17. Change the `primarypub` value of a text:
    ```bash
    perl -i.bak16 -pe 'if (/^<text cdlinumber="X002215[":]/) { s/( primarypub=").*?"/$1Strassmaier, Cambyses 81"/ }' input-vrt/ach_strassmaier.vrt
    ```

## Creating CWB corpus

The CWB corpus was created with the
[`make_achemenet.sh`](make_achemenet.sh) script:
```bash
bash make_achemenet_2025.sh input-vrt/*.vrt
```
The script calls [`korp-make`](../../scripts/korp-make) with the
following options:
```
--add-lemgrams-without-diacritics --add-lowercase-lemgrams --no-lemmas-without-boundaries --lemgram-posmap achemenet_lemgram_posmap.tsv
```
