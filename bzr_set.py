#!/usr/bin/python

# TODO: take options on the command line : branch or checkout, version, lp login

import optparse

parser = optparse.OptionParser(description="tool that allow you to get the last sources of openerp on launchpad", usage="%prog [options] [directory]")
parser.add_option('--checkout', dest='lplogin', help="Specify the launchpad login to make a checkout instead of a branch")
parser.add_option('-v', dest="version", default="trunk", type="choice", choices=["4.2", "trunk"], help="Specify the version to take")
parser.add_option('--bi', dest="bi", action="store_true", default=False, help="Grab the BI if you choose the trunk version")

opt, args = parser.parse_args()
dest_dir = args and args[0] or '.'

# Subscribe here repositories you plan to use for your project
branch = opt.lplogin is None

if branch:
	BASEURL = 'lp:'	
else:
	BASEURL = 'bzr+ssh://%s@bazaar.launchpad.net/' % (opt.lplogin,)

bzr_repository = {
	'server': BASEURL + '~openerp/openobject-server/' + opt.version,
	'client': BASEURL + '~openerp/openobject-client/' + opt.version,
	'addons': BASEURL + '~openerp/openobject-addons/' + opt.version,
	'addons-extra': BASEURL + '~openerp-commiter/openobject-addons/' + opt.version + '-extra-addons',
	'web': BASEURL + '~openerp/openobject-client-web/' + opt.version,
}

# Subscribe here links to modules you are interrested in
bzr_links = {
	'addons/*': 'server/bin/addons/',
}

if opt.bi and opt.version == "trunk":
	bzr_repository['bi'] = BASEURL + '~openerp/openobject-bi/' + opt.version
	bzr_links['bi/addons/*'] = 'server/bin/addons/'

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
	cmd_args = {}
else:
	cmd = cmd_checkout()
	cmd_args = {'lightweight':True}

for local,bzrdir in bzr_repository.items():
	local = os.path.join(dest_dir, local)
	print branch and 'Branch' or 'Checkout', bzrdir, 'to' ,local
	# TODO: improve this using a bzr call if possible
	if not os.path.isdir(os.path.join(local,'.bzr')):
		cmd.run(bzrdir, local, **cmd_args)
	file(os.path.join(local,'.bzrignore'), 'wb+').write('*.pyc\n.*.swp\n.bzrignore\n')

# Doing symlinks

print '(Re)Computing Symbolic links...'
for src2,dest2 in bzr_links.items():
	src2 = os.path.join(dest_dir, src2)
	dest2 = os.path.join(dest_dir, dest2)
	for src in glob.glob(src2):
		dest = os.path.join(dest2, os.path.basename(src))
		if not os.path.isdir(dest):
			os.symlink(os.path.realpath(src), dest)
		for local in bzr_repository:
			if dest.startswith(local):
				file(os.path.join(local,'.bzrignore'), 'ab+').write(dest[len(local):]+'\n')

print
print 'Sources of OpenERP have been installed. If you develop new features,'
print 'you can get more information on how to contribute to the project here:'
print '\thttp://openerp.com/community-process.html'
print
