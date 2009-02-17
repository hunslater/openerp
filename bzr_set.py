#!/usr/bin/python

__all__ = ['update_openerp']

import os
import shutil
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

_VERSIONS = ('4.2', '5.0', 'trunk')

def update_openerp(dest_dir, version, lplogin=None, export=False, with_bi=False, verbose=False):
    """
        if lplogin == None -> make a branch instead of a checkout
        if export == True -> bzr export 
    """
    def log(msg):
        if verbose:
            print msg

    if version not in _VERSIONS:
        raise Exception('Unknown version')
    dest_dir = dest_dir or '.'
    with_bi = with_bi and version == 'trunk'

    branch = lplogin is None
    if branch:
        BASEURL = 'lp:'    
    else:
        BASEURL = 'bzr+ssh://%s@bazaar.launchpad.net/' % (lplogin,)

    bzr_repository = {
        'server': BASEURL + '~openerp/openobject-server/' + version,
        'client': BASEURL + '~openerp/openobject-client/' + version,
        'addons': BASEURL + '~openerp/openobject-addons/' + version,
        'addons-extra': BASEURL + '~openerp-commiter/openobject-addons/' + version + '-extra-addons',
        'web': BASEURL + '~openerp/openobject-client-web/' + version,
    }

    bzr_links = {
        'addons/*': 'server/bin/addons/',
    }

    if with_bi:
        bzr_repository['bi'] = BASEURL + '~openerp/openobject-bi/' + version


    if branch:
        cmd = {'new': lambda u, l: run_cmd('branch', u, l),
               'update': lambda u, l: run_cmd('pull', u, directory=l, overwrite=True),
        }
    else:
        cmd = {'new': lambda u, l: run_cmd('checkout', u, l, lightweight=True),
               'update': lambda u, l: run_cmd('update', l),
        }
    cmd['export'] = lambda u, l: run_cmd('export', l, u)

    msg = "%(status)s %(type)s of %(from)s into %(to)s"

    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    for local,bzrdir in bzr_repository.items():
        local = os.path.join(dest_dir, local)
        typ = ['checkout', 'branch'][branch]
        if export:
            if os.path.exists(local):
                shutil.rmtree(local)
            status = 'export'
            typ = 'sources'
        else:
            try:
                b = Branch.open(local)
                # FIXME check that the current workingDirectory is a branch or a checkout
                status = 'update'
            except NotBranchError:
                status = 'new'
        
        log(msg % {'status': status, 'type': typ, 'to': local, 'from': bzrdir})
                
        cmd[status](bzrdir, local)

    # Doing symlinks
    log('(Re)Computing Symbolic links...')
    for src2,dest2 in bzr_links.items():
        src2 = os.path.join(dest_dir, src2)
        dest2 = os.path.join(dest_dir, dest2)
        for src in glob.glob(src2):
            dest = os.path.join(dest2, os.path.basename(src))
            if not os.path.isdir(dest):
                os.symlink(os.path.realpath(src), dest)

    log('='*79)
    log('Sources of OpenERP have been installed. If you develop new features,')
    log('you can get more information on how to contribute to the project here:')
    log('\thttp://openerp.com/community-process.html')
    log('='*79)


if __name__ == '__main__':
    import optparse

    parser = optparse.OptionParser(description="Tool that allow you to get the last sources of openerp on launchpad", 
                                   usage="%prog [options] [directory]")
    parser.add_option('--checkout', dest='lplogin', help="Specify the launchpad login to make a checkout instead of a branch")
    parser.add_option('--export', dest='export', help='Make an export of the sources', action='store_true', default=False)
    parser.add_option('-v', dest="version", default="trunk", type="choice", choices=_VERSIONS, help="Specify the version to take")
    parser.add_option('--bi', dest="bi", action="store_true", default=False, help="Grab the BI if you choose the trunk version")
    parser.add_option('-q', '--quiet', dest='quiet', help='Suppress the output', action='store_true', default=False)

    opt, args = parser.parse_args()
    dest_dir = args and args[0] or '.'

    update_openerp(dest_dir, opt.version, opt.lplogin, opt.export, opt.bi, not opt.quiet)

