cat uudet_aineistot/*txt | perl muuta_korvausmerkit.pl | perl muuta_rakenne.pl | perl lisaa_pdf_linkit.pl
# perl -C -pe 's/([^\x00-\x7f])/sprintf("&#%d;", ord($1))/ge;' 

