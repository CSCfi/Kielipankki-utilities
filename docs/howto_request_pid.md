# How to request a PID
Login to GitHub and open the page
[https://github.com/CSCfi/Kielipankki/tree/master/FIN-CLARIN-Administration](https://github.com/CSCfi/Kielipankki/tree/master/FIN-CLARIN-Administration) 

Below the file selection on this page you will find instructions on how to edit the file `lb_pid.txt`.
The file contains all our given PIDs. 
For editing the file you should use the mode 'no wrap'.
With CTRL-F you can search the file for the name of the resource in question. 
If the resource cannot be found, it does not have any PIDs yet and you can add them to the end of the file.
Format of a PID: the date of the day (yyyymmdd) + a running number, starting from 01.

Example for an entry in `lb_pid.txt` (PID and address):

	2021092407 https://www.kielipankki.fi/corpora/nlfcl/

Commit your changes and add a short comment about what you have done.

Run the PID-Generator under 'Registeröinti'. You will get a message created by the script, where you can find the words 'REGISTER OK' and 'update finished'.

NOTE: Your changes and additions will come into effect only the following day!

A resource usually needs PIDs for the following pages:

- META-SHARE article
- LICENSE in English
- LICENSE in Finnish
- location PID
- resource group page
