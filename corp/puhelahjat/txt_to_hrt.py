#! /usr/bin/env python3
# -*- mode: Python; -*-

# Based on scripts/hrt-from-txt by Jussi Piitulainen

import os, re, sys, tempfile, traceback
import argparse
import csv

def getargs():
    argparser = argparse.ArgumentParser(
        description='''Convert Puhelahjat to HRT''')
    argparser.add_argument('dirname',
                           help='name of input file')
    argparser.add_argument('--metadata-file', metavar='FILE', required=True,
                           help='read text metadata from FILE in CSV format')
    return argparser.parse_args()

def read_metadata_file(filename,value):
    value = re.search('clt\d*_.*\d', value).group(0)
    with open(filename, 'r') as metadatafile:
        reader = csv.DictReader(metadatafile,delimiter=',', restval='',
                                fieldnames=["recordingId","clientPlatformName","clientPlatformVersion","contentType","recordingBitDepth","recordingDuration","recordingNumberOfChannels","recordingSampleRate","recordingTimestamp","theme","topic", "dialect","gender","L1","age","placeOfResidence","birthplace","occupation","education"]) 
        row = next((item for item in reader if item['recordingId'] == value))
    return row

def get_prompt(theme, topic):
    topics= {"01":"Kerro aamiaisesta\
    Voit kertoa lemmikistä tai muusta eläimestä. Paina Äänitä-nappia, kun olet valmis puhumaan.\
    Kun olet valmis, paina Lopeta äänitys.",
    "02":"Auta eläintä\
    Neuvo vuohiparkaa juurta jaksain!\
    Mikä jalka ensin?",
    "03":"Kuva-arvoitus\
    Päina Äänitä ja arvaile, mitä kuvasta paljastuu.\
    Kuva aukeaa 15 sekunnin välein.",
    "04":"Leiki selostajaa\
    Video kestää minuutin.\
    Alternative prompt:\
    Leiki selostajaa\
    Video kestää vajaan minuutin.",
    "05":"Lemmikkini ui\
    Pohdi, puhu ja pulise vapaasti!",
    "06":"Tunnista koirat\
    Mitä muistoja näistä herää?\
    Jos et tunnista koiria, kerro vapaasti, mitä näet kuvassa.",
    "07":"Arvaa eläin\
    Mikä eläin on kyseessä?\
    Paina Äänitä ja höpöttele Ransunkin puolesta.",
    "08":"Entisajan lemmikit\
    Video kestää reilun minuutin.",
    "09":"Rakkain eläimeni\
    Puhu niin kauan kuin juttua riittää.",
    "10":"Alkuverryttely\
    Paina Äänitä ja ala turista! Kuka tässä on ja mistä hänet tunnetaan?\
    Kun olet kertonut tarpeeksi, paina Lopeta äänitys.",
    "11":"Haastattelijana\
    Paina äänitä, niin kuva vaihtuu 15 sekunnin välein.",
    "12":"Suosikkini\
    Onko suosikkisi Suomesta, maailman kisakentiltä vai naapurikylästä?\
    Milloin suhteenne alkoi?",
    "13":"Selostajana\
    Viren on sinipaita numero 228. Antaa mennä!",
    "14":"Pallo maaliin\
    Kuvittele ja selitä pelaajien liikkeet! Sinun pelaajasi ovat värillisiä, vastustaja mustalla.\
    Alternative prompt:\
    2000-luvun urheilija\
    Yleensä Suomessa valitaan Vuoden urheilija. Nyt venytetään aikarajaa vähän pidemmäksi.\
    Päinä Äänitä, niin näet videolla suomalaisia urheilutähtiä. Kenet heistä pitäisi valita 2000-luvun urheilijaksi?",
    "15":"Liikuntamuisto\
    Muistele ja hersytä vapaasti.\
    Oletko yksilö- vai joukkuetyyppiä? Kerro tuore kokemus tai palaa vuosien taakse!\
    Alternative prompt:\
    Pysäytä Seppo\
    Seuraavaksi on sinun vuorosi: Yritä saada Seppo pysähtymään!\
    Paina Äänitä, niin näet saman videon ilman ääniä.",
    "16":"Arvaa laji\
    Kuva aukeaa 15 sekunnin välein. Jos arvaat lajin: Mikä vuosi on kyseessä ja keitä kuvassa on?",
    "40":"Alkulämmittely\
    Verrytellään ensin. Kuvan Suomi-faneissa on kolme pientä eroa.\
    Paina Äänitä ja etsi eroja ääneen!",
    "41":"Kysy suosikiltasi\
    Sitten eteenpäin! Olet voittanut tapaamisen suosikkiurheilijasi kanssa.\
    Nyt voit kysyä häneltä aivan kaikki mielessäsi olevat kysymykset.",
    "42":"Selosta Virénin juoksu\
    Nyt pääset selostamaan klassikkoa. Näet lyhyen videon Lasse Virénin uskomattomasta suorituksesta.\
    Paikka on Munchenin olympiastadion ja vuosi 1972. Video alkaa, kun painat Äänitä.",
    "43":"Ihme lajit\
    Suomen kesässä kisataan erikoisissa urheilulajeissa. Ulkomainen kaverisi ei ole koskaan kuullut tällaisista.\
    Näet videolla viisi lajia. Selitä ne kaverillesi.",
    "44":"Penkkiurheilumuisto\
    Mikä on sinun paras penkkiurheilumuistosi? Missä ja milloin se oli?\
    Muistele ja hersytä sielusi kyllyydestä.",
    "17":"Kerro aamiaisestasi\
    Kun haluat puhua, paina Äänitä-nappia.\
    Kun olet valmis, paina Lopeta äänitys.",
    "18":"Katson ikkunasta\
    Kerro ja kuvaile, mitä lähimmästä ikkunastasi näkyy.",
    "19":"Tärkeä esineeni\
    Mieti rauhassa, paina Äänitä ja ajattele ääneen.\
    Puhu niin kauan kuin haluat!",
    "20":"Turhat tavarani\
    Kerro myös, miksi et ole onnistunut luopumaan noista tavaroista?",
    "21":"Lempivaate\
    Kertoile vapaasti: Mistä sait vaatteen?\
    Kuinka tärkeä sen väri on?",
    "22":"Mistä kodikkuus syntyy?\
    Puhu ja pulise niin kauan kuin haluat.",
    "23":"Harjoitellaan ensin!\
    Paina Äänitä-nappia ja laske sitten ääneen leppäkertussa näkyvät pilkut.\
    Muistuuko mieleesi myös leppäkerttuihin liittyvä laulu tai loru? Voit tapailla sen sanoja.",
    "24":"Kekseliäät kesätapahtumat\
    Kerro, mitä tässä kuvassa tapahtuu. Satutko tietämään, mistä kisasta on kyse?\
    Ideoi myös itse – millainen kesätapahtuma Suomesta vielä puuttuu? Irrottele vapaasti!",
    "25":"Kerro sääennuste\
    Kaikissa meissä asuu pieni meteorologi!\
    Ryhdy Kertuksi ja esittele perjantain sää.",
    "26":"Etsi eroavaisuudet\
    Kuvissa on 3 eroavaisuutta. Etsi ne ääneen ajatellen.\
    Anna pähkäilysi kuulua!",
    "27":"Kerro kesätaitosi\
    Mikä sujuu sinulta kuin Strömsössä?\
    Osaatko esimerkiksi tyhjentää ulkohuussin, tehdä kukkaseppeleen tai huoltaa polkupyörän?",
    "28":"Mitä näkyy?\
    Oho! Puoli Seitsemän -toimittaja Minttu on havainnut niityllä jotain hämmästyttävää.\
    Hyppää neiti kesäheinän saappaisiin ja kerro, mitä hän näkee ja mitä siitä ajattelee.",
    "29":"Toimi silminnäkijänä\
    Tämä parivaljakko vohki vyölaukkusi festareilla. Kuvaile heidän ulkonäkönsä tarkasti rikoksen selvittämiseksi.\
    Kerro myös, mitä olit pakannut festarilaukkuusi.",
    "30":"Kokoa eväskori\
    Mitä sinun unelmiesi ulkokattaus sisältää?\
    Onko tarjolla sekä suolaista että makeaa? Haetko syötävät kaupan hyllyltä tai valmistatko jotain itse?",
    "31":"Neuvo perille\
    Tapaat Oulussa matkailuohjelma Egenlandin juontajat Nicken ja Hannamarin.\
    Neuvo heidät ensin kahville (1), sitten puistoon (2) ja lopulta Toripolliisin luokse (3).",
    "32":"Kuvaile kesänviettoa\
    Saat ulkoavaruudesta vieraita, joilla on videokuvaa suomalaisesta kesänvietosta.\
    Selosta heille, mitä videon tilanteissa tapahtuu. Video alkaa, kun painat Äänitä.",
    "33":"Kerro rakkaasta kesäpaikasta\
    Mikä on sinulle tärkeä kesäpaikka, nykyinen tai muistoissa oleva?\
    Rantasauna, huvipuisto, kaupungin vilkkain terassi...",
    "34":"Harjoitellaan ensin!\
    Paina Äänitä-nappia ja kerro, kuinka usein pesit keväällä käsiäsi – entä nyt?\
    Alternative prompt:\
    Harjoitellaan ensin\
    Paina Äänitä-nappia ja kerro, miten kosket pintoihin julkisissa tiloissa: suojaatko kätesi vai et?\
    Juttele rennosti puhekielellä. Tauot ja takeltelu ovat sallittuja!",
    "35":"Tavallinen päiväni\
    Muistele seuraavaksi, millainen oli tavallinen arkipäiväsi poikkeusaikana.\
    Kerro, lähditkö töihin vai teitkö töitä tai opiskelit kotoa käsin?\
    Alternative prompt:\
    Mikä suututtaa?\
    Koronavirus ei kadonnutkaan kesällä 2020, kuten moni odotti.\
    Kerro, mikä sinua suututtaa tai ahdistaa koronatilanteessa juuri nyt eniten.",
    "36":"Tätä kaipasin\
    Mitä asioita kaipasit rajoitustoimien aikana eniten? Kerro yksi tai useampi.\
    Voit miettiä rauhassa ennen äänitystä.\
    Alternative prompt:\
    Tätä kaipasin\
    Tiukimpien rajoitustoimien aikana moni asia oli kielletty. Mitä asiaa sinä kaipasit silloin eniten?\
    Kerro yksi tai useampi. Voit miettiä rauhassa ennen äänitystä.",
    "37":"Muutokset\
    Pohdi seuraavaksi, toiko koronavirus muutoksia suunnitelmiisi.\
    Jäikö sinulta juhlat tai matka väliin?\
    Alternative prompt:\
    Kysy maskista\
    Vuonna 2020 maskeista tuli valtavirtaa. Paina Äänitä, niin näet erilaisia kasvosuojien käyttäjiä.\
    Mitä kysyisit heiltä, jos he tulisivat vastaan?",
    "38":"Hyvät asiat\
    Kukaan ei jää kaipaamaan Covid-19 -virusta tai talouskriisiä, mutta erikoisessa ajassa oli jotain hyvääkin.\
    Toiko korona-aika elämääsi positiivisia asioita?\
    Alternative prompt:\
    Hyvät asiat\
    Kukaan ei jää kaipaamaan covid-19-virusta tai talouskriisiä, mutta on tässä ajassa on ollut hyvääkin.\
    Näet kuvassa joitakin korona-ajan positiivisia asioita. Mitä ne tuovat mieleesi?",
    "39":"Mitä opimme?\
    Mitä ihmiskunta tulee mielestäsi oppimaan tästä pandemiasta?\
    Alternative prompt:\
    Mitä opimme?\
    Mitä ihmiskunta voi mielestäsi oppia tästä pandemiasta?",
    "45":"Ohjeista kuritonta\
    Näet kohta videolla kolme tilannetta. Anna niissä näkyville käskyjä!\
    Video alkaa, kun painat Äänitä.",
    "46":"Verrytellään ensin\
    Näet kohta tutun meemipätkän. Kerro ääneen, millaiseen tilanteeseen se sopisi.\
    Video käynnistyy, kun painat Äänitä.",
    "47":"Pientä tuunausta\
    Filttereillä kasvoja ja kehoa voi muokata helposti millaiseksi haluaa. Mitä ajattelet niistä?\
    Tässä on yksi esimerkki. Kun painat Äänitä, näet toisen.",
    "48":"Some-suomi -tulkkaus\
    Somella on oma kielioppi, jota vanhemmat eivät välttämättä tunne.\
    Paina Äänitä ja tulkkaa kuvassa näkyvät asiat mummollesi.",
    "49":"Somen botit\
    Somessa on profiileja, jotka esittävät ihmistä, mutta niiden takana on osin tai kokonaan tietokoneohjelma.\
    Millaisia botteja sinä olet kohdannut? Mistä tunnistat sellaisen?",
    "50":"Harjoitellaan ensin\
    Mitä someja käytät?\
    Kun olet valmis puhumaan, paina Äänitä.",
    "51":"Suuria uutisia\
    Paina Äänitä ja kerro ajatuksiasi videosta.",
    "52":"Valehtelevat kuvat\
    Kun painat Äänitä, näet peräkkäin neljä väärennettyä kuvaa.\
    Kerro, mikä kuvissa on valetta.",
    "53":"Mitä näkyy, mitä ei?\
    Jo pelkkä rajaus voi vaikuttaa kuvaan paljon.\
    Paina Äänitä, niin näet kolme kuvaa. Mitä näet kuvassa ensin – entä sitten?",
    "54":"Usko tai älä!\
    Sait Ohoh!-lehden toimittajana tuoreen silminnäkijäkuvan Mikael Gabrielista.\
    Pomosi odottaa siitä mehevää klikkiotsikkoa. Millaisia keksit?",
    "55":"Harjoitellaan ensin\
    Mitä nämä emojit tarkoittavat?\
    Kun olet valmis puhumaan, paina Äänitä. Selitä kaikessa rauhassa.",
    "56":"Feikkikuva vai ei?\
    Kuvia voidaan käsitellä ja niihin liittää asioita, jotka eivät niihin aluksi kuuluneet.\
    Tunnistatko valekuvat oikeista? Paina Äänitä, niin saat arvioitavaksesi neljä kuvaa.",
    "57":"Unelmien mainos\
    Mainoksissa näytetään usein unelmia: osta, niin sinunkin elämästäsi voi tulla tällaista.\
    Seuraavaksi näet kolme mainoskuvaa. Millaisia unelmia niissä näkyy?",
    "58":"Valeuutistarkastaja\
    Näet netissä kolme uutisotsikkoa.\
    Tunnista niistä valheelliset ja perustele vastauksesi.",
    "59":"Etsi erot\
    Kun olet löytänyt erot, paina Äänitä ja kerro niistä omin sanoin.\
    Juttele puhekielellä! Takeltelu ja hymähtely ovat sallittuja.",
    "60":"Terveisiä perseestä!\
    Aika tulla ulos kaapista.\
    Paina Äänitä ja kerro, mikä potuttaa!",
    "61":"Sanaselityspeli\
    Sana vaihtuu 10  sekunnin välein.\
    Video alkaa, kun painat Äänitä.",
    "62":"Tunnustusten huone\
    Ole huoleti: sinua ei voi jäljittää. Puheesi menee vain tutkimuskäyttöön.",
    "63":"Seksiä ja saksia!\
    Mieti ääneen, miksi nämä kohtaukset aikanaan joutuivat sensuurin saksimiksi.\
    Video alkaa, kun painat Äänitä. Se kestää reilun minuutin.",
    "64":"Opasta synnin polulla\
    Siis ensin tie hotellista baariin, sitten klubille ja lopuksi hotellille.\
    Paikat vaihtuvat 15 sekunnin välein.",
    "65":"Reenataas eka!\
    Kuvissa on 3 eroavaisuutta.\
    Paina Äänitä ja etsi erot ääneen ajatellen.",
    "66":"Kerro sääennuste\
    Ryhdy Ylen meteorologiksi ja esittele kesäperjantain sää.\
    Paina Äänitä, niin näet tarkemman kartan.",
    "67":"Lirkuttele lomakuvista\
    Tuore ihastuksesi esittelee matkakuviaan. Tee vaikutus häneen ja kysele kuvista.\
    Näet matkakuvat videolla, kun painat Äänitä-nappia.",
    "68":"Kerrospukeutumisen koreografia\
    Olet lähdössä ulos paukkupakkasiin.\
    Selosta, missä järjestyksessä puet päälle nämä tamineet.",
    "69":"Kuvaile kesänviettoa\
    Saat ulkoavaruudesta vieraita, joilla on videokuvaa suomalaisesta kesänvietosta.\
    Selosta heille, mitä videon tilanteissa tapahtuu. Video alkaa, kun painat Äänitä.",
    "70":"Onko ilmoja piisannu?\
    Tätisi Kanarialta soittaa kyselläkseen kuulumisia. Sää on hänen lempiaiheensa.\
    Miten kuvailet hänelle tämän ja eilisen päivän säätä?",
    "71":"#päivänfiilis\
    Näet videolla neljä kuvaparia. Kerro, kumpi kuvista sopii paremmin tämänhetkiseen mielentilaasi.\
    Video käynnistyy Äänitä-napista.",
    "72":"Keräillen ja metsästäen\
    Oletko käynyt sienessä, marjassa, kalassa tai metsästämässä?\
    Mikä on ollut päräyttävin reissusi luontoäidin ruokakomerossa?"
    }

    if theme=='01':
        return ("Eläinystävät",topics[topic])
    elif theme=='02':
        return ("Urheiluhetket",topics[topic])
    elif theme=='03':
        return ("Lähelläni juuri nyt",topics[topic])
    elif theme=='04':
        return ("Sukella kesään",topics[topic])
    elif theme=='05':
        return ("Kirottu korona",topics[topic])
    elif theme=="06":
        return ("Mediataidot lukio",topics[topic])
    elif theme=="07":
        return ("Mediataidot 8-9 lk.",topics[topic])
    elif theme=="08":
        return ("Mediataidot 4-6 lk.",topics[topic])
    elif theme=="09":
        return ("K-18",topics[topic])
    elif theme=="10":
        return ("Luonto, sää ja mää",topics[topic])

