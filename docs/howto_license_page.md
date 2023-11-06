# Creating a license page in the portal
If adding a new version of an existing resource group, check if the previously existing license page (or one of them) covers the new resource version. If so, you can just insert the details of the new resource to the license page. Otherwise, you need to create a new license page in the portal. This page always has to be created in two language variants; in English and in Finnish.
The pages both need a PID (instructions on [how to request a PID](howto_request_pid.md)). From the META-SHARE record of this resource at least the English license page has to be referred to via its PID.

In order to create a license page in the portal, login at [kielipankki.fi/wp-admin](https://www.kielipankki.fi/wp-admin/). A VPN connection to the university is required. 
On Windows, you can use OpenVPNGUI -> Connect -> "hy". ("hu-tun" is not enough as it uses VPN only for University services).

License pages (and portal pages in general) can be created from scratch or using an existing page as a starting point (see also [How to create a license page in the portal](https://www.kielipankki.fi/intra/creating-license-pages/))

From scratch, if the license is included in the "standard" CLARIN PUB/ACA/RES licenses:

    - Choose "+ Uusi -> Sivu" from upper bar.
    - Choose "Sivun ominaisuudet -> Pohja: License template - generic" and "Yläsivu: lic" from right column.
    
From scratch, in cases where the license is a "special" one, or one of the public licenses, e.g., CC BY, whose original legal text is not curated by the Language Bank of Finland:

    - Look up the template draft pages (Finnish and English) of the corresponding under lic/ in the Portal, and copy each language version (let's call it "existing-page") into a new draft page (choose "Kopioi uudeksi luonnokseksi" from right corner of upper bar).
    - Don't forget to edit "Kestolinkki -> Polkutunnus". Otherwise the new page will be named "existing-page-2" or similar.
    - Update the title and the links in the header part of the license page according to the resource (group) in question:
        - Fill in "Resource name (EN)" and "Kielivaran nimi (FI)". (same as in META-SHARE)
        - Fill in "URN of resource" (see the persistent identifier in META-SHARE) and "Copyright holder" (= the right holder(s) in the deposition agreement, or the Licensor in META-SHARE).
    - NB: the URNs of each language version of the license will probably need to be redirected to point to the physical pages, e.g., https://www.kielipankki.fi/lic/uspenskij-4bat-fin instead of the dynamic address https://www.kielipankki.fi/lic/uspenskij-4bat/?lang=fi.

Using an existing page:

    - Go to a page you want to use (let's call it "existing-page") and choose "Kopioi uudeksi luonnokseksi" from right corner of upper bar.
    - Don't forget to edit "Kestolinkki -> Polkutunnus". Otherwise the new page will be named "existing-page-2" or similar.

Adding or modifying information for the license template:

    - Choose the correct license type.
    - Fill in "Resource name (EN)" and "Kielivaran nimi (FI)". (same as in META-SHARE)
    - Fill in "URN of resource" (see the persistent identifier in META-SHARE) and "Copyright holder" (= the right holder(s) in the deposition agreement, or the Licensor in META-SHARE).
    - Choose the appropriate "Tags: ID & Access", "Tags: Usage", and "Tags: Distribution".

Saving, previewing, and publishing a page:

    - From upper right corner, "Tallenna luonnos", "Esikatsele", or "Julkaise".


After having created the license page in English and in Finnish, request PIDs for both language variants. 
Link to (at least the English) license page via its PID from the META-SHARE record. 
