#!/usr/bin/python


# Subscribe here repositories you plan to use for your project

bzr_repository = {
	'server': 'bzr+ssh://fp-tinyerp@bazaar.launchpad.net/~openerp/openobject-server/trunk',
	'client': 'bzr+ssh://fp-tinyerp@bazaar.launchpad.net/~openerp/openobject-client/trunk',
	'addons': 'bzr+ssh://fp-tinyerp@bazaar.launchpad.net/~openerp/openobject-addons/trunk',
	'web': 'bzr+ssh://fp-tinyerp@bazaar.launchpad.net/~openerp/openobject-client-web/trunk',
	'addons-extra': 'bzr+ssh://fp-tinyerp@bazaar.launchpad.net/~openerp/openobject-addons/trunk-extra-addons',
}

# Subscribe here links to modules you are interrested in

bzr_links = {
	'addons/*': 'server/bin/addons/',
}

# ---------------------- End of Project Configuration -------------

#
# Note: this script could be improved to include modules dependencies detection
#

import glob
import os
import optparse
from bzrlib.builtins import cmd_checkout, cmd_branch

for local,bzrdir in bzr_repository.items():
	print 'Branching', bzrdir
	if not os.path.isdir(os.path.join(local,'.bzr')):
		#cmd = cmd_checkout()
		#cmd.run(bzrdir, local, lightweight=True)
		cmd = cmd_branch()
		cmd.run(bzrdir, local)
	file(os.path.join(local,'.bzrignore'), 'wb+').write('*.pyc\n.svn\n.bzrignore\n')

# Doing symlinks

for src2,dest2 in bzr_links.items():
	for src in glob.glob(src2):
		dest = os.path.join(dest2, os.path.basename(src))
		if not os.path.isdir(dest):
			os.symlink(os.path.realpath(src), dest)
		for local in bzr_repository:
			if dest.startswith(local):
				file(os.path.join(local,'.bzrignore'), 'ab+').write(dest[len(local):]+'\n')

print
