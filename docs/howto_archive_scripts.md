# Archiving your conversion scripts
Your **conversion scripts** for creating the HRT should be preserved. It is recommended to upload them to GitHub. The place for your scripts is in '[Kielipankki-utilities](https://github.com/CSCfi/Kielipankki-utilities/tree/master/corp/)'. 

On Puhti, do 'git pull' to make sure your copy of the repository is up to date. Then change to the sub folder 'corp' and create a new folder for your corpus in here. Copy your conversion scripts to this folder.

The command for adding your scripts to the repository (from Kielipankki-konversio/corp/'your_corpus'/) is:

    git add .
    
With the following command you can check the git status:

    git status

Commit your changes:

    git commit
    
This will ask for a short description of your action (e.g. 'conversion scripts for 'corpus' added')
    
Finally you can push your changes:

    git push
    