#!/bin/sh

if [ "$1" = "--help" ]; then
    echo "ceal-txt-to-vrt.sh [--austen|--dickens|--james] [--fin|--eng]";
    echo "source text must be in AUTHOR/AUTHOR_LANG.txt, e.g. austen/austen_fi.txt"
    exit 0;
fi

vrttools="";

### Austen
if [ "$1" = "--austen" ]; then    
    if [ "$2" = "--eng" ]; then
	
	## English text	
	(cat austen/austen_en.txt | perl -pe 's/^(.*)$/\1\n/;' | perl -pe 's/^(Chapter [0-9][0-9]?)$/###C: <\/chapter>\n###C: <chapter title="\1">\n###C: <paragraph type="heading">\n\1\n/;' ; echo "###C: </chapter>"; echo "EXTRA_LINE_FOR_TNPP") | tac | head -n -1 | tac > austen/austen_en_1.txt	
	echo "parsing austen_en"
	cat austen/austen_en_1.txt | python3 full_pipeline_stream.py --gpu -1 --conf models_en_ewt/pipelines.yaml parse_plaintext > austen/austen_en_2.conllu
	cat austen/austen_en_2.conllu | perl -pe 's/^# newpar/<paragraph>/; s/^# sent_id = [0-9]+/<sentence>/; s/^# newdoc//; s/^# text = .*//; s/^# //;' | head -n -6 > austen/austen_en_3.conllu
	cat austen/austen_en_3.conllu | ./austen-conllu-to-vrt.pl --eng > austen/austen_en.vrt
	$vrttools/vrt-keep -i -n 'word,id,lemma,upos,xpos,feats,head,deprel,deps,misc' austen/austen_en.vrt
	$vrttools/vrt-rename -i -m id=ref -m head=dephead -m feats=msd -m upos=pos austen/austen_en.vrt
	# msd-bar-to-space.pl
	cat austen/austen_en.vrt | ./ceal-insert-links.pl --austen > austen/tmp && mv austen/tmp austen/austen_en.vrt;
    fi
    if [ "$2" = "--fin" ]; then
	
	## Finnish text
	(cat austen/austen_fi.txt | perl -pe 's/^(.*)$/\1\n/;' | perl -pe 's/^([^ ]+ luku)$/###C: <\/chapter>\n###C: <chapter title="\1">\n###C: <paragraph type="heading">\n\1\n/;' ; echo "###C: </chapter>"; echo "EXTRA_LINE_FOR_TNPP") | tac | head -n -1 | tac > austen/austen_fi_1.txt
	echo "parsing austen_fi"
	cat austen/austen_fi_1.txt | python3 full_pipeline_stream.py --gpu -1 --conf models_fi_tdt/pipelines.yaml parse_plaintext > austen/austen_fi_2.conllu
	cat austen/austen_fi_2.conllu | perl -pe 's/^# newpar/<paragraph>/; s/^# sent_id = [0-9]+/<sentence>/; s/^# newdoc//; s/^# text = .*//; s/^# //;' | head -n -6 > austen/austen_fi_3.conllu
	cat austen/austen_fi_3.conllu | ./austen-conllu-to-vrt.pl --fin > austen/austen_fi.vrt
	$vrttools/vrt-keep -i -n 'word,id,lemma,upos,xpos,feats,head,deprel,deps,misc' austen/austen_fi.vrt
	$vrttools/vrt-rename -i -m id=ref -m head=dephead -m feats=msd -m upos=pos austen/austen_fi.vrt
	# msd-bar-to-space.pl
	cat austen/austen_fi.vrt | ./ceal-insert-links.pl --austen > austen/tmp && mv austen/tmp austen/austen_fi.vrt;
    fi
    exit 0;
fi

