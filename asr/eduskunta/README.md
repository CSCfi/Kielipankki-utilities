# Eduskunnan materiaalin vienti LAT:iin


## Lähtöpiste
Lähtöpiste on, että raaka eduskunnan materiaali koostuu:
1. .metadata -tiedostoista
2. .eaf -tiedostoista
3. .mp4 -tiedostoista


## Proseduuri
1. Siirrä kaikki tiedostot (.metadata, .eaf, .mp4) samaan kansioon
2. Lataa skriptit tästä kansiosta samaan kansioon tiedostojen kanssa
3. Aja skripti

  - Skripti nimeää lähtöpisteen tiedostot muotoon vvvv-kk-pp ja järjestelee vuosittain kevään ja syksyn omiin kansioihinsa
  - Skripti lisäksi normalisoi PARTICIPANT ja TIER_ID kohdat, jotta annotaatiokerrokset on mahdollista yhdistellä toisiinsa

4. Käytä aineisto [Arbilin](https://tla.mpi.nl/tools/tla-tools/arbil/) kautta. Arbil merkkaa tiedostojen koot oikein.
5. Vie luodut .eaf tiedostot [Elaniin](https://tla.mpi.nl/tools/tla-tools/elan/) ja exportoi ne TextGrid -muotoon. Muista raksittaa utf-8 ennen kuin vienti alkaa, muuten ääkköset eivät mene oikein
6. Käsittele Textgrid tiedostot Praat scripteillä TODO
7. Exportoi aineisto Arbilista
8. Vie aineisto LAT:iin käyttäen takaovea TODO

  - Kts. <https://wiki.csc.fi/wiki/Kielipankki/Lat>



