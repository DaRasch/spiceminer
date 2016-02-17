#!/usr/bin/env python
#-*- coding:utf-8 -*-

from __future__ import print_function

import os
import re
import sys
import json
import logging
import itertools
import contextlib

if sys.version_info.major == 3:
    import urllib.request as urllib
else:
    import urllib2 as urllib

from operator import itemgetter


class URL2Path(object):
    def __init__(self, root_path, root_url, dct):
        name_url = dct['name']
        name_path = dct.get('substitute', name_url)
        self.name = name_path
        self.path = os.path.join(root_path, name_path)
        self.url = '/'.join([root_url, name_url])
        self.files = dct.get('files', [])
        dirs = dct.get('dirs', [])
        self.dirs = [URL2Path(self.path, self.url, d) for d in dirs]

    @classmethod
    def fromjson(cls, root_path, filepath):
        with open(filepath, 'rt') as f:
            source = json.load(f)
        root_url = source['root']
        return [cls(root_path, root_url, dct) for dct in source['dirs']]

    def walk(self, urls=False):
        if urls:
            yield self.url, self.path, [d.name for d in self.dirs], self.files
        else:
            yield self.path, [d.name for d in self.dirs], self.files
        for d in self.dirs:
            for item in d.walk(urls):
                yield item

    def populate(self):
        for url, path, _, files in self.walk(urls=True):
            # Build folder structure
            try:
                os.mkdir(path)
                print('Created folder {}'.format(path))
            except Exception as e:
                logging.debug(str(e))
            # Ignore folders without files
            if not files:
                continue
            print('Updating {}'.format(path))
            # Load metadata
            print('Loading metadata')
            try:
                with open(os.path.join(path, 'metadata.json'), 'rt') as f:
                    meta_old = json.load(f)
            except Exception as e:
                logging.debug(str(e))
                meta_old = {}
            # Update files
            meta_new = {}
            for file_regex in files:
                try:
                    file_name, metadata = update_file(path, url, file_regex, meta_old)
                    meta_new[file_name] = metadata
                except Exception as e:
                    logging.error(str(e))
            # Store metadata
            try:
                with open(os.path.join(path, 'metadata.json'), 'wt') as f:
                    json.dump(meta_new, f)
            except Exception as e:
                logging.error(str(e))


def update_file(folder_path, url, regex, meta):
    def find_local(name_regex, meta):
        matches = (re.match(name_regex, file_name) for file_name in meta)
        matches = (item.group() for item in matches if item is not None)
        matches = [item for item in matches if item in meta]
        if len(matches) > 1:
            msg = 'Regex {} found too many matches.'
            raise ValueError(msg.format(name_regex))
        elif len(matches) == 1:
            old_file = matches[0]
            old_meta = meta[old_file]
        else:
            old_file = ''
            old_meta = {}
        return old_file, old_meta

    def find_internet(name_regex, url):
        REGEX_TIME = '[0-9a-zA-Z -]*:[0-9]*'
        REGEX_JUNK = '[a-zA-Z<> =/"]*'
        REGEX_SIZE = '[0-9\.]*[kKmMgGtT]'
        DT_FORMAT = '%d-%b-%Y %H:%M'
        regex = '(?P<name>{0}){3}(?P<time>{1}){3}(?P<size>{2})'
        regex = regex.format(name_regex, REGEX_TIME, REGEX_SIZE, REGEX_JUNK)
        response = urllib.urlopen(url)
        with contextlib.closing(response):
            page = response.read().decode('utf-8')
        matches = re.finditer(regex, page)
        matches = (item.groups() for item in matches)
        matches = sorted(matches, key=itemgetter(1), reverse=True)
        try:
            new_file = matches[0][0]
            new_meta = dict(zip(('time', 'size'), matches[0][1:]))
        except IndexError:
            msg = 'Unable to find entry for {}'
            raise ValueError(msg.format(name_regex))
        return new_file, new_meta

    old_file, old_meta = find_local(regex, meta)
    old_path = os.path.join(folder_path, old_file)
    new_file, new_meta = find_internet(regex, url)
    new_path = os.path.join(folder_path, new_file)
    new_url = '/'.join([url, new_file])
    if not old_file:
        print('{} does not exist'.format(new_file))
        print('Creating {}'.format(new_file))
        print('Downloading {}'.format(new_meta['size']))
        download(new_url, new_path)
    elif new_meta['time'] > old_meta['time']:
        print('{} is out of date'.format(old_file))
        if new_file != old_file:
            print('{} changes to {}'.format(old_file, new_file))
        print('Updating {}'.format(new_file))
        os.remove(old_path)
        print('Downloading {}'.format(new_meta['size']))
        download(new_url, new_path)
    print('{} is up to date'.format(new_file))
    return new_file, new_meta

def download(url, path):
    response = urllib.urlopen(url)
    with contextlib.closing(response):
        with open(path, 'wb') as f:
            f.write(response.read())

def main(path, files, names, lst=False):
    path = os.path.join(path, 'data')
    # Collect sources
    sources = (URL2Path.fromjson(path, f) for f in files)
    sources = itertools.chain(*sources)
    sources = {item.name: item for item in sources}
    # List parts
    if lst:
        print('Options:')
        for key in sources:
            print(' ', key)
        return
    # Make data dir
    try:
        os.mkdir(path)
    except Exception:
        pass
    # Load data
    if not names:
        names = sources.keys()
    for name in names:
        try:
            item = sources[name]
        except KeyError:
            msg = 'Parameter {} is invalid'
            raise ValueError(msg.format(name))
        item.populate()

if __name__ == '__main__':
    import argparse

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    #logging.basicConfig(level=logging.DEBUG)


    parser = argparse.ArgumentParser()
    parser.add_argument('data', nargs='*', metavar='DATA',
        help='The data to download (Default: all).')
    parser.add_argument('--dir', '-d', nargs=1, default=BASE_DIR, dest='path',
        help='Base directory for installation.')
    parser.add_argument('--list', '-l', default=False,
        help='List available options.')
    vargs = parser.parse_args()

    main(vargs.path, [os.path.join(BASE_DIR, 'data-naif.json')], vargs.data, vargs.list)
