#!/usr/bin/python

# Subscribe here repositories you plan to use for your project

bzr_repository = {
	'server': 'bzr+ssh://fp-tinyerp@bazaar.launchpad.net/~openerp/openobject-server/trunk',
	'client': 'bzr+ssh://fp-tinyerp@bazaar.launchpad.net/~openerp/openobject-client/trunk',
	'addons': 'bzr+ssh://fp-tinyerp@bazaar.launchpad.net/~openerp/openobject-addons/trunk',
#	'addons-extra': 'bzr+ssh://fp-tinyerp@bazaar.launchpad.net/~openerp/openobject-addons/trunk-extra-addons',
}

# Subscribe here links to modules you are interrested in

bzr_links = {
	'addons/base_setup': 'server/bin/addons/base_setup',
	'addons/product': 'server/bin/addons/product',
	'addons/hr': 'server/bin/addons/hr',
	'addons/board': 'server/bin/addons/board',
	'addons/crm': 'server/bin/addons/crm',
	'addons/account': 'server/bin/addons/account',
	'addons/stock': 'server/bin/addons/stock',
	'addons/purchase': 'server/bin/addons/purchase',
	'addons/mrp': 'server/bin/addons/mrp',
	'addons/report_mrp': 'server/bin/addons/report_mrp',
	'addons/sale': 'server/bin/addons/sale',
	'addons/board_manufacturing': 'server/bin/addons/board_manufacturing',
	'addons/delivery': 'server/bin/addons/delivery',
	'addons/profile_manufacturing': 'server/bin/addons/profile_manufacturing',
}

# ---------------------- End of Project Configuration -------------

#
# Note: this script could be improved to include modules dependencies detection
#

import os
from bzrlib.builtins import cmd_checkout

for local,bzrdir in bzr_repository.items():
	print 'Checkout', bzrdir
	# TODO: improve this using a bzr call if possible
	if not os.path.isdir(os.path.join(local,'.bzr')):
		cmd = cmd_checkout()
		cmd.run(bzrdir, local, lightweight=True)
	file(os.path.join(local,'.bzrignore'), 'wb+').write('*.pyc\n.svn\n.bzrignore\n')

for src,dest in bzr_links.items():
	if not os.path.isdir(dest):
		os.symlink(os.path.realpath(src), dest)
	for local in bzr_repository:
		if dest.startswith(local):
			file(os.path.join(local,'.bzrignore'), 'ab+').write(dest[len(local):]+'\n')

