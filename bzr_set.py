#!/usr/bin/python

import glob

# Subscribe here repositories you plan to use for your project

bzr_repository = {
	'server': 'bzr+ssh://fp-tinyerp@bazaar.launchpad.net/~openerp/openobject-server/trunk',
	'client': 'bzr+ssh://fp-tinyerp@bazaar.launchpad.net/~openerp/openobject-client/trunk',
	'addons': 'bzr+ssh://fp-tinyerp@bazaar.launchpad.net/~openerp/openobject-addons/trunk',
	'web': 'bzr+ssh://fp-tinyerp@bazaar.launchpad.net/~openerp/openobject-client-web/trunk',
#	'addons-extra': 'bzr+ssh://fp-tinyerp@bazaar.launchpad.net/~openerp/openobject-addons/trunk-extra-addons',
}

# Subscribe here links to modules you are interrested in

bzr_links = {
	'addons/*': 'server/bin/addons/',
}

#bzr_links = {
#	'addons/base_setup': 'server/bin/addons/',
#	'addons/product': 'server/bin/addons/',
#	'addons/hr': 'server/bin/addons/',
#	'addons/board': 'server/bin/addons/',
#	'addons/crm': 'server/bin/addons/',
#	'addons/account': 'server/bin/addons/',
#	'addons/stock': 'server/bin/addons/',
#	'addons/purchase': 'server/bin/addons/',
#	'addons/mrp': 'server/bin/addons/',
#	'addons/report_mrp': 'server/bin/addons/',
#	'addons/sale': 'server/bin/addons/',
#	'addons/board_manufacturing': 'server/bin/addons/',
#	'addons/delivery': 'server/bin/addons/',
#	'addons/profile_manufacturing': 'server/bin/addons/',
#}

# ---------------------- End of Project Configuration -------------

#
# Note: this script could be improved to include modules dependencies detection
#

import os
import optparse
from bzrlib.builtins import cmd_checkout, cmd_branch

for local,bzrdir in bzr_repository.items():
	print 'Checkout', bzrdir
	# TODO: improve this using a bzr call if possible
	if not os.path.isdir(os.path.join(local,'.bzr')):
		#cmd = cmd_checkout()
		#cmd.run(bzrdir, local, lightweight=True)
		cmd = cmd_branch()
		cmd.run(bzrdir, local)
	file(os.path.join(local,'.bzrignore'), 'wb+').write('*.pyc\n.svn\n.bzrignore\n')

for src2,dest2 in bzr_links.items():
	for src in glob.glob(src2):
		dest = os.path.join(dest2, os.path.basename(src))
		if not os.path.isdir(dest):
			os.symlink(os.path.realpath(src), dest)
		for local in bzr_repository:
			if dest.startswith(local):
				file(os.path.join(local,'.bzrignore'), 'ab+').write(dest[len(local):]+'\n')

