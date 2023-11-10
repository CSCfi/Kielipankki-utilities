#The Landing Page

##What is a landing page and when is it used

In the services of Kielipankki a landing page (or “stop over page”)  is a manually curated portal page, to which a PID has been assigned. For instructions on how to request a PID, see [docs: how to request a PID](howto_request_pid.md).

A landing page is used as a “stop over”, in order to provide the user of a corpus with additional information and then to refer him to the actual data or information, he is looking for.

One example is a landing page accessed by a resource PID that has pointed to data which is not available in its original form any longer. The changes are explained and the user is
directed further to the location of the corrected data. The landing page either gives access to the previously available data or it provides information on how to use the updated data to
get comparable results. In this case a landing page shares properties with a tombstone page. Both refer to data not directly available anymore. A tombstone page is used when it is hard or impossible to recreate the data.
(example for such a “stop over” page: Corpus of Finnish Magazines and Newspapers from the 1990s and 2000s, Version 1, http://urn.fi/urn:nbn:fi:lb-201711021)

In another case a landing page is used as a “stop over” to inform the user about a dual license of a corpus. In the META-SHARE record as well as the database the PID of the landing page is used as the license PID.
On the landing page the user gets all the necessary information about the dual license and he will be directed further to the individual licenses usuable for the resource in question.
The landing page as well as the individual license pages all get a PID, and preferably all these pages are created in Finnish and English. For instructions on how to create a license page, see [docs: how to license page](howto_license_page.md).
(example for a 'dual license' landing page: Finnish TreeBank 1, http://urn.fi/urn:nbn:fi:lb-2023103105)


##How to create a landing page with WordPress

In order to create a page in the portal, go to [Kielipankki.fi/wp-admin](https://www.kielipankki.fi/wp-admin/) (login with your university account, you need the VPN when working remotely).
It is possible to edit existing pages.
To create a new page, press 'uusi sivu'.
The first, bold text (document) will be the name of the page (link).
The following bold text will be the headline of the page.

The minimum content of a landing page is:

- The name of the resource in question and its PID
- A description of the reason for this landing page (changes of a corpus, dual license etc.)
- Reference(s) to the data the user is expecting after the “stop over” (e.g. access location of the data or license)
- A PID

A page created in Kielipankki can be put to 'privat' first. Then it is only visible to the author.

You can check the appearance of your page by pressing the 'preview' button.

Remember to choose the correct language of the page below. Then the other language options on the page are shown correctly.
Most of the Kielipankki portal pages are offered in English and Finnish.

After everything is done, the page should be put to 'public' and be published.

The page can be moved in the 'tree view' in the menu on the left (e.g. to the folder 'corpora'). This can also be done after publishing the page.


A landing page in the portal is usually located under the resource group page with the name 'pid-landing-oldPID', e.g. 'https://www.kielipankki.fi/corpora/ceal/pid-landing-2017022201/'.

A landing page created for a dual license could be located under the usual license of this resource, named after the resource shortname and the term 'dual-license', e.g. 'https://www.kielipankki.fi/lic/finntreebank-eng/finntreebank1-dual-license-eng/'.
