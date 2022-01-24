# Creating a license page in the portal
A resource with restricted access rights (ACA or RES) needs to have a separate license page in the portal. This page always has to be created in two language variants; in English and in Finnish.
The pages both need a PID (instructions on [how to request a PID](howto_request_pid.md)). From the META-SHARE record of this resource at least the English license page has to be referred to via its PID.

In order to create a license page in the portal, login at [kielipankki.fi/wp-admin](https://www.kielipankki.fi/wp-admin/). A VPN connection to the university is required. 
On Windows, you can use OpenVPNGUI -> Connect -> "hy". ("hu-tun" is not enough as it uses VPN only for University services).

License pages (and portal pages in general) can be created from scratch or using an existing page as a starting point.

From scratch:

    - Choose "+ Uusi -> Sivu" from upper bar.
    - Choose "Sivun ominaisuudet -> Pohja: License template - generic" and "Yläsivu: lic" from right column.

Using an existing page:

    - Go to a page you want to use (let's call it "existing-page") and choose "Kopioi uudeksi luonnokseksi" from right corner of upper bar.
    - Don't forget to edit "Kestolinkki -> Polkutunnus" in the in the right column. Otherwise the new page will be named "existing-page-2" or similar.

Adding or modifying information for the license template:

    - Choose the correct license type.
    - Fill in "Resource name (EN)" and "Kielivaran nimi (FI)". (same as in META-SHARE)
    - Fill in "URN of resource" (see META-SHARE) and "Copyright holder".
    - Choose the appropriate "Tags: ID & Access", "Tags: Usage", and "Tags: Distribution".

Saving, previewing, and publishing a page:

    - From upper right corner, "Tallenna luonnos", "Esikatsele", or "Julkaise".


After having created the license page in English and in Finnish, request URNs for both language variants. 
Link to (at least the English) license page via its URN from the META-SHARE record. 
