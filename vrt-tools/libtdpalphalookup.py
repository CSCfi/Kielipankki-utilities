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

    # Then a basic test, to be removed after testing.
    
    'testiä' : { ('testi', ('N', 'Sg', 'Par'))
    },
}
