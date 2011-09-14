Obtaining OpenERP with bzr_set.py
=================================

Execute bzr_set with the version you wish to use::

    python bzr_set.py -v 6.0

The version can be '5.0', '6.0' or 'trunk' for the bleeding-edge next release.

It will automatically:
* Download the appropriate source code branches
* Setup modules in your server as symbolic links


All symbolic links are set in the server at this point, so you can run it directly.
