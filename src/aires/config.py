#!/usr/bin/env python

"""Reader and writer for JSON config files."""

import os
import glob
from json import loads, dumps
import re

re_comment = re.compile('\s*//')

def list(folder):
    if not os.path.isdir(folder):
        return []

    files = []
    for item in glob.glob(os.path.join(folder, '*.json')):
        item = re.sub(folder+'/', '', item)
        files.append(item)

    return files

def read(filename):
    """Read a JSON config file from disk.

    @param filename: The file to read."""

    fh    = open(filename, 'r')
    lines = fh.readlines()
    data  = []

    # Allow comments in the JSON data.
    for line in lines:
        if re.match(re_comment, line):
            continue
        data.append(line)

    return loads("".join(data))

def write(filename, data):
    """Write JSON configuration back to disk.

    @param filename: The file to be written to.
    @param data: Python data structure to be converted."""

    fh = open(filename, 'w')
    fh.write(dumps(data))
