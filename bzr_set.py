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

# ---------------------- End of Project Configuration -------------

#
# Note: this script could be improved to include modules dependencies detection
#

import os
import glob
import bzrlib.builtins
from bzrlib.plugins import launchpad
from bzrlib.branch import Branch
from bzrlib.errors import NotBranchError

def run_cmd(cmdname, *args, **kwargs):
    f = getattr(bzrlib.builtins, 'cmd_' + cmdname)()
    if hasattr(f, '_setup_outf'):
        # old versions of bzr does not have this function   
        # this function must be called to avoid a exception in bzr code
        f._setup_outf()
    return f.run(*args, **kwargs)

if branch:
    cmd = {'new': lambda u, l: run_cmd('branch', u, l),
           'update': lambda u, l: run_cmd('pull', u, directory=l, overwrite=True),
    }
else:
    cmd = {'new': lambda u, l: run_cmd('checkout', u, l, lightweight=True),
           'update': lambda u, l: run_cmd('update', l),
    }

msg = "%(status)s %(type)s %(to)s from %(from)s"

if not os.path.exists(dest_dir):
    os.makedirs(dest_dir)

for local,bzrdir in bzr_repository.items():
    local = os.path.join(dest_dir, local)
    
    try:
        Branch.open(local)
        # FIXME check that the current workingDirectory is a branch or a checkout
        status = 'update'
    except NotBranchError:
        status = 'new'
    
    print msg % {'status': status, 'type': ['checkout', 'branch'][branch], 'to': local, 'from': bzrdir}
            
    cmd[status](bzrdir, local)

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

