Using the package scripts
=========================

Configure a Project
-------------------

To configure the bzr_set.py script for your project, change the header
and set:
* the links to the different bazaar branches you plan to use.
* the links of modules to put in the server of the project

When the script is configured for your project, run it:
* python bzr_set.py

It will automatically:
* Download Bazaar branches
* Set modules in your server as symbolic links


Using Your Project
------------------

All symbolic links are set in the server, so you can run it directly.
You can apply any modification you want.

To commit your changes, go to the appropriate bazaar branch and commit it.

As an example, if you downloaded:
* server
* client
* addons

You have to commit the 3 branches individually if you made changes everywhere.


Using With Subversion (for Tiny employees only)
---------------------

At Tiny, customers projects are managed through our internal subversion.
We store there all documents related to the project: documentation, meeting
documents, sales and quotations, ...

But all related code are published in the public bazaar on launchpad.

A typical structure would be:
/doc
/sprints
/meetings
/dev

You must download the code and the bzr_set.py script in the dev directory and
add a svn:ignore property so that the code do not enter in our internal
subversion and keeps being managed on the launchpad bazaar.

As a summary, to download a full customer project including docs and code, you
must:
* svn co CUSTOMER_PROJECT
* cd CUSTOMER_PROJECT/dev && python bzr_set.py