### Dickens
if [ "$1" = "--dickens" ]; then
    if [ "$2" = "--eng" ]; then

	## English text
	(cat dickens/dickens_en.txt | perl -pe 's/^(.*)$/\1\n/;' | perl -pe 's/^(CHAPTER( [IVXL]+)?( \(?[0-9][0-9]\-[0-9][0-9]\)?)?)$/###C: <\/chapter>\n###C: <chapter title="">\n\1\n/;' ; echo "###C: </chapter>"; echo "EXTRA_LINE_FOR_TNPP") | tac | head -n -1 | tac > dickens/dickens_en_1.txt
	# grep -A 3 'CHAPTER' dickens_en_1.txt | egrep -v '^CHAPTER' | egrep -v '^--' | perl -pe 's/^ *\n$//;' # This is placed in ./dickens-conllu-to-vrt.pl
	echo "parsing dickens_en"
	cat dickens/dickens_en_1.txt | python3 full_pipeline_stream.py --gpu -1 --conf models_en_ewt/pipelines.yaml parse_plaintext > dickens/dickens_en_2.conllu
	cat dickens/dickens_en_2.conllu | perl -pe 's/^# newpar/<paragraph>/; s/^# sent_id = [0-9]+/<sentence>/; s/^# newdoc//; s/^# text = .*//; s/^# //;' | head -n -6 > dickens/dickens_en_3.conllu
	cat dickens/dickens_en_3.conllu | ./dickens-conllu-to-vrt.pl --eng > dickens/dickens_en.vrt
	$vrttools/vrt-keep -i -n 'word,id,lemma,upos,xpos,feats,head,deprel,deps,misc' dickens/dickens_en.vrt
	$vrttools/vrt-rename -i -m id=ref -m head=dephead -m feats=msd -m upos=pos dickens/dickens_en.vrt
	# msd-bar-to-space.pl
	cat dickens/dickens_en.vrt | ./ceal-insert-links.pl --dickens > dickens/tmp && mv dickens/tmp dickens/dickens_en.vrt;
    fi
    if [ "$2" = "--fin" ]; then

	## Finnish text
	(cat dickens/dickens_fi.txt | perl -pe 's/^(.*)$/\1\n/;' | perl -pe 's/^([^ ]+ luku)$/###C: <\/chapter>\n###C: <chapter title="">\n\1\n/;' ; echo "###C: </chapter>"; echo "EXTRA_LINE_FOR_TNPP") | tac | head -n -1 | tac > dickens/dickens_fi_1.txt
	# egrep -A 3 '^[^ ]+ luku$' dickens_fi_1.txt | egrep -v '^[^ ]+ luku' | egrep -v '^--' | perl -pe 's/^ *\n$//;' # This is placed in ./dickens-conllu-to-vrt.pl
	echo "parsing dickens_fi"
	cat dickens/dickens_fi_1.txt | python3 full_pipeline_stream.py --gpu -1 --conf models_fi_tdt/pipelines.yaml parse_plaintext > dickens/dickens_fi_2.conllu
	cat dickens/dickens_fi_2.conllu | perl -pe 's/^# newpar/<paragraph>/; s/^# sent_id = [0-9]+/<sentence>/; s/^# newdoc//; s/^# text = .*//; s/^# //;' | head -n -6 > dickens/dickens_fi_3.conllu
	cat dickens/dickens_fi_3.conllu | ./dickens-conllu-to-vrt.pl --fin > dickens/dickens_fi.vrt
	$vrttools/vrt-keep -i -n 'word,id,lemma,upos,xpos,feats,head,deprel,deps,misc' dickens/dickens_fi.vrt
	$vrttools/vrt-rename -i -m id=ref -m head=dephead -m feats=msd -m upos=pos dickens/dickens_fi.vrt
	# msd-bar-to-space.pl
	cat dickens/dickens_fi.vrt | ./ceal-insert-links.pl --dickens > dickens/tmp && mv dickens/tmp dickens/dickens_fi.vrt;
    fi
    exit 0;
fi

### James
if [ "$1" = "--james" ]; then
    if [ "$2" = "--eng" ]; then

	## English text
	(cat james/james_en.txt | tac | head -n -2 | tac | head -n -1 | perl -pe 's/^(.*)$/\1\n/;' | perl -pe 's/^(CHAPTER [IVXL]+)$/###C: <\/chapter>\n###C: <chapter title="\1">\n###C: <paragraph type="heading">\n\1\n/;' ; echo "###C: </chapter>"; echo "EXTRA_LINE_FOR_TNPP") | tac | head -n -1 | tac > james/james_en_1.txt
	echo "parsing james_en"
	cat james/james_en_1.txt | python3 full_pipeline_stream.py --gpu -1 --conf models_en_ewt/pipelines.yaml parse_plaintext > james/james_en_2.conllu
	cat james/james_en_2.conllu | perl -pe 's/^# newpar/<paragraph>/; s/^# sent_id = [0-9]+/<sentence>/; s/^# newdoc//; s/^# text = .*//; s/^# //;' | head -n -6 > james/james_en_3.conllu
	cat james/james_en_3.conllu | ./james-conllu-to-vrt.pl --eng > james/james_en.vrt
	$vrttools/vrt-keep -i -n 'word,id,lemma,upos,xpos,feats,head,deprel,deps,misc' james/james_en.vrt
	$vrttools/vrt-rename -i -m id=ref -m head=dephead -m feats=msd -m upos=pos james/james_en.vrt
	# msd-bar-to-space.pl
	cat james/james_en.vrt | ./ceal-insert-links.pl --james > james/tmp && mv james/tmp james/james_en.vrt;
    fi
    if [ "$2" = "--fin" ]; then
	
	## Finnish text
	(cat james/james_fi.txt | tac | head -n -2 | tac | head -n -1 | perl -pe 's/^(.*)$/\1\n/;' | perl -pe 's/^([^ ]+ luku)$/###C: <\/chapter>\n###C: <chapter title="\1">\n###C: <paragraph type="heading">\n\1\n/;' ; echo "###C: </chapter>"; echo "EXTRA_LINE_FOR_TNPP") | tac | head -n -1 | tac > james/james_fi_1.txt
	echo "parsing james_fi"
	cat james/james_fi_1.txt | python3 full_pipeline_stream.py --gpu -1 --conf models_fi_tdt/pipelines.yaml parse_plaintext > james/james_fi_2.conllu
	cat james/james_fi_2.conllu | perl -pe 's/^# newpar/<paragraph>/; s/^# sent_id = [0-9]+/<sentence>/; s/^# newdoc//; s/^# text = .*//; s/^# //;' | head -n -6 > james/james_fi_3.conllu
	cat james/james_fi_3.conllu | ./james-conllu-to-vrt.pl --fin > james/james_fi.vrt
	$vrttools/vrt-keep -i -n 'word,id,lemma,upos,xpos,feats,head,deprel,deps,misc' james/james_fi.vrt
	$vrttools/vrt-rename -i -m id=ref -m head=dephead -m feats=msd -m upos=pos james/james_fi.vrt
	# msd-bar-to-space.pl
	cat james/james_fi.vrt | ./ceal-insert-links.pl --james > james/tmp && mv james/tmp james/james_fi.vrt;
    fi
    exit 0;
fi