def main(args):

    def issome(line): return not line.isspace()
    
    directory = args.dirname
    for filename in os.listdir(directory):
        if filename.endswith('.txt'):
            print(filename)
            ins = directory+"/"+filename
            ous = re.sub("txt","hrt",ins)
            metadata = read_metadata_file(args.metadata_file,ins)
            rec_id = re.search("clt\d*_.*\d",ins).group(0)
            client_id = re.search("clt\d*",ins).group(0)
            theme, prompt = get_prompt(metadata['theme'],metadata['topic'])

            with open(ins, 'r') as ins:
                with open(ous, 'w') as ous:
                    
                    print('<text recording_id="'+rec_id+'" client_id="'+client_id+'" platform_name="'+metadata['clientPlatformName']+
                            '" platform_version="'+metadata['clientPlatformVersion']+'" content_type="'+
                            metadata['contentType']+'" bit_depth="'+metadata['recordingBitDepth']+
                            '" duration="'+metadata['recordingDuration']+'" number_of_channels="'+metadata['recordingNumberOfChannels'] +
                            '" samplerate="'+metadata['recordingSampleRate']+'" timestamp="'+metadata['recordingTimestamp']+
                            '" theme="'+metadata['theme']+'" topic="'+metadata['topic']+'" theme_text="'+theme+'" prompt="'+prompt+'" dialect="'+metadata['dialect']+
                            '" gender="'+metadata['gender']+'" l1="'+metadata['L1']+'" age="'+metadata['age']+'" place_of_residence="'+
                            metadata['placeOfResidence']+'" birthplace="'+metadata['birthplace']+'" occupation="'+metadata['occupation']+
                            '" education="'+metadata['education'] +'">', file = ous)
                    for line in ins:
                        if line is None: 
                            return
                        else:
                            ship(line, ous)
                    print('</text>', file = ous)

def ship(para, ous):
    print('<paragraph>', file = ous)
    print(para,
        end = '' if para.endswith('\n') else '\n',
        file = ous)
    print('</paragraph>', file = ous)

if __name__ == '__main__':
    args = getargs()
    # consider it a win to crash now if not UTF-8
    # and not produce invalid output in that case
    main(args)
