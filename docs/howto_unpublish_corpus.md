# How to unpublish a resource

## When is it necessary?
### When a license for a resource has expired or if it was revoked, the resource must be removed from Kielipankki's services. Example cases: 'Triangle of Aspects Analysis of Frozen' (http://urn.fi/urn:nbn:fi:lb-2019022701), or the fulltext versions of the Finnish News Agency Archive (http://urn.fi/urn:nbn:fi:lb-2019041502)
### A resource, or some of its versions, may also need to be archived, e.g., to save storage space, or because they have become deprecated.

## Task list for unpublishing a resource
```
# [ ] _*+DB*_ Move the removed versions to status 'archived' in the resource database, so they will not show up on the list of corpora, and add an internal comment including the date and reason for unpublishing.
# [ ] _*+PORTAL*_ In case of a restricted corpus, add an internal note in Katselmointiprosessi about the resource not being available anymore, including the date and the reason for unpublishing. LBR applications should no longer be processed.
# [ ] _*+META*_ Remove the access location from the metadata record, so that the record will no longer be listed on VLO.
# [ ] _*+META*_ Edit the metadata description to 'This resource was previously available for download in Kielipankki - The Language Bank of Finland.' Include a brief explanation for unpublishing. If applicable, mention the resource group page for further information.
# [ ] _*+GITHUB*_ Re-direct the access location PID to the resource group page.
# [ ] _*+PORTAL*_ On the resource group page, add a note about the resource not being available anymore, the archival/removal schedule and the reason for unpublishing. Mention if other versions of the resources will still remain available.
# [ ] _*?AGREEMENT*_ In case the removal was requested by the depositor, the rightholder or the data controller, contact them, inform them about the schedule of the removal process, and ensure politely that their decision was final (offer to update the deposition agreement).
# [ ] _*?PORTAL*_ If the license of some resource versions was revoked, add text to the option +OTHER, clearly stating the date when the license was revoked and the time after which the license will no longer be valid.
# [ ] _*?DB*_ If the license of some resource versions was revoked, specify the 'License Validity End Date'.
# [ ] _*?AGREEMENT*_ In case the archival/removal was initiated by the Language Bank, contact the original depositor of the resource and politely inform them about the reason and schedule of the archival/removal process (mentioning if other versions of the resource remain available).
# [ ] _*+CSC*_ In case a downloadable corpus is to be archived (to be available on request only, no longer promoted), create an archive copy of the downloadable data to IDA and freeze it.
# [ ] _*+PORTAL*_ Publish a news item about the resource not being available anymore, the archival/removal schedule, and the reason for unpublishing the resource.
# [ ] _*?LBR*_ In case restricted corpus versions are to be archived or removed, ask CSC for the current list of email addresses of the users with a valid license in LBR.
## [ ] _*?SUPPORT*_ In case restricted corpus versions are to be archived or removed, send an email announcement to the users with a valid license, stating the license terms, the reason and the schedule of removal/archival.
## [ ] _*?SUPPORT*_ In case restricted corpus versions are to be archived or removed, send another email announcement to the users with a valid license 2 weeks before removing the data, stating the license terms, the reason and the schedule of removal/archival.
# [ ] _*?KORP*_ In case of an important corpus published in Korp, add a notification in Korp about the removal schedule of the resource (e.g., 2 weeks in advance).
# [ ] _*?DB*_ When the removal time comes, if resource versions are to be removed completely, change their status into 'removed' in the resource database and add an internal comment including the date and reason for unpublishing. Check that the resource is not visible on the list of published corpora any longer.
# [ ] _*?DB*_ If the license of some resource versions was revoked, change the license status into 'needs_review' (unless an option 'revoked' is available!), to hide the license from users. If required, update the 'License Validity End Date'.
# [ ] _*+CSC*_ In case of a downloadable corpus is to be archived or removed, remove the data and corpus folder from the download server.
# [ ] _*+KORP*_ In case of a corpus published in Korp, remove the corpus from the Korp server and from the Korp corpus configuration.
# [ ] _*+PORTAL*_ On the resource group page, update the text describing which versions were (archived or) removed, when and why.
# [ ] _*+META*_ If some resource versions were removed completely, specify the 'Availability end date' (under Distribution) in their metadata records.
# [ ] _*?SUPPORT*_ If applicable, contact the depositor, the rightholder or the data controller, and politely inform them about the removal of the data.
```

