#!/usr/bin/env python
import imp, os, shutil, subprocess, tempfile

from fabric.api import env, run, local, cd
from fabric.operations import put

# This should be updated every release

VERSION_MAJOR='6.0'
VERSION_FULL='%s.0-rc2'%VERSION_MAJOR

WINDOWS_IP='Stef@172.16.225.128'

# This should not be updated

BRANCHES = [
    ('addons','bzr+ssh://bazaar.launchpad.net/~openerp/openobject-addons/trunk'),
    ('client','bzr+ssh://bazaar.launchpad.net/~openerp/openobject-client/trunk'),
    ('server','bzr+ssh://bazaar.launchpad.net/~openerp/openobject-server/trunk'),
    ('web','bzr+ssh://bazaar.launchpad.net/~openerp/openobject-client-web/trunk'),
]

PROJECTS = [
    ('openobject-server', 'server', os.path.join('bin', 'release.py'), 'server_release.py.mako'),
    ('openobject-client', 'client', os.path.join('bin', 'release.py'), 'client_release.py.mako'),
    ('openobject-web', 'web', os.path.join('openobject', 'release.py'), 'web_release.py.mako'),
]

DIR_DIST = os.path.realpath('packaging')
if not os.path.exists(DIR_DIST):
    os.mkdir(DIST_DIR)

GLOB_TARBALL = 'openerp-*-%s.tar.gz' % VERSION_FULL
GLOB_WIN32 = 'openerp-*-setup-%s.exe' % VERSION_FULL

DIR_WEBSITE = os.path.join('/', 'var', 'www', 'www.openerp.com', 'www', 'download')
DIR_SOURCE = os.path.join(DIR_WEBSITE, 'unstable', 'source')
DIR_WIN32 = os.path.join(DIR_WEBSITE, 'unstable', 'win32')

env.hosts = ['root@openerp.com']
env.show = ['debug']

def system(l):
    print l
    if isinstance(l,list):
        rc=os.spawnvp(os.P_WAIT, l[0], l)
    elif isinstance(l,str):
        tmp=['sh','-c',l]
        rc=os.spawnvp(os.P_WAIT, tmp[0], tmp)
    return rc

def update():
    """
    Make bzr pull on each branch
    """
    #system("[ -d .bzr ] || bzr init-repository .")
    for i in BRANCHES:
        if not os.path.isdir(i[0]):
            system(['bzr','branch',i[1],i[0]])
        else:
            system(['bzr','pull','-d',i[0],i[1]])
    system("cd addons; bzr revert -r 4148")
    system("rsync -av --delete --exclude .bzr/ --exclude .bzrignore --exclude /__init__.py --exclude /base --exclude /base_quality_interrogation.py addons/ server/bin/addons/")

def update_release_files():
    """
    Update the release files
    """
    from mako.template import Template as MakoTemplate
    for project in PROJECTS:
        release_file = os.path.join(os.path.abspath(project[1]), project[2])
        template_file = os.path.join(os.path.abspath('templates'), project[3])

        template = MakoTemplate(filename=template_file)
        file_pointer = open(release_file, 'w')
        file_pointer.write( template.render(VERSION=VERSION_FULL, MAJOR_VERSION=VERSION_MAJOR))
        file_pointer.close()
        print "release_file: %r" % release_file

def sdist():
    """
    Generate the sources
    """
    for project in PROJECTS:
        directory = os.path.abspath(project[1])
        cmd=['python', os.path.join(directory, 'setup.py'), 'sdist', '-d', os.path.abspath(DIR_DIST)]
        print cmd
        subprocess.Popen(cmd, cwd=directory).communicate()

def update_current():
    """
    Update the local CURRENT file with the new version
    """
    local('echo %s > %s' % (VERSION_FULL, os.path.join(DIR_DIST, 'CURRENT')))

def windows():
    system('rsync -av --delete --exclude .bzr/ --exclude .bzrignore ./ %s:openerp-packaging/'%WINDOWS_IP)
    system('ssh %s "cd openerp-packaging/windows-installer;make allinone;"'%WINDOWS_IP)
    system('rsync -av %s:openerp-packaging/windows-installer/files/ %s/ '%(WINDOWS_IP,DIR_DIST))

def upload_tar():
    """
    Upload the tarballs (source)
    """
    run('mkdir %s -p' % DIR_SOURCE)
    put(os.path.join(DIR_DIST, GLOB_TARBALL), DIR_SOURCE)

def upload_win32():
    """
    Upload the Windows Installers
    """
    run('mkdir %s -p' % DIR_WIN32)
    put(os.path.join(DIR_DIST, GLOB_WIN32), DIR_WIN32)

def upload():
    """
    Upload the Windows Installer and the tarballs
    """
    update_current()
    upload_tar()
    upload_win32()

def update_planets():
    """
    Update the planets (openerp, openobject)
    """
    run('/var/www/www.openerp.com/planet/upd-planet.sh')
    run('/var/www/www.openobject.com/planet/upd-planet.sh')

def make_all():
    update()
    update_release_files()
    sdist()
    update_current()
    #upload()

