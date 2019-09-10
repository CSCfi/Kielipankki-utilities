# The additions to the particular Omorfi transducer used by the alpha
# pipeline are used twice: in vrt-tdp-alpha-lookup before Marmot, then
# in vrt-tdp-alpha-fillup after Marmot. Hence this library module.

additions = {
    # form : { (base, tags), ... }

    # First there are the additions that mimic the original Turku
    # scripts, which are quite few.

    'esimerkiksi' : { ('esimerkiksi', ('Adv',))
    },
    'Esimerkiksi' : { ('Esimerkiksi', ('Adv', 'Up'))
    },
    'mm.' : { ('mm', ('Adv',))
    },
    'Mm.' : { ('mm', ('Adv', 'Up'))
    },

    # Then there is the list of frequent UNK forms in Iijoki, with
    # analyses, extracted by Melissa Eskin, edited by jpiitula. Not
    # sure if these are exactly in the expected format yet, or was it
    # a mistake to remove 'cap' from all entries, replace 'Cap' with
    # 'Up'

    'oisi' : { ('olla',	('V', 'Act', 'Cond', 'Sg3')),
	       ('olla',	('V', 'Cond', 'ConNeg'))
    },

    'ehki' : { ('ehkä', ('Pcle',))
    },

    'sitte' : { ('sitten', ('Adv',)),
	        ('sitten', ('Pcle',)),
    },

    'sillon' : {
        ('silloin', ('Adv',)),
	('silloin', ('Pcle',)),
	# ('silla', ('N', 'Pl', 'Ins')),
	# ('silta', ( 'N', 'Pl', 'Ins'))
    },

    'meijän' : { ('minä', ('Pron', 'Pers', 'Pl', 'Gen'))
    },

    'pittää' : { ('pitää', ('V', 'Act', 'Ind', 'Prs', 'Sg3')),
	         ('pitää', ('V', 'Act', 'Inf1', 'Sg', 'Lat'))
    },

    'ennää' : { ('enää', ('Pcle',))
    },

    'ko' : { ('kun', ('CS',)),
	     ('kun', ('Pcle',))
    },

    'semmonen' : { ('semmoinen', ('Pron', 'Sg', 'Nom')),
		   ('semmoinen', ('A', 'Pos', 'Sg', 'Nom'))
    },

    'ite' : { ('itse', ('Pcle',)),
	      ('itse', ('Pron', 'Refl', 'Pl', 'Gen')),
	      ('itse', ('Pron', 'Refl', 'Pl', 'Nom')),
	      ('itse', ('Pron', 'Refl', 'Sg', 'Gen')),
	      ('itse', ('Pron', 'Refl', 'Sg', 'Nom'))
    },

    'minnua' : { ('minä', ('Pron', 'Pers', 'Sg', 'Par'))
    },

    'Vouvila' : { ('Vouvila', ('N', 'Prop', 'Sg', 'Nom'))
    },

    'nuin' : { ('noin', ('Adv',)),
	       ('noin', ('Pcle',)),
	       ('tuo', ('Pron', 'Dem', 'Pl', 'Ins'))
	       # noki	N', 'Pl', 'Ins', 'cap
    },

    'Tarkotan' : { ('tarkoittaa', ('V', 'Act', 'Ind', 'Prs', 'Sg1', 'Up'))
    },

    'jäläkeen' : { ('jälkeen', ('Adp', 'Po')),
		   ('jälkeen', ('Adp', 'Pr')),
		   # ('jälkeen', ('Adp',)), # rather Adv?
		   ('jälki', ('N', 'Sg', 'Ill'))
    },

    'Sillon' : { ('silloin', ('Adv', 'Up')),
	         ('silloin', ('Pcle', 'Up')),
	         # ('silla', ('N', 'Pl', 'Ins', 'Up')),
	         # ('silta', ('N', 'Pl', 'Ins', 'Up'))
    },

    'tehä' : { ('tehdä', ('V', 'Act', 'Inf1', 'Sg', 'Lat')),
	       ('tehdä', ('V', 'Pass', 'Ind', 'Prs', 'Pe4', 'ConNeg'))
    },

    'pitäsi' : { ('pitää', ('V', 'Act', 'Cond', 'Sg3')),
	         ('pitää', ('V', 'Cond', 'ConNeg'))
    },

    'ainaski' : {
        # ('aina', ('Adv', 'Foc_kin')),
	# ('aina', ('Pcle', 'Foc_kin')),
	('ainakin', ('Pcle',))
    },

    'semmosta' : { ('semmoinen', ('Pron', 'Sg', 'Par')),
		   ('semmoinen', ('A', 'Pos', 'Sg', 'Par'))
    },

    'sinnua' : { ('sinä', ('Pron', 'Pers', 'Sg', 'Par'))
    },

    'Sitte' : { ('Sitten', ('Adv', 'Up')),
	        ('Sitten', ('Pcle', 'Up'))
    },

    'saapi' : { ('saada', ('V', 'Act', 'Imprt', 'Sg2')),
	        ('saada', ('V', 'Act', 'Ind', 'Prs', 'Sg3')),
	        ('saada', ('V', 'Ind', 'Prs', 'ConNeg'))
    },

    'helevetin' : { ('helvetti', ('N', 'Sg', 'Gen'))
    },

    'Ainaski' : {
        # ('aina', ('Adv', 'Foc_kin', 'Up')),
	# ('aina', ('Pcle', 'Foc_kin', 'Up')),
	('ainakin', ('Pcle', 'Up'))
    },

    'oisin' : { ('olla', ('V', 'Act', 'Cond', 'Sg1'))
    },

    'tartte' : { ('tarvita', ('V', 'Act', 'Imprt', 'Sg2')),
	         ('tarvita', ('V', 'Ind', 'Prs', 'ConNeg'))
    },

    'tiijä' : { ('tietää', ('V', 'Act', 'Imprt', 'Sg2')),
	        ('tietää', ('V', 'Ind', 'Prs', 'ConNeg'))
    },

    'viimme' : { ('viime', ('Pcle',))
    },

    'Tessu' : { ('Tessu', ('N', 'Prop', 'Sg', 'Nom'))
    },

    'tosijaan' : {
        ('tosiaan', ('Pcle',)),
	# ('tosi', ('A', 'Pos', 'Pl', 'Par', 'Px13')),
	# ('tosi', ('A', 'Pos', 'Pl', 'Par', 'PxSg3'))
    },

    'lähen' : { ('lähteä', ('V', 'Act', 'Ind', 'Prs', 'Sg1'))
    },

    'nin' : { ('niin', ('Adv',)),
	      ('niin', ('Pcle',)),
	      # ('se', ('Pron', 'Dem', 'Pl', 'Ins'))
    },

    'kiini' : { ('kiinni', ('Adv',))
    },

    'saaha' : { ('saada', ('V', 'Act', 'Inf1', 'Sg', 'Lat')),
	        ('saada', ('V', 'Pass', 'Ind', 'Prs', 'Pe4', 'ConNeg'))
    },

    'Riitu' : { ('Riitu', ('N', 'Prop', 'Sg', 'Nom'))
    },

    'tulloo' : { ('tulee', ('V', 'Act', 'Ind', 'Prs', 'Sg3'))
    },

    'ruppea' : { ('rupea', ('V', 'Act', 'Imprt', 'Sg2')),
	         ('rupea', ('V', 'Ind', 'Prs', 'ConNeg')),
	         ('rupi', ('N', 'Sg', 'Par'))
    },

    'semmosia' : { ('semmoisia', ('Pron', 'Pl', 'Par')),
		   ('semmoisia', ('A', 'Pos', 'Pl', 'Par'))
    },

    'viä' : { ('vielä', ('Pcle',))
    },

    'ylleesä' : { ('yleensä', ('Adv',))
    },

    'niihen' : { ('niiden', ('Pron', 'Dem', 'Pl', 'Gen'))
    },

    'Vouvilan' : { ('Vouvila', ('N', 'Prop', 'Sg', 'Gen'))
    },

    'Hoikkala' : { ('Hoikkala', ('N', 'Prop', 'Sg', 'Gen'))
    },

    'jouvun' : { ('joutua', ('V', 'Act', 'Ind', 'Prs', 'Sg1'))
    },

    'Heikinkallio' : { ('Heikinkallio', ('N', 'Prop', 'Sg', 'Nom'))
    },

    # believe the examples to be "sotien" rather than "sodan"
    'sottain' : { ('sota', ('N', 'Pl', 'Gen'))
    },

    'Tessun' : { ('Tessu', ('N', 'Prop', 'Sg', 'Gen', 'Up'))
    },

    'iliman' : { ('ilman', ('Adp', 'Po')),
	         ('ilman', ('Adp', 'Pr')),
	         ('ilman', ('Adv',)),
	         ('ilma', ('N', 'Sg', 'Gen'))
    },

    # 'A.' 395 kertaa Iijoessa
    # 'K.' 539 kertaa Iijoessa

    'poijat' : { ('poika', ('N', 'Pl', 'Nom')),
    },

    # or should Ins be retained for this word?
    'jonku' : {
        ('joku', ('Pron', 'Sg', 'Gen')),
	# ('jonkun', ('Pron', 'Sg', 'Ins'))
    },

    # "kotiin" might be also a noun in two ways - either "kota" Pl Ill
    # or "koti" Sg Ill - oh well
    'kottiin' : { ('kotiin', ('Adv',)),
    },

    'alakaa' : { ('alkaa', ('V', 'Act', 'Ind', 'Prs', 'Sg3')),
	         ('alkaa', ('V', 'Act', 'Inf1', 'Sg', 'Lat'))
    },

    'palajo' : { ('paljon', ('Adv',))
    },

    'tietenni' : { ('tietenkin', ('Pcle',))
    },

    'tiijät' : { ('tietää', ('V', 'Act', 'Ind', 'Prs', 'Sg2'))
    },

    'Tessun' : { ('Tessu', ('N', 'Prop', 'Sg', 'Gen'))
    },

    'koskaa' : { ('koskaan', ('Adv',)),
    },

    'semmosen' : { ('semmoinen', ('Pron', 'Sg', 'Gen')),
	           ('semmoinen', ('Pron', 'Sg', 'Ins')),
	           ('semmoinen', ('A', 'Pos', 'Sg', 'Gen'))
    },

    'assia' : { ('asia', ('N', 'Sg', 'Nom'))
    },

    'nähä' : { ('nähdä', ('V', 'Act', 'Inf1', 'Sg', 'Lat')),
	       ('nähdä', ('V', 'Pass', 'Ind', 'Prs', 'Pe4', 'ConNeg'))
    },

    'tämmönen' : { ('tämmöinen', ('Pron', 'Sg', 'Nom')),
		   ('tämmöinen', ('A', 'Pos', 'Sg', 'Nom'))
    },

    'perrään' : { ('perään', ('Adp', 'Po')),
	          ('perään', ('Adp', 'Pr')),
	          ('perään', ('Adv',)),
	          ('perä', ('N', 'Sg', 'Ill'))
    },

    'sannoo' : { ('sanoa', ('V', 'Act', 'Ind', 'Prs', 'Sg3'))
    },

    'lähe' : { ('lähteä', ('V', 'Act', 'Imprt', 'Sg2')),
	       ('lähteä', ('V', 'Ind', 'Prs', 'ConNeg'))
    },

    'helevetissä' : { ('helvetti', ('N', 'Sg', 'Ine'))
    },

    'saahaan' : { ('saada', ('V', 'Pass', 'Ind', 'Prs', 'Pe4')),
    },

    'vujen' : { ('vuosi', ('N', 'Sg', 'Gen'))
    },

    'Vimparin' : { ('Vimpari', ('N', 'Prop', 'Sg', 'Gen', 'Up'))
    },

    'kahen' : { ('kahden', ('Adv',)),
	        ('kaksi', ('Num', 'Card', 'Sg', 'Gen'))
    },

    'liijan' : { ('liian', ('Pcle',)),
	         ('liian', ('N', 'Sg', 'Gen'))
    },

    'Kassu' : { ('Kassu', ('N', 'Prop', 'Sg', 'Nom'))
    },

    'näkönen' : { ('näköinen', ('A', 'Pos', 'Sg', 'Nom'))
    },

    'Meijän' : { ('minä', ('Pron', 'Pers', 'Pl', 'Gen', 'Up'))
    },

    'ainakaa' : { ('ainakaan', ('Pcle',))
    },

    'Väinin' : { ('Väini', ('N', 'Prop', 'Sg', 'Gen'))
    },

    'äitin' : { ('äiti', ('N', 'Sg', 'Gen'))
    },

    'meleko' : { ('melko', ('Pcle',))
    },

    # eww
    'terviisiä' : {
        # ('terveisiä', ('Der_inen', 'A', 'Pos', 'Pl', 'Par')),
	('terveinen', ('N', 'Pl', 'Par'))
    },

    'huommenna' : { ('huomenna', ('Adv',))
    },

    'Lammela' : { ('Lammela', ('N', 'Prop', 'Sg', 'Nom'))
    },

    'oisit' : { ('olla', ('V', 'Act', 'Cond', 'Sg2'))
    },

    'ihtesä' : { ('itse', ('Pron', 'Refl', 'Pl', 'Gen', 'PxPl3')),
                 ('itse', ('Pron', 'Refl', 'Pl', 'Gen', 'PxSg3')),
                 ('itse', ('Pron', 'Refl', 'Pl', 'Nom', 'PxPl3')),
                 ('itse', ('Pron', 'Refl', 'Pl', 'Nom', 'PxSg3')),
                 ('itse', ('Pron', 'Refl', 'Sg', 'Gen', 'PxPl3')),
                 ('itse', ('Pron', 'Refl', 'Sg', 'Gen', 'PxSg3')),
                 # ('itse', ('Pron', 'Refl', 'Sg', 'Ins', 'PxPl3')),
                 # ('itse', ('Pron', 'Refl', 'Sg', 'Ins', 'PxSg3')),
                 ('itse', ('Pron', 'Refl', 'Sg', 'Nom', 'PxPl3')),
                 ('itse', ('Pron', 'Refl', 'Sg', 'Nom', 'PxSg3')),
    },

    'sammaa' : { ('samaa', ('Pron', 'Sg', 'Par'))
    },

    'Puranen' : { ('Puranen', ('N', 'Prop', 'Sg', 'Nom'))
    },

    'mukkaan' : { ('mukaan', ('Adp', 'Po')),
	          ('mukaan', ('Adp', 'Pr')),
	          ('mukaan', ('Adv',))
    },

    'Mannilan' : { ('Mannila', ('N', 'Prop', 'Sg', 'Gen'))
    },

    'tiijän' : { ('tietää', ('V', 'Act', 'Ind', 'Prs', 'Sg1'))
    },

    'etteen' : { ('eteen', ('Adp', 'Po')),
	         ('eteen', ('Adp', 'Pr')),
	         ('eteen', ('Adv',))
    },

    'semmoset' : { ('semmoinen', ('Pron', 'Pl', 'Nom')),
		   ('semmoinen', ('A', 'Pos', 'Pl', 'Nom'))
    },

    'Lähen' : { ('lähteä', ('V', 'Act', 'Ind', 'Prs', 'Sg1', 'Up'))
    },

    # some examples (in Iijoki) are "aidan" but more are "ajan"
    'aijan' : { ('aika', ('N', 'Sg', 'Gen'))
    },

    'ainaskaa' : { ('ainakaan', ('Pcle',))
    },

    # "kohdalla" has only this analysis in the transducer
    'kohalla' : { ('kohta', ('N', 'Sg', 'Ade'))
    },

    'täsä' : { ('tässä', ('Adv',))
    },

    'Semmonen' : { ('Semmoinen', ('Pron', 'Sg', 'Nom', 'Up')),
		   ('Semmoinen', ('A', 'Pos', 'Sg', 'Nom', 'Up'))
    },

    'meijät' : { ('minä', ('Pron', 'Pers', 'Pl', 'Acc'))
    },
}


