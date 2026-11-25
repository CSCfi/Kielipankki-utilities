# How to create a table app with the app builder in WordPress 
With the help of the table app in WordPress we created table apps in order to be able to display the content of the resource data base on various portal pages.
These table apps are used to show the lists for all published corpora, all upcoming corpora, and they are used to display the list of corpora belonging to the various resource groups and resource families.
These instructions describe how a table app is created, maintained and used on a specific portal page.

## How to create a new table app
To be able to create a table app, you need to login to WordPress. 

Go to WP Data Access and open the App Builder.

The steps to create a filtered table are approximately:

1. Create a new app in the app builder, filling in the basic text fields as you please. 
   The table/view should be corpora_frontend, and you need to select all the columns you 
   want to display as well as the columns you want to use for filtering / constructing computed fields
   (the choice can be changed later under 'Manage')
   
2. Run & build app, and enter the setup via the crossed tools icon (tooltip "table builder", 
   they use the same icon for two different functions in different views, which is a bit confusing): 
   the interesting stuff is under "columns" in the hamburger menu. 
   NB: you can also access this from the page the table is embedded to, which is pretty handy when 
   trying to figure out why things don't work
   
3. Hide the columns you don't want to display (eye icon)

4. Add the desired computed fields, with whatever you want to display, such as `<a href={:url}>{:group_name}</a>` 
  (to use html, you need to expand the column settings and enable "Allow inline HTML" under column settings)
   NB: With the help of the 'wand' icon you can easily enter the correct column names here.
     
5. Switch to the table settings (under the same hamburger menu you found the columns from), and add a "default where" clause. 
   Example: For BYU, we want to filter by other_information, so the clause should be 
   `where other_information = shortcodeParam['other_information']`
   
6. Embed the table to a page: for BYU the shortcode would be something like 
   `[wpda_app app_id="4" other_information="english-corpora.org"]` 
   (with the correct app_id of course: you can see it in the list in the app builder front page and copy the shortcode 
   (without the other_information parameter) from the three-dot button.)
   

You can set `hidetitlebar="true"` in the shortcode to hide the black bar on top of the table.


## How to adjust an existing table app

An existing table app can be managed either with the link 'Manage' after the table name or with the cockwheal on the right-hand side of the display.
Here you can select the columns you want to display as well as the columns you want to use for filtering / constructing computed fields. You can also remove columns from the choice.

An existing table app can be adjusted with the link 'Run & Build' after the table name or on the right hand side with the tools icon.
This function is also accessable (via the same icon) from a portal page the table is embedded to, if the title bar is not hidden.
It is handy to create a test page (as draft), embed the table app in question (with title bar shown) and fine-tune it directly. 
The changes will be saved to the table app and will therefore be available on all pages, where the table app is used. Usually the page (table) has to be reloaded to show the latest changes.


## How the table app is used in the portal
For the Kielipankki portal we have created three table apps: one table for each language used in the portal (en, fi, sv), 
and then use filters for other_information, corpus_status, group_name and so on, with the default "show_all".
The code under 'Default Where' can be updated with more filters if needed.

Each table app has an id: 
corpora_en (App ID: 4) for English, corpora_fi (App ID: 5) for Finnish and corpora_sv (App ID: 6) for Swedish 

The table app for Swedish is a copy of the English one and not yet adjusted. 
It can be used on Swedish portal pages already, but will show the table content in English.



Example for shortcodes used with different filter values:

This table shows all corpora belonging to the ecorg group.

[wpda_app app_id="4" hidetitlebar="true" other_information="english-corpora.org" corpus_status="production" group_name="show_all" clarin_resource_family_en="show_all"]



This table shows all upcoming corpora.

[wpda_app app_id="4" hidetitlebar="true" other_information="show_all" corpus_status="upcoming" group_name="show_all" clarin_resource_family_en="show_all"]



This table shows all published corpora.

[wpda_app app_id="4" hidetitlebar="true" other_information="show_all" corpus_status="production" group_name="show_all" clarin_resource_family_en="show_all"]



This table shows published corpora of group ylenews, resource family 'Newspaper corpora'

[wpda_app app_id="4" hidetitlebar="true" other_information="show_all" corpus_status="production" group_name="ylenews" clarin_resource_family_en="%Newspaper corpora%"] 


## Filters
To use filters in your table app, you have to add a 'DefaultWhere' clause.
To do this, go to the table settings (under the same hamburger menu you found the columns from), and add a "default where" clause with all the required filters.

This is the current 'Default Where'-expression used in the Kielipankki table apps:

where (other_information = shortcodeParam['other_information'] OR
 shortcodeParam['other_information']='show_all') AND 
  (group_name = shortcodeParam['group_name'] OR
 shortcodeParam['group_name']='show_all') AND
corpus_status = shortcodeParam['corpus_status'] AND
(clarin_resource_family_en LIKE shortcodeParam['clarin_resource_family_en'] OR
 shortcodeParam['clarin_resource_family_en']='show_all')

The resources are filtered by the field 'other_information' (which is used to gather resources of a certain type, e.g. 'english-corpora.org', or 'eduskunta'),
group name, corpus status (production or upcoming) and resource family. The value 'show_all' must be defined so that all resources can be displayed, regardless of a specific filter value. 
Please note that 'show-all' is not defined for the 'corpus status'. A value (either 'production' or 'upcoming') must therefore always be specified here.


## Computed field definitions
Computed fields come in two types, either as computed text field or as computed code field. 
For a Computed Text Field, the expression contains text or HTML. For a Computed Code Field, the expression must be a valid JavaScript expression. 
Both types may contain placeholders. Clicking the wand icon opens a drop-down list of available column placeholders. You can also add them by typing their names directly.
Inline HTML is supported in both computed field types, whereas for a computed code field the type has to be set to 'code'. 


### Computed text fields
 
Computed field definition (HTML):
In this example the content of field 'location' will be shown with a hyper link referring to the access location.

<a href={:access_urn}>{:location}</a>


The citation instruction popups can be created via the app builder tables! 
The HTML code that needs to be added into the relevant column is this:
<a target="popup" onclick="window.open('https://www.kielipankki.fi/viittaus/?key={:metadata_urn}', '_blank', 'width=760,height=600')"><i class="fa fa-quote-right fa-1x" title="How to cite"><span style="color: transparent; display: none;">icon-quote-right</span></i></a>

<a target="popup" onclick="window.open('https://www.kielipankki.fi/viittaus/?key={:metadata_urn}&lang=fi', '_blank', 'width=760,height=600')"><i class="fa fa-quote-right fa-1x" title="Viittausmuoto"><span style="color: transparent; display: none;">icon-quote-right</span></i></a>


### Computed code fields

Computed field definition as code (NB: the field needs to be "Code", not "Text HTML" for this kind of definition),
In this example the content of 'license' will be shown as an icon (PUB, ACA, RES) with link to the respective license URN, when the status of the license is 'available'.
If the status is anything else, no content will be shown for 'license' at all.

(()  => {
  if ("{:license_status}" != "available") {
    return "";
  }
  if ("{:license_urn_en}".includes("urn.fi/urn:nbn:fi")) {
    return `<a href="{:license_urn_en}">
    <img
      src="/wp-content/uploads/2015/08/{:clarin_category_label}-1.png"
      alt="{:clarin_category_label}" width="50"></a>`;
  } else {
    return "";
  }
})()


For more information about Computed Fields in the WP App Builder see https://docs.rad.wpdataaccess.com/table-builder/menu/columns/computed-fields.html