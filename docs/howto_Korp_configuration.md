# Korp configuration
This part of the pipeline consists of making changes to the existing Korp configuration and translation files on your own branch of the Korp frontend repository and committing the changes.

You should have a folder ‘korp-frontend’ in your HOME directory in Taito shell, which is a Git working directory. 

Change to that directory:

    cd korp-frontend

You can create a new branch in GitHub, for example for a new corpus. This might be useful e.g. when working on several corpora at a time. Do the following (while in the master branch):

	git pull origin master 


With the following command you create a new branch and you already change to this new branch:

    git checkout -b your_new_branch master 



To change between existing branches:

	git checkout your_branch

You can check, in which branch you are right now:

	git branch
  
  
## Changing the configuration and translation files

Every time, before adding a new batch of corpus configurations, do (in your own corpus branch!):

    git pull origin master  

That merges the changes made to the master branch to your current committed changes. However, you shouldn't have uncommitted changes (at least not in the files that have been updated in the master branch, but Git will refuse to pull if you have). 

In order to create a configuration of your corpus, you should think about where to add the corpus in Korp: Which language is it? Is it a parallel corpus? Does it fit under a collection of corpora already available? Does the corpus have any access restrictions?

Add the corpus configuration of your corpus to the file `app/modes/default_mode.js` (for Finnish). See the configuration of other corpora, e.g. ‘yo_aineet’, for examples.
If needed, add common definitions to `app/modes/common.js` 
If needed, add translations to `app/translations/corpora-fi.json` for Finnish and the corresponding files for English and Swedish.
      
Commit your changes:

    git commit app/modes/default_mode.js

This asks for a commit message describing what you have done. It is recommended that the message has a single title line with preferably no more than 50 characters, optionally followed by a blank line and a more detailed description, with lines at most 75 characters long.

In case you changed several files at a time, you can commit all the changes together with 

    git commit . 
(ending in full stop)

This command will commit all changes at once, without naming the specific files.

In the commit message you should describe all changes you made to all files in question. It makes sense to commit multiple files at the same time, if the changes are closely related to each other, such as when adding to `common.js` a definition (or to `corpora-fi.json` a translation) of a term that is used in `default_mode.js`.

Push your changes to the main repository ("origin").

    git push origin your_branch
        

### Creating a test instance of Korp
Inform Jyrki, that you have pushed the changes. He will then create a test instance of Korp for your corpus, copy your corpus package (which you created earlier with 'korp-make') to the Korp server and install your configuration. When you did changes to an already existing test corpus, he will update the test instance for you.

### Testing the corpus in Korp

Check that

- Korp still works and doesn't hang to the startup logo
- the corpus shows up correctly in the Korp's corpus selector
- the information shown in the mouseover window are correct
- searching in the corpus seems to work correctly (extended search, look for a word, check the attributes under 'sana')
- the attribute values shown in the sidebar look correct (click on a searched word, check the sidebar)
- the word picture is working



It would be nice to have a common list of what should be tested for all text corpora.


### Debugging    
In case Korp gets stuck in reloading, you can try to open the Web browser's developer tools (`Ctrl-Shift-I` in at least Firefox and Chrome), reload the page and see what messages the console shows. You might want to ask Jyrki Niemi or Jussi Piitulainen for help.
