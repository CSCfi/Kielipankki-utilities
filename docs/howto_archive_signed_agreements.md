# Archiving the deposition agreement
Immediately after a deposition agreement has been signed (e.g., via UniSign), the full document including all the appendices should be safely stored for future reference.

## Save the document (from UniSign) as a single PDF file
Name the file as KP_yyyy_AINEISTO_shortname_yyyymmdd.pdf, where _yyyymmdd_ should correspond to the **date of the last signature** in the document.
Make sure all the signatures are included!

For the time being, identical copies of the document should be stored in three locations: 
  - IDA
  - the HFST server
  - in the contract register of the University of Helsinki.

## IDA
Upload the document under FIN-CLARIN Administration/agreements/shortname ([Go to IDA](https://ida.fairdata.fi/login))
  
After the data is successfully uploaded, you should freeze it. For this, press the 'snowflake' button in the user interface of IDA. Only the frozen data will be backed up!

Instructions on how to upload and download data to IDA can be found here: [IDA user guide](https://www.fairdata.fi/en/ida/user-guide/ "https://www.fairdata.fi/en/ida/user-guide/"). 
More information on how to freeze, see [IDA user guide](https://www.fairdata.fi/en/ida/user-guide/ "https://www.fairdata.fi/en/ida/user-guide/").

## HFST server
Transfer the pdf document to the **HFST server** (hfst-17.it.helsinki.fi) and place it under /data/corpora/agreements/shortname (ensure permissions for group!).
(If needed, create a subfolder named with the resource group shortname, in lowercase characters.)
Note that you need a VPN connection to the University of Helsinki to be able to access the HFST server. In order to be able to connect to Puhti from the HFST server, you can use e.g. sftp.


## Contract register (Sopimusrekisteri)

The University of Helsinki is usually the legal party representing Kielipankki. Via the contract register at UHEL, we make sure that the legal team at the University of Helsinki is able to refer to the existing agreements regarding Kielipankki when needed.

Currently, only some members of Kielipankki administrative staff have access and editing rights to the contract register (20240814: Mietta & Tommi). It is slightly cumbersome to get access permissions from the manager of the register, there is a learning curve, and the editors have read access to all contracts at UHEL. Therefore, editing permissions should not be requested unless needed on a regular basis.

In case you cannot login to the contract register, update the relevant details to the following document, and then reassign the Jira issue to Mietta or Tommi:
[Agreement metadata for the contract register] (https://helsinkifi-my.sharepoint.com/:x:/r/personal/lennes_ad_helsinki_fi/Documents/Kielipankin%20sopimusasiat/Sopimusrekisteri.xlsx?d=w061756453b6b4bcfad9c8c8d9ff52918&csf=1&web=1&e=tg8HUc)

### How to use the contract register:

[Login to the contract register] (https://sopimus.helsinki.fi/)

From the list of folders on the left, open "H402 Digitaalisten ihmistieteiden osasto" under "H40 Humanistinen tiedekunta".

1. On the top left corner, select **Tee** > **Uusi dokumentti** > **Tallenna tiedosto**.

Add the PDF file including the signed agreement and click on **Lataa tiedosto uuteen dokumenttiin**.

2. Fill in the required information, according to the agreement in question.

  - **Nimi:** For regular deposition agreement regarding Kielipankki resources, name the document as "Kielipankki yyyy Aineistosopimus: shortname(s)", where "yyyy" is the year of the latest signature in the agreement. (For other types of agreements, modify the document title as you see fit, e.g., "Kielipankki/LAREINA yyyy Tietojenkäsittelysopimus/Puhelahjat: Company Name".)
  - **Julkisuusaste:** Select "Julkinen" (=public). Normally, there are no confidential parts in our deposition agreements. The "degree of publicity" means that if someone from outside the University asks the University to disclose information regarding the documents, we state that we have not identified any particular legal reason why we should keep this particular agreement as a secret. (In general, personal or confidential details should be avoided in agreements.) By default, all documents in the contract register are accessible by other users of the register, but specific documents can be protected. Their metadata are still shown to everyone on the system.
  - **Sopimustyyppi:** Select "Immateriaalioikeudet" for regular deposition agreement.
  - **Sopimuksen omistajan koodi:** Write "HY001" for Helsingin yliopisto.
   - **Sopimuskumppani(t):** Add the University of Helsinki ("Helsingin yliopisto" in the list, use wildcards in search, e.g. "Hels*".) and all other parties that are mentioned in the agreement as either Rightholder (Oikeudenhaltija) or Data Controller (Rekisterinpitäjä). In case a party is not yet included in the list of parties (e.g., in the case of a private individual), add a new item ("Luo sopimuskumppani) which opens "Uusi dokumentti". In the case of a private individual as Firstname Lastname and include their ORCID identifier in "Kuvaus" (ORCID: xxxx-xxxx-xxxx-xxxx). Do not include any other personal data, as this data field is only there for searching purposes. In the case of an organization, copy paste the information from the agreement. ("Sopimuskumppanityyppikoodi" is not a required field.). Press "Tallenna".
  - **Sopimuksen allekirjoittaja(t):** Add the names of the people who actually signed the agreement (Firstname Lastname, Firstname2 Lastname2).
  - **Asiakirjan allekirjoituspäivämäärä:** Insert the date of the latest signature of the agreement.
  - **Voimassaolon alkamispäivämäärä:** Insert the date of the latest signature of the agreement (same as above).
  - In case the agreement is a temporary one, add **Voimassaolon päättymispäivämäärä:** and consider setting some notifications closer to the date when the agreement will no longer be valid (set "Jakelu:" with other recipients for reminders).
  - In special cases, check whether any other fields are relevant for this particular contract.
  - Save the agreement: **Tallenna**.
  
3. Finally, go back to the document list (by clicking "H402 Digitaalisten ihmistieteiden osasto") and set the agreement as currently valid: **Toiminnot >> Voimassa**.
