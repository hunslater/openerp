#!/usr/bin/python

# Subscribe here repositories you plan to use for your project

branch = True

if branch:
	BASEURL = 'lp:'	
else:
	BASEURL = 'bzr+ssh://christophe-simonis@bazaar.launchpad.net/'

bzr_repository = {
	'server': BASEURL + '~openerp/openobject-server/trunk',
	'client': BASEURL + '~openerp/openobject-client/trunk',
	'addons': BASEURL + '~openerp/openobject-addons/trunk',
#	'addons-extra': BASEURL + '~openerp/openobject-addons/trunk-extra-addons',
}

# Subscribe here links to modules you are interrested in

bzr_links = {
	'addons/*': 'server/bin/addons/',
}

# ---------------------- End of Project Configuration -------------

#
# Note: this script could be improved to include modules dependencies detection
#

import os
import glob
from bzrlib.builtins import cmd_checkout, cmd_branch
from bzrlib.plugins import launchpad

if branch:
	cmd = cmd_branch()
	args = {}
else:
	cmd = cmd_checkout()
	args = {'lightweight':True}

for local,bzrdir in bzr_repository.items():
	print branch and 'Branch' or 'Checkout', bzrdir, 'to' ,local
	# TODO: improve this using a bzr call if possible
	if not os.path.isdir(os.path.join(local,'.bzr')):
		cmd.run(bzrdir, local, *args)
	file(os.path.join(local,'.bzrignore'), 'wb+').write('*.pyc\n.*.swp\n.bzrignore\n')

for src2,dest2 in bzr_links.items():
	for src in glob.glob(src2):
		dest = os.path.join(dest2, os.path.basename(src))
		if not os.path.isdir(dest):
			os.symlink(os.path.realpath(src), dest)
		for local in bzr_repository:
			if dest.startswith(local):
				file(os.path.join(local,'.bzrignore'), 'ab+').write(dest[len(local):]+'\n')

