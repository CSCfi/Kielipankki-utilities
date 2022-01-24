# Publish a corpus in Korp
The **corpus package**, created by running **korp-make**, has to be installed on the Korp server. If you do not have access rights to the Korp server, ask someone with the rights to do that. Instructions on how to create a corpus package by running korp-make can be found in [docs: how to korpmake](howto_korpmake.md).

The **corpus configuration** has to be added to Korp by making changes to the existing Korp configuration and translation files on the corpus-specific branch of the Korp frontend repository (Kielipankki-korp-frontend). For instructions on how to add a corpus configuration to Korp, see [docs: how to add a corpus configuration to Korp](howto_Korp_configuration.md). 


## Publish on a test instance of Korp
At first, the corpus configuration should be installed on a separate test instance of Korp. Jyrki Niemi takes care of this. Just let him know, when you pushed your changes of the Korp configuration and translation files in GitHub.

Example of a test instance of Korp:

    https://korp.csc.fi/korp-test/nlfcl-fi/#?corpus=nlfcl_fi


### Testing the corpus in Korp
Check that the corpus shows up and works as expected in the test instance of Korp. The corpus should be tested by at least one other person of the team. 

Check that

    - Korp still works and doesn't hang to the startup logo
    - the corpus shows up correctly in the Korp's corpus selector
    - the information shown in the mouseover window are correct
    - searching in the corpus seems to work correctly (extended search, look for a word, check the attributes under 'sana')
    - the attribute values shown in the sidebar look correct (click on a searched word, check the sidebar)
    - the word picture is working


### Informing others of the corpus and request feedback
After the test version works as expected, you should inform at least *fin-clarin(at)helsinki.fi* and the original corpus owner or compiler if applicable. In practice, rise this topic up in our team meeting to get info about whom to inform and decide who is going to test your corpus. If you get feedback, you might need to re-do some of the previous steps. 


## Publish on the production Korp
Once the corpus works as desired in the test version of Korp, it is ready to be installed on the production Korp. Jyrki Niemi takes care of the installation. Usually the corpus will be published as a **beta version** for approximately two weeks. If during this time someone notices problems and changes need to be done to the data, it will not be necessary to change the version of the corpus.

### Beta version
In order to publish the corpus as a beta version, you have to add information to the corpus configuration.
 
    - add the label 'beta' to the title of the corpus
    - add a fixed warning text to the description by adding to the corpus configuration:
      labels: [beta],

The METASHARE article for your corpus should be checked and possibly updated. Add the label 'beta' to the name of the corpus (e.g. *The Finnish sub-corpus of the Classics Library of the National Library of Finland - Kielipankki version (beta)*) and add the information '*available in Korp as a beta test version*' to the description. The access location (Korp URN) has to be added to the METASHARE article as well as to the Korp configuration, if not done earlier.
Add the corpus to the list of published resources (see [instructions](howto_maintain_resources_lists.md)) and add the label 'beta' to the corpus name.
Add the corpus to the resource group page (see [instructions](howto_resource_group_page.md)) and add the label 'beta' to the corpus name.
Create news in Korp, see [docs: how to create Korp news](howto_korp_news.md).
Create news in the portal, see [docs: how to create news in the portal](howto_portal_news.md) and always remember to add information about the status 'beta'.

If you haven’t heard of any requests for corrections or changes during a period of about two weeks, you can remove the beta status.

    remove the beta label from the Korp configuration
    remove 'beta' from the corpus name in META-SHARE and update the description to *is available in Korp*
	remove 'beta' from the corpus name on the resource group page
    remove 'beta' from the corpus name in the list of published resources

 



