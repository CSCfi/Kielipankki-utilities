# How to process password-protected packages
The source data of a resource as well as its VRT version are made available in the download service of Kielipankki [http://www.kielipankki.fi/download](http://www.kielipankki.fi/download "http://www.kielipankki.fi/download").
For further instructions on how to prepare data for being published in the download service, see [how to create a download package](howto_download_package.md).

General principles:

- The package containing confidential files should remain encrypted whenever possible, until the package is made available in the download service with the appropriate access restrictions. 

- The time of processing confidential data in unencrypted form should be minimized and the processing must only take place in the environments we have agreed to trust for this purpose.

- We can currently trust the HFST server, the interactive shell on Puhti, the local home directory on the user's work laptop (no network drives!) or the user's password-protected and encrypted external hard drive, given that the data are processed according to the instructions. 


## Receiving confidential data (RES +PRIV)

The delivery method must be explicitly agreed with the researcher/depositor providing the original data.

Packaging the data for delivery:

If possible, the researcher should provide us with a password-protected zip archive that includes the confidential data set in an unencrypted zip file. It is then easier for us to first decrypt the archive and then to re-encrypt it with another password for our internal use.

- To do: Create instructions in the Portal for the researchers/depositors
   
DELIVERY OPTION 1: The package can be delivered, e.g., via [Filesender](https://filesender.funet.fi/). It can then be downloaded to Puhti (via [Puhti web interface](https://www.puhti.csc.fi/)).

- The password should be delivered via another communication method, e.g., via SMS, to reduce risks.

DELIVERY OPTION 2: The researcher can hand the data over to a Kielipankki staff member on external disk.

- In case the researcher's disk is not password-protected, the disk must not be taken off the premises, i.e., the data must be copied by the Kielipankki staff member into an encrypted archive on site. The encrypted archive should then be stored at a trusted location for further processing.

DELIVERY OPTION 3: The researcher can make the encrypted package directly accessible to a Kielipankki staff member on a sufficiently secure service (as recommended by their home university) for sharing data.


## Storing confidential data

On the HFST server, create a new password for this resource group (one password per resource group, should contain the short-name) and put it to the password store. In case a password for this resource group exists already, get it from the password store.

For instructions on how to create / retrieve a Kielipankki password, see [guidelines on how to manage Kielipankki passwords](howto_manage_passwords.md).

The next steps can be completed on your local device (i.e., work-related and well maintained laptop or the like), on the HFST server, or on the interactive shell on Puhti:

If the original dataset was encrypted by the researcher (with their password), unencrypt the data and create a new zip package, without a password.

Using the resource group password, encrypt the data in a new wrapper package:

      $ zip -e shortname_date_orig.zip origdata_unencrypted.zip		

The encrypted zip file contains the un-encrypted zip file!

For naming conventions for the data packages see [guidelines for data storage](howto_data_storage.md).

If uploading data to Puhti, you must make sure that the data ends up in the user group `project_2013016` or, if required, in your private group.

On Puhti, start the process by changing to the user group `project_2013016` with command 
   
      $ newgrp project_2013016
   
Transfer the data to the folder /scratch/project_2013016/shortname (or where it is needed). Ensure that the target folder on Puhti is only available to your current group/project. For instance, to recursively set read, write and execute permissions to the current user (you) and your currently active group/project (but not for others), use

      $ chmod -R ug=rwx foldername

For file transfer in the command line, you may use [scp](https://docs.csc.fi/data/moving/scp/) or [rsync](https://docs.csc.fi/data/moving/rsync/). Rsync checks the difference between the source and target files and only transfers the parts that have changed, and it can be used to resume transfer after interruptions in the connection. Thus, it is good for transferring large files and for synchronizing folders.

Default suggestions for rsync [PLEASE COMMENT!]:

      $ rsync -auzv sourcefoldername/ targetserver:targetfoldername

The aforementioned rsync options will recursively copy all files from under 'sourcefoldername'. Data will be compressed in transit (to skip compression, drop the 'z' option). Files that are newer on the target server will not be transferred or replaced. Files that exist at the target but not at the source are not removed. The privileges of the source files and folders are kept.

Start an interactive shell on Puhti. Go to LOCAL_SCRATCH and create a folder for this resource.
There, decrypt the wrapper zip from the researcher with the help of his or her password.

Move the encrypted wrapper package from the interactive shell to the resource folder on scratch (group protected!)

Create a README to accompany the the original data, for instructions see [guidelines for data storage](howto_data_storage.md).

Upload the shortname_date_orig.zip and the README_shortname_date_orig.txt to IDA and HFST for storage.

For safety reasons, you might want to overwrite the original package before removing:

      $ echo "..." > original.zip
   
Remove the wrapper package original.zip, received from the researcher, from Puhti.

      $ rm -rf original.zip



## Preparing confidential data to be published in Download

For detailed instructions on how to prepare data for being published in the Kielipankki download service, see also [how to create a download package](howto_download_package.md)

The process for packaging confidental data is basically the same, only that the data will be enclosed in a password-protected wrapper.

The steps are the following:

- The encrypted (protected with Kielipankki's password) zip file is on Puhti, in a folder with rights for our own, limited, user group `project_2013016`.

- unzip the wrapper package to the interactive shell, LOCAL_SCRATCH

- create a folder named 'shortname-src'

- create the wanted folder structure, add README.txt and LICENSE.txt

- zip the data to shortname-src.zip

- Create an encrypted wrapper zip for this download package, using the password of the resource group:
 
        $ zip -e download_encrypted_shortname-src.zip shortname-src.zip

   The shortname-src.zip is un-encrypted inside the encrypted file download_encrypted_shortname-src.zip.

- move the download_encrypted_shortname-src.zip to the folder `download_preview` on Puhti.

- Tell CSC about the data in `download_preview`, to be uploaded to the download service. CSC staff will de-crypt the data (they will be able to detect the correct password by the resource's shortname!) only after transferring it to the download service.

- Note: When closing the interactive shell, the data will no longer be available there (so no need to actively delete the data from there).



More information on how to publish a corpus in the download service:
[Kielipankki: corpus data publication for download at the language-bank](https://www.kielipankki.fi/development/corpus-data-publication-for-download-at-the-language-bank/)


## Preparing confidential data to be published in Korp

TO BE EDITED
