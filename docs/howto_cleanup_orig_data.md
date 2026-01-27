# How to clean up original data

## Requirements for downloadable data
Source data of a resource is offered in the download service of Kielipankki [http://www.kielipankki.fi/download](http://www.kielipankki.fi/download "http://www.kielipankki.fi/download").

The source data is offered as is, meaning that usually it is not changed by us, except for packaging the data (in zip files) in a suitable way. 

**NOTE:** All original data should be stored immediately after receiving and before making changes to them.

The original resource data, as to be offered in the Kielipankki's download service, should meet some requirements regarding their format ect.

Typical options for the format:

   - WAV, EAF (from Elan)
   - TXT, PDF (raw formats)
  
For detailed format recommendations, please see [FIN-CLARIN format recommendations](https://clarin.ids-mannheim.de/standards/views/view-centre.xq?id=FIN-CLARIN)

File names and folder names should be machine readable, which means to use only alphanumeric characters (a-z, A-Z, 0-9) and consistent delimiters like underscores (_) or hyphens (-), avoiding spaces and special symbols (#, %, &, *, ?, /) that confuse operating systems and software, ensuring files are easily searchable, sortable, and processable by scripts and other programs.

File and folder names should preferably be written in English.

The data should not include empty files, log files or tmp directories. 

Also, the data should not include any additionaly folders created by MAC (__MACOSX/).

Preferably, the resource provider takes care of transferring the data in the required form (*see instructions in the portal, to be created!*)

If this is not the case, we can either ask the resource provider to make the required changes to the data him/herself and transfer new data, or we can offer to change the data with his/her permission.

## Cleaning up the data for download
After savely storing the original data received from the resource provider, a copy of the data can be prepared for being offered in the download service.
1. Check that all data is received, as announced by the data provider
2. Check the data format (if the same data is offered in different formats, e.g. a spreadsheed in xlsx, csv and sav, leave out the file in not-supported format, here sav)
3. Remove empty files, log files ect.
4. Clean up file and folder names to a machine readable form, if necessary (For this the agreement of the resource provider is needed)

## Cleaning up file names and folder names
In case the given names of files and folders do not meet the above mentioned requirements, and the resource provider agrees that we make the changes, we will do the necessary changes on the copy of the data, which is prepared for being offered in the download service.

For changing folder names and names of single files, you can use the command 'mv':

    mv foldername_old foldername_new
    e.g.: mv 'Free Speech' Free_Speech
    
    mv filename_old filename_new
    e.g.: mv 'Sosiolingvistinen kyselylomake, suomessa asuvat verrokit_FI.pdf' Sosiolingvistinen_kyselylomake_suomessa_asuvat_verrokit_FI.pdf

For changing several files names in a batch, e.g. fix all files of the format wav, that have spaces in their names, you can use the following command:

    for f in *\ *.wav ; do mv "$f" ${f// /_} ; done

With the ‘echo’ option, you can first try out what changes will be made without actually implementing them:

    for f in *\ *.wav ; do echo mv "$f" ${f// /_} ; done

---
For checking out LINUX basic commands, please see [CSC's LINUX basics tutorial](https://docs.csc.fi/support/tutorials/env-guide/).
