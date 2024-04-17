# How to unpublish a resource

## When is it necessary?
For example, when a license for a resource has expired, the resource has to be removed from Kielipankki's services.   
Example case: 'Triangle of Aspects Analysis of Frozen' (http://urn.fi/urn:nbn:fi:lb-2019022701).

## Steps for unpublishing
Metadata: 

- the access location has to be removed

- information has to be added to the description, e.g. 'This resource was previously available for download in Kielipankki - The Language Bank of Finland. However, *reason for removing the corpus*.'


GitHub:
- re-direct the access PID to the resource group page



Resource group page:
- remove the access link and instead put the information *not available anymore*

- edit description text and add information that the corpus is no longer available   
e.g. *Note: This resource was previously available for download in Kielipankki – The Language Bank of Finland. However, reason for removing the corpus*   		


Database: 
- set the resource to 'corpus removed' and add a comment about the reason for unpublishing
- check that the resource is not visible on the list of published corpora any longer


Portal:
- remove the resource from the list of resource families


Data:
- remove the data and corpus folder from the download server
- in case of a corpus published in Korp, remove the corpus from the Korp server and from the Korp corpus configuration



## Task list for unpublishing a resource
```
    [ ] _*+META*_ Remove the access location from the META-SHARE record 
    [ ] _*+META*_ Edit the description in META-SHARE to 'This resource was previously available for download in Kielipankki - The Language Bank of Finland.' together with an explanation for unpublishing.
    [ ] _*+GITHUB*_ Re-direct the access location PID to the resource group page 
    [ ] _*+PORTAL*_ Remove the access link from the resource group page and replace with 'not available anymore'
    [ ] _*+PORTAL*_ Add a note about the resource not being available anymore and the reason for unpublishing
    [ ] _*+DB*_ Change the status of the corpus to 'corpus removed' and add a comment about the reason for unpublishing. Check that the resource is not anymore visible on the list of published corpora.
    [ ] _*+PORTAL*_ Remove the resource from the list of resource families
    [ ] _*+PUHTI*_ In case of a downloadable corpus, remove the data and corpus folder from the download server
    [ ] _*+PUHTI*_ In case of a corpus published Korp, remove the corpus from the Korp server and from the Korp corpus configuration
```

