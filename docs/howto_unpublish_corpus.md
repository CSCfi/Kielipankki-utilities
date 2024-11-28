# How to unpublish a resource

## When is it necessary?
   * When the license of a resource expires or if the license was revoked by the rightholder, the resource must be removed from Kielipankki's services. Examples: 'Triangle of Aspects Analysis of Frozen' (http://urn.fi/urn:nbn:fi:lb-2019022701), or the fulltext versions of the Finnish News Agency Archive (http://urn.fi/urn:nbn:fi:lb-2019041502)
   * A resource, or some of its versions, may also need to be archived, e.g., to save storage space, or because they have become deprecated.

## Task list for unpublishing a resource

Create a Jira Story with one of the following titles:
### _shortname_: Stage 1: Archive the version(s) XYZ in Kielipankki
### _shortname_: Stage 1: Remove the version(s) XYZ from Kielipankki

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
# [ ] _*+KORP*_ In case of a corpus published in Korp, remove the corpus from the Korp server and from the Korp corpus configuration.
# [ ] _*+PORTAL*_ On the resource group page, update the text describing which versions were (archived or) removed, when and why.
# [ ] _*+META*_ If some resource versions were removed completely, specify the 'Availability end date' (under Distribution) in their metadata records.
# [ ] _*?SUPPORT*_ If applicable, contact the depositor, the rightholder or the data controller, and politely inform them about the removal of the data.
# [ ] _*?ADMIN*_ Schedule and assign the next stage of the removal/archival process.
```

### _shortname_: Stage 2: Remove the version(s) XYZ from Kielipankki
### _shortname_: Stage 2: Archive the version(s) XYZ from Kielipankki

```
# [ ] _*+GITHUB*_ Re-direct the access location PID to the resource group page.
 # [ ] _*?SUPPORT*_ In case restricted corpus versions are to be archived or removed, send a reminder email to the users with a valid license 2 weeks before removing the data, stating the license terms, the reason and the schedule of removal.
 # [ ] _*+CSC*_ In case a  corpus is to be archived (to be available on request only, no longer promoted) or completely removed, create and assign an issue to CSC to create an archive copy of the data and to remove the data from the download service.
```

### _shortname_: Internally archive and remove the version(s) XYZ from Kielipankki (Download|Other)

```
(Deadline of removing the data: DD.MM.YYYY)
# [ ] _*+CSC*_ Create an archive copy of the downloadable data to IDA and freeze it (in the case of dataset removal, this is for internal emergency use only).
# [ ] *_?CSC_* In case restricted corpus versions are to be removed, ensure with the UHEL team that the end-users are sent a final reminder to remove their copy of the data about 2 weeks before the deadline.
# [ ] _*+CSC*_ Remove the restricted data and the corpus folder from the download server (by the deadline).
# [ ] _*+CSC*_ Inform the UHEL team about the completion of the removal/archival process and mention the address of the archival copy in IDA.
```

If applicable, add the following issue, to complete the removal process requested by the rightholder(s):

### _shortname_: Stage 3: Inform the depositor, the rightholder or the data controller about the removal of the data
```
# [ ] _*?DB*_ Ensure that the status of the corpus version and its license in the resource database are up to date.
# [ ] _*?META*_ Ensure that the access location points to the resource group page (with tombstone information).
 # [ ] _*?SUPPORT*_ If applicable, contact the depositor, the rightholder and/or the data controller, and politely inform them about the removal of the data.
```
