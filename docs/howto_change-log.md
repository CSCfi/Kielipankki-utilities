# Non-significant Corpus Changes
A new version of a corpus is generated when the corpus’s content changes significantly. 
What constitutes a significant change is defined individually for each corpus. 
If the corpus description does not specify otherwise, such changes that may substantially affect research results or that are not easily reversible are considered significant. 

All **non-significant** changes are recorded in the change log in the corpus’s metadata.

## A CHANGE-LOG in the metadata record
A change log is added to the metadata record under the tab 'Resource documentation info', as an unstructured documentation. 

Further changes are added to the same documentation element. Each change entry is preceded by the current date.

Example for a CHANGE-LOG in the metadata record:

     CHANGE LOG:
     2023-05-10 Added the missing license condition +DEP, according to the original agreement. 
     2025-04-16: The rightholder changed from Aller Media Oy to City Digital Group for all versions of Suomi24. 

Examples of non-significant changes:

 - A single article in a large conversation corpus has to be removed at an informant’s request. In this case, providing the previous version would not be possible in the first place.
 - Some hand-written tags in a large corpus have been found to contain a typographical error.
 - A corpus has been automatically converted from Latin-1 to UTF-8 character encoding. The old encoding remains accessible in the archive.
 - Small changes in the corpus' name
 - Small changes to the license of a corpus (e.g. adding a missing license condition)
 - The Rightholder changed (e.g. due to company takeover)
 


## CHANGES.txt in DOWNLOAD
A non-significant change to an already published corpus in the download service, which leads to invalid or outdated content of its README.txt or LICENSE.txt file, can be documentend in a file **CHANGES.txt**.
The file is added to the download folder of the resource in question, next to the README and LICENSE files.
The existing README.txt and LICENSE.txt themselves are not changed.

This avoids having to repackage the data each time, as the README.txt and LICENSE.txt have the same content inside and outside the data packages.

Content of a file **CHANGES.txt**:

    CHANGE-LOG

    2025-04-14: The rightholder changed from Aller Media Oy to City Digital Group for all versions of Suomi24.

The content of this file can be extended by additional change log entries, similar to the CHANGE-LOG in the metadata record.
