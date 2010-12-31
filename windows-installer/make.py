#!/usr/bin/python
"""
Copyright 2010 - Stephane Wirtel
"""
import argparse
import logging
import os
import shutil
import sys
import tarfile
import time
import tempfile
import urllib2
import urlparse
import glob

logging.basicConfig(level=logging.DEBUG,
                    format='[%(levelname)s] %(message)s',
                   )

from subprocess import Popen

PROJECTS = [
    'openerp-server',
    'openerp-client',
    'openerp-web',
]

OPENERP_NSIS = 'setup.nsi'
OPENERP_STATIC_DIR = 'static'
POSTGRESQL_MSI = os.path.join(OPENERP_STATIC_DIR, 'postgresql-8.3-int.msi')

def download(url, download_dir='.'):
    filename = urlparse.urlparse(url).path.split('/')[-1]
    assert filename

    download_dir = os.path.normpath(download_dir)
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    filename = os.path.join(download_dir, filename)
    logging.info('Downloading %s', url)

    infh = urllib2.urlopen(url)
    outfh = file(filename, 'wb')

    while True:
        data = infh.read(10000)
        if not data:
            break
        outfh.write(data)

    outfh.close()
    infh.close()

    return os.path.abspath(filename)

def uncompress_archive(archive, directory):
    logging.info('Decompressing %s', archive)
    tar = tarfile.open(archive)
    tar.extractall(directory)
    archive_directory = tar.getnames()[0]
    tar.close()

    return os.path.abspath(os.path.join(directory, archive_directory))

def get_current_version(url, directory='.'):
    filename_abs_path = download('%s/%s' % (url, 'CURRENT'), directory)
    current = file(filename_abs_path, 'r')
    version = current.read().strip()
    current.close()

    major_version, minor_version, tmp = version.split('.')
    tmp = tmp.split('-', 1)
    revision_version = tmp[0]
    build_version = None
    if len(tmp) > 1:
        build_version = ''.join(tmp[1:])

    return major_version, minor_version, revision_version, build_version

def create_working_directory(directory):
    if directory is None:
        directory = tempfile.mkdtemp(prefix='packaging',
                                     suffix=time.strftime('%Y-%m-%d'))

    if not os.path.exists(directory):
        os.makedirs(directory)
        logging.info('Creating directory: %s', directory)

    return os.path.abspath(directory)

def create_win32_packaging(args, build_directory, directories, version, version_str):
    makensis_arguments = [
        'makensis',
        '/DMAJOR_VERSION=%s' % version[0],
        '/DMINOR_VERSION=%s' % version[1],
        '/DREVISION_VERSION=%s' % version[2],
    ]

    if version[3]:
        makensis_arguments.append('/DBUILD_VERSION=%s' % version[3])

    makensis_arguments.append('setup.nsi')
    logging.debug('makensis: %r', makensis_arguments)

    py2exe_call = ['python', 'setup.py', 'py2exe']

    for project, project_directory in directories.iteritems():
        archive = "%s-setup-%s.exe" % (project, version_str)

        Popen(py2exe_call, cwd=project_directory).communicate()

        if project in ('openerp-server', 'openerp-web'):
            Popen(py2exe_call,
                  cwd=os.path.join(project_directory, 'win32')
                 ).communicate()

        Popen(makensis_arguments, cwd=project_directory).communicate()

        path_to_archive = os.path.join(project_directory, archive)
        logging.debug('path_to_archive: %r', path_to_archive)
        shutil.move(path_to_archive, build_directory)

    if args.allinone:
        allinone_directory = create_working_directory(os.path.join(build_directory, 'allinone'))
        logging.debug('allinone_directory: %s', allinone_directory)


        files_directory = create_working_directory(os.path.join(allinone_directory, 'files'))
        logging.debug('files_directory: %s', files_directory)

        for item in glob.glob(os.path.join(build_directory, '*.exe')):
            shutil.copy(item, files_directory)

        for item in (POSTGRESQL_MSI, OPENERP_NSIS, ):
            shutil.copy(item, allinone_directory)


        shutil.copytree(OPENERP_STATIC_DIR, os.path.join(allinone_directory, OPENERP_STATIC_DIR))

        Popen(makensis_arguments, cwd=allinone_directory).communicate()

        shutil.move(
            os.path.join(allinone_directory, 'openerp-setup-%s.exe' % version_str),
            build_directory
        )

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--allinone', action='store_true')
    parser.add_argument('-u', '--url', action='store', default='http://localhost/~stephane/openerp/stable')
    parser.add_argument('-d', '--directory', action='store')
    parser.add_argument('-n', '--nokeep', action='store_true')

    args = parser.parse_args()


    build_directory = ""
    try:
        build_directory = create_working_directory(args.directory)
        logging.info('Build Directory: %s', build_directory)

        version = get_current_version(args.url, build_directory)
        version_str = '.'.join(map(str, version[0:3]))
        if version[3]:
            version_str += '-%s' % version[3]
        logging.info('Version: %r', version_str)

        directories = dict()
        for project in PROJECTS:
            archive = "%s/%s-%s.tar.gz" % (args.url, project, version_str)
            filename_abs_path = download(archive, build_directory)
            archive_directory = uncompress_archive(filename_abs_path, build_directory)

            directories[project] = archive_directory

        create_win32_packaging(args, build_directory, directories, version, version_str)


    except Exception, exception:
        logging.exception(exception)
        if args.nokeep:
            shutil.rmtree(build_directory)

if __name__ == '__main__':
    main()
