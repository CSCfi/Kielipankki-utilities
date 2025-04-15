THIS IS UNDER CONSTRUCTION

# How to process password-protected packages
Source data of a resource as well as its VRT version can be offered in the download service of Kielipankki [http://www.kielipankki.fi/download](http://www.kielipankki.fi/download "http://www.kielipankki.fi/download").
Add link to howto_download_package.md

## Receiving confidential data (RES +PRIV)
The zip file should be encrypted all the time, until it ends up in the download service with RES protection.

The researcher should provide us with a password-protected zip file.
The un-encrypted zip file should be included within an encrypted zip file.
   
e.g. via Filesender, downloadable via Puhti web interface to Puhti

To do: Create instructions for the researchers

The password could be delivered via SMS, to have two different routes.



## Storing confidential data
On Puhti, start the process by changing to the user group `project_2013016` with command 
   
   $ newgrp project_2013016
   
Transfer the data to Puhti, to a folder with access rights restricted to the user group `project_2013016`.
If uploading data, make sure that the data ends up in your private group or in the user group `project_2013016`.

Start an interactive shell on Puhti. Go to LOCAL_SCRATCH and create a folder for this resource.
There, decrypt the wrapper zip from the researcher with the help of his or her password.
Create a new password and put it to the password store. In case a password for this resource group exists already, get it from the password store. 
For instructions on how to create / retrieve a Kielipankki password, see howto_manage_passwords.md.


Encrypt the wrapper package with Kielipankki's own password, the internal password of this particular resource group (one password per resource group, should contain the short-name).

   $ zip -e shortname_date_orig.zip origdata_unencrypted.zip		(The encrypted zip file contains the un-encrypted zip file !!)

For naming conventions see howto_data_storage.md

Move the encrypted wrapper package from the interactive shell to the resource folder on scratch (group protected!)

Create a README to accompany the the original data, for instructions see howto_data_storage.md.

Upload the shortname_date_orig.zip and the README_shortname_date_orig.txt to IDA and HFST for storage.

For safety reasons, you might want to overwrite the original package before removing:

   $ echo "..." > original.zip
   
Remove the wrapper package original.zip, received from the researcher, from Puhti.

   $ rm -rf original.zip



## Packaging confidential data

Packaging process: see also howto_download_package.md

- The encrypted (protected with Kielipankki's password) zip file is on Puhti, in a folder with rights for our own, limited, user group `project_2013016`.

- unzip the wrapper package to the interactive shell, LOCAL_SCRATCH

- create a folder named 'shortname-src'

- create the wanted folder structure, add README.txt and LICENSE.txt

- zip the data to shortname-src.zip

- Create an encrypted wrapper zip for this download package, using the password of the resource group:
 
     $ zip -e download_encrypted_shortname-src.zip shortname-src.zip   (the shortname-src.zip is un-encrypted inside the encrypted download_e_shortname-src.zip)

- move download_encrypted_shortname-src.zip to the folder `download_preview`.

- Tell CSC about the data in `download_preview`, to be uploaded to the download service.

- Note: When closing the interactive shell, the data will no longer be available there.






More information on how to publish a corpus in the download service:
[Kielipankki: corpus data publication for download at the language-bank](https://www.kielipankki.fi/development/corpus-data-publication-for-download-at-the-language-bank/)
