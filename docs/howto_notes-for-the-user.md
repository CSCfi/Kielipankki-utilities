# How to create notes for the user
If issues are found in the data, whether they originate from the source data or were inadvertently generated during processing, the user should be informed.
In case the note would be just one sentence, it can be added to the desription of the corpus in META-SHARE directly.

In more complex cases, a portal page with name "shortname: Notes for the user" should be created, to collect all information about found issues for a particular resource.
 - create a portal page with path /corpora/shortname/notes (placed under the resource group page)
 - request a PID, see [docs: how to request a PID](howto_request_pid.md) (in most cases an English version of the notes should be sufficient)
 - add the PID, a link to the resource group page in question and a link to the relevant resource in META-SHARE to the portal page
 - describe the issues for the user
 - link to this page from META-SHARE under documentation with name "short name: Notes for the user"


## Creating a reference "shortname: Notes for the user" in META-SHARE
- In META-SHARE, start editing the metadata record of a resource on which a given notes' page should be applied.
- Under the ”Recommended” section, create a new Documentation item as a ”documentInfoType”.
- Select Document type: Other.
- Type the Title in the style ”klk-fi: Notes for the user” and set the language of the title as English.
- If relevant, insert a Finnish translation of the Title in the style ”klk-fi: Huomautuksia käyttäjälle” and set the language of this title as Finnish.
- In the URL field, insert the URN of the English version of the notes' page (NB: use the complete link here, starting with ”http://urn.fi/”).
- Set the Editor of the note as ”FIN-CLARIN” (this is optional, but the link may look funny on META-SHARE without setting an ’author’ or ’editor’).
- When creating a new version in the same resource group, and the issues on the notes' page apply to this version as well, you can look for the existing link on META-SHARE. At the Documentation section, you can just start typing ”klk-fi: Notes” for instance, and META-SHARE will show the matching records in a while.