TAGCAT = {
    'Abe' : 'CASE',
    'Abl' : 'CASE',
    'Acc' : 'CASE',
    'Ade' : 'CASE',
    'All' : 'CASE',
    'cap' : 'CASECHANGE',
    'Cap' : 'CASECHANGE',
    'CAP' : 'CASECHANGE',
    'Up' : 'CASECHANGE',
    'Com' : 'CASE',
    'Dis' : 'CASE',
    'Ela' : 'CASE',
    'Ess' : 'CASE',
    'Gen' : 'CASE',
    'Ill' : 'CASE',
    'Ine' : 'CASE',
    'Ins' : 'CASE',
    'Lat' : 'CASE',
    'Nom' : 'CASE',
    'Par' : 'CASE',
    'Prl' : 'CASE',
    'Sti' : 'CASE',
    'Tra' : 'CASE',
    'Foc_han' : 'CLIT',
    'Foc_ka' : 'CLIT',
    'Foc_kaan' : 'CLIT',
    'Foc_kin' : 'CLIT',
    'Foc_pa' : 'CLIT',
    'Foc_s' : 'CLIT',
    'Qst' : 'CLIT',

    # Q. Is Qst+Foc_s one tag or two?
    # A. Two. It comes from marmot.
    # Q. Do we have Qst+Foc_s in Korp?
    # A. Doubt it.
    # Q. Does + appear in other tags?
    # A. At least in Qst+Foc_han.

    'Comp' : 'CMP',
    'Pos' : 'CMP',
    'Superl' : 'CMP',
    'Der_inen' : 'DRV',
    'Der_ja' : 'DRV',
    'Der_lainen' : 'DRV',
    'Der_llinen' : 'DRV',
    'Der_maisilla' : 'DRV',
    'Der_minen' : 'DRV',
    'Der_oi' : 'DRV',
    'Der_sti' : 'DRV',
    'Der_tar' : 'DRV',
    'Der_tattaa' : 'DRV',
    'Der_tatuttaa' : 'DRV',
    'Der_ton' : 'DRV',
    'Der_tse' : 'DRV',
    'Der_ttaa' : 'DRV',
    'Der_ttain' : 'DRV',
    'Der_u' : 'DRV',
    'Der_vs' : 'DRV',
    'Inf1' : 'INF',
    'Inf2' : 'INF',
    'Inf3' : 'INF',
    'Inf5' : 'INF',
    'Cond' : 'MOOD',
    'Eve' : 'MOOD',
    'Imprt' : 'MOOD',
    'Ind' : 'MOOD',
    'Opt' : 'MOOD',
    'Pot' : 'MOOD',
    'ConNeg' : 'NEG',
    'Pl' : 'NUM',
    'Sg' : 'NUM',
    'AgPcp' : 'PCP',
    'Pcp' : 'PCP',
    'PrfPrc' : 'PCP',
    'PrsPrc' : 'PCP',
    'A' : 'POS',
    'Adp' : 'POS',
    'Adv' : 'POS',
    'C' : 'POS',
    'Interj' : 'POS',
    'N' : 'POS',
    'Null' : 'POS',
    'Num' : 'POS',
    'Pcle' : 'POS',
    'Pron' : 'POS',
    'Punct' : 'POS',
    'PxPl1' : 'POSS',
    'PxPl2' : 'POSS',
    'PxPl3' : 'POSS',
    'PxSg1' : 'POSS',
    'PxSg2' : 'POSS',
    'PxSg3' : 'POSS',
    'Px3' : 'POSS',
    'V' : 'POS',
    'Pe4' : 'PRS',
    'Pl1' : 'PRS',
    'Pl2' : 'PRS',
    'Pl3' : 'PRS',
    'Sg1' : 'PRS',
    'Sg2' : 'PRS',
    'Sg3' : 'PRS',
    'Abbr' : 'SUBCAT',
    'Acro' : 'SUBCAT',
    'Approx' : 'SUBCAT',
    'Card' : 'SUBCAT',
    'CC' : 'SUBCAT',
    'CS' : 'SUBCAT',
    'Dem' : 'SUBCAT',
    'Indef' : 'SUBCAT',
    'Interr' : 'SUBCAT',
    'Neg' : 'SUBCAT',
    'Ord' : 'SUBCAT',
    'Para' : 'SUBCAT',
    'Pers' : 'SUBCAT',
    'Pfx' : 'SUBCAT',
    'Po' : 'SUBCAT',
    'Pr' : 'SUBCAT',
    'Prop' : 'SUBCAT',
    'Qnt' : 'SUBCAT',
    'Real' : 'SUBCAT',
    'Recipr' : 'SUBCAT',
    'Refl' : 'SUBCAT',
    'Rel' : 'SUBCAT',
    'Sent' : 'SUBCAT',
    'Sfx' : 'SUBCAT',
    'Prs' : 'TENSE',
    'Prt' : 'TENSE',
    'Act' : 'VOICE',
    'Pass' : 'VOICE',
    'Typo' : 'OTHER',
    'Cllq' : 'OTHER',
    'Trash' : 'POS',
    'Symb' : 'POS',
    'Foreign' : 'POS',
    'UNK' : 'OTHER',
}

