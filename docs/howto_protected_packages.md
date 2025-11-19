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

- [Instructions for the researchers/depositors (draft)](https://www.kielipankki.fi/tuki/aineiston-toimitus-kielipankille/)
   
DELIVERY OPTION 1: The package can be delivered, e.g., via [Filesender](https://filesender.funet.fi/). It can then be downloaded to Puhti (via [Puhti web interface](https://www.puhti.csc.fi/)).

- The password should be delivered via another communication method, e.g., via SMS, to reduce risks. **Delivering the password via regular email is not recommended.**

DELIVERY OPTION 2: The researcher can hand the data over to a Kielipankki staff member on external disk.

- In case the researcher's disk is not password-protected, the disk must not be taken off the premises, i.e., the data must be copied by the Kielipankki staff member into an encrypted archive on site. The encrypted archive should then be stored at a trusted location for further processing.

DELIVERY OPTION 3: The researcher can make the encrypted package directly accessible to a Kielipankki staff member on a sufficiently secure service (as recommended by their home university) for sharing data.

## Encrypting and (re-)packaging the confidential data

On the HFST server, create a new password for this resource group (one password per resource group, should contain the short-name) and put it to the password store. In case a password for this resource group exists already, get it from the password store.

For instructions on how to create / retrieve a Kielipankki password, see [guidelines on how to manage Kielipankki passwords](https://github.com/CSCfi/Kielipankki-passwords/blob/master/howto_manage_corpus_passwords.md).

The next steps can be completed on your local device (i.e., work-related and well maintained laptop or the like), on the HFST server, or on the interactive shell on Puhti.

If the original dataset was encrypted by the researcher (with their password), unencrypt the data and create a new zip package, without a password. Then, using the resource group password, encrypt the data in a new wrapper package. The encrypted zip file then contains the un-encrypted zip file.

For naming conventions for the data packages see [guidelines for data storage](howto_data_storage.md).

## Transferring the confidential data to Puhti

If uploading data to Puhti, you must make sure that the data ends up in the user group `project_2013016` or, if required, in your private group/project.

On Puhti, start the process by changing to the user group `project_2013016` with command 
   
      $ newgrp project_2013016
   
If needed, create the target folder for the data on the project-specific scratch folder (or where the data is needed):

      $ mkdir /scratch/project_2013016/shortname

It is good practice to check the file permissions on the source folder before transfer. rsync and other file transfer tools can be set to keep the permissions on the target server, too. Ensure once again that the target folder on Puhti is only available to your current group/project.

For instance, to recursively set **read, write and execute** permissions of a given folder and its contents to the **user** (you) **and** **group**/project that currently owns the file, and to make sure **no permissions** are given **to** **others**, you could use

      $ chmod -R ug=rwx foldername

For file transfer in the command line, you may use [scp](https://docs.csc.fi/data/moving/scp/) or [rsync](https://docs.csc.fi/data/moving/rsync/). Rsync checks the difference between the source and target files and only transfers the parts that have changed, and it can be used to resume transfer after interruptions in the connection. Thus, it is good for transferring large files and for synchronizing folders.

Default suggestions for rsync [PLEASE COMMENT OR MODIFY IF THIS DOES NOT WORK!]:

      $ rsync -auzv sourcefoldername/ puhti.csc.fi:/scratch/project_2013016/shortname

The aforementioned rsync options will recursively copy all files from under 'sourcefoldername' to the folder 'shortname' on scratch. Data will be compressed in transit (to skip additional compression attempts, drop the 'z' option). Files that are newer on the target server will not be transferred or replaced. Files that exist at the target but not at the source are not removed. The permissions of the source files and folders are kept on the target.

If, after all your precautions, some files ended up in the wrong group (of which you are also a member) on Puhti, you can recursively change the group of the directory and the files under it (provided that you are the owner of the files and a member of the desired project):

      $ chgrp -R project_2013016 foldername

## Processing the data on Puhti

Start an [interactive shell](https://docs.csc.fi/computing/running/interactive-usage/) on Puhti. 
Again, select the project `project_2013016`.

Go to LOCAL_SCRATCH and create a folder for this resource.
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

The process for packaging confidential data is basically the same, only that the data will be enclosed in a password-protected wrapper.

**Before decrypting, the encrypted zip file (protected with Kielipankki's password) should be on a sufficiently secure server (preferably not Puhti). If you must use Puhti, use the interactive shell and maintain permissions for the restricted user group `project_2013016`.**

The steps are the following:

- unzip the wrapper package
- create a folder named 'shortname-src'
- create and arrange the desired folder structure, add README.txt and LICENSE.txt
- zip the data to shortname-src.zip
- Create an encrypted wrapper zip for this download package, using the password of the resource group.  
- **For password protection, you should select an appropriate cipher, probably e.g. AES-256.** (The default cipher in zip is said to be very weak.)
  
    You should use:
  - **7-Zip** on Windows,
  - e.g., **Keka** on Mac (or 7z in the command line),
  - **7z** (?) on unix/linux:
  
    7z a -p ???-mem=aes256??? -tzip "/shortname/shortname-src_encrypted.zip" "/shortname/shortname-src.zip"
    (UNTESTED! Please confirm the recommended "spell" from Martin! This should add files to archive, use a password, select cipher AES-256 and select zip as the archive type. – ML 20251119)
    
- You can then move the file shortname-src_encrypted.zip to the folder `download_preview` on Puhti.

- Tell CSC about the data in `download_preview`, to be uploaded to the download service. CSC staff will decrypt the data only after transferring it to the download service. (They will be able to locate the correct password by the resource's shortname.)

- Note: When closing the interactive shell, the data will no longer be available there (so no need to actively delete the data from there).



More information on how to publish a corpus in the download service:
[Kielipankki: corpus data publication for download at the language-bank](https://www.kielipankki.fi/development/corpus-data-publication-for-download-at-the-language-bank/)


## Preparing confidential data to be published in Korp

(INSTRUCTIONS TO BE ADDED)
