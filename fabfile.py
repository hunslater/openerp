#!/usr/bin/env python
from __future__ import with_statement

import os
import imp
import tempfile
import shutil

from fabric.api import env, run, local, cd
from fabric.operations import put

MAJOR_VERSION=6
MINOR_VERSION=0
REVISION_VERSION=0
BUILD_VERSION='rc2'

VERSION='%d.%d.%d' % (MAJOR_VERSION, MINOR_VERSION, REVISION_VERSION)
if BUILD_VERSION:
    VERSION='%s-%s' % (VERSION, BUILD_VERSION,)

SDIST_DIR = os.path.realpath('packaging')
if not os.path.exists(SDIST_DIR):
    print "The packaging directory doesn't exist - create it or change the directory in the fabfile"
    sys.exit()
TARBALL_PATTERN = 'openerp-*-%s.tar.gz' % VERSION
EXE_WIN32_PATTERN = 'openerp-*-setup-%s.exe' % VERSION
WORKING_DIRECTORY = os.getcwd()

PROJECTS = [
    ('openobject-server', 'server', os.path.join('bin', 'release.py'), 'server_release.py.mako'),
    ('openobject-client', 'client', os.path.join('bin', 'release.py'), 'client_release.py.mako'),
    ('openobject-web', 'web', os.path.join('openobject', 'release.py'), 'web_release.py.mako'),
]


DOWNLOAD_DIRECTORY = os.path.join('/', 'var', 'www', 'www.openerp.com', 'www', 'download')
REMOTE_DIRECTORY = os.path.join(DOWNLOAD_DIRECTORY, 'unstable')
SOURCE_DIRECTORY = os.path.join(REMOTE_DIRECTORY, 'source')
WIN32_DIRECTORY = os.path.join(REMOTE_DIRECTORY, 'win32')

env.hosts = ['root@openerp.com']

def show_version():
    """
    Make the version defined in this file and the release.py files
    """
    print "CURRENT: %r" % (VERSION)
    for project, project_directory, release_file, _ in PROJECTS:
        release = imp.load_source(release_file, os.path.join(project_directory, release_file))
        print "project: %r -- %r" % (project, release.version)

def update():
    """
    Make bzr pull on each branch
    """
    cmd="""
        #[ -d .bzr ] || bzr init-repository .;
        [ -d addons ] || time bzr branch bzr+ssh://bazaar.launchpad.net/~openerp/openobject-addons/trunk addons;
        [ -d client ] || time bzr branch bzr+ssh://bazaar.launchpad.net/~openerp/openobject-client/trunk client;
        [ -d server ] || time bzr branch bzr+ssh://bazaar.launchpad.net/~openerp/openobject-server/trunk server;
        [ -d web ] || time bzr branch bzr+ssh://bazaar.launchpad.net/~openerp/openobject-client-web/trunk web;
        bzr pull -d addons;
        cd addons; bzr revert -r 4148; cd ..
        bzr pull -d client;
        bzr pull -d server;
        bzr pull -d web;
        rsync --exclude .bzr/ -av addons/ server/bin/addons/
    """
    for i in cmd.split('\n'):
        print i
        os.system(i)

def sdist():
    """
    Generate the sources
    """
    from subprocess import Popen, call
    for project in PROJECTS:
        project_name = project[0]
        project_directory = project[1]

        directory = os.path.abspath(project_directory)
        print "project: %s - %s" % (project_name, directory,)
        Popen(['python', os.path.join(directory, 'setup.py'), 'sdist', '-d', os.path.abspath(SDIST_DIR)],
              cwd=directory).communicate()

def upload_tar():
    """
    Upload the tarballs (source)
    """
    run('mkdir %s -p' % SOURCE_DIRECTORY)
    put(os.path.join(SDIST_DIR, TARBALL_PATTERN), SOURCE_DIRECTORY)

def upload_win32():
    """
    Upload the Windows Installers
    """
    run('mkdir %s -p' % WIN32_DIRECTORY)
    put(os.path.join(SDIST_DIR, EXE_WIN32_PATTERN), WIN32_DIRECTORY)

def update_local_current():
    """
    Update the local CURRENT file with the new version
    """
    local('echo %s > %s' % (VERSION, os.path.join(SDIST_DIR, 'CURRENT')))

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
        file_pointer.write(
            template.render(VERSION=VERSION,
                            MAJOR_VERSION='%d.%d' % (MAJOR_VERSION, MINOR_VERSION)
                           )
        )
        file_pointer.close()
        print "release_file: %r" % release_file

def update_current():
    """
    Update the CURRENT file with the new version
    """
    run('echo %s > %s' % (VERSION, os.path.join(DOWNLOAD_DIRECTORY, 'CURRENT')))
    run('chown www-data:www-data %s -R' % DOWNLOAD_DIRECTORY)

def upload():
    """
    Upload the Windows Installer and the tarballs
    """
    upload_tar()
    upload_win32()
    update_current()

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
    update_local_current()
    update_current()
    #upload()