if __name__ == '__main__':
    print('sanity check on all additions table entries:')

    if not isinstance(additions, dict):
        print('bad additions table')
        exit(1)

    ok = True
    for word, readings in additions.items():
        if not (isinstance(word, str) and word):
            print('bad word:', repr(word))
            ok = False
        if not (isinstance(readings, set) and readings):
            print('bad reading set on word:', repr(word))
            ok = False
        else:
            for reading in readings:
                if not (isinstance(reading, tuple) and len(reading) == 2):
                    print('bad reading on word:', repr(word))
                    ok = False
                else:
                    base, tags = reading
                    if not (isinstance(base, str) and base):
                        print('bad base form on word:', repr(word))
                        ok = False
                    if not (isinstance(tags, tuple) and tags):
                        print('bad tags on word:', repr(word))
                        ok = False

    if not ok:
        print('bad entries found, not checking tags')
        exit(1)

    # the above type check was tested with various manually inserted
    # entries during development and seemed to work as intended

    bad = {
        (repr(word), repr(tag))
        for word, readings in additions.items()
        for base, tags in readings
        for tag in tags
        if tag not in TAGCAT
    }

    if not bad:
        print('all tags in all entries recognized')
        exit(0)

    print('unrecognized tags found')
    for word, tag in bad:
        print(tag, 'in', word)
    exit(1)
