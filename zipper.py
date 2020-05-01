#!/usr/bin/env python
# -*- coding: utf-8 -*-

import shutil
import os
import sys
import re

KODIDIR = os.path.dirname(os.path.realpath(__file__))
REPODIR = os.path.join(KODIDIR, 'repo')

if not os.path.isdir(KODIDIR):
    print('No kodi directory')
    sys.exit()

if not os.path.isdir(REPODIR):
    print('No repo directory')
    sys.exit()

jdirs = [os.path.join(KODIDIR, x) for x in os.listdir(KODIDIR)
    if os.path.isdir(os.path.join(KODIDIR, x)) and x!='.git' and os.path.isfile(os.path.join(KODIDIR, x, 'addon.xml'))]

for item in jdirs:
    v = open(os.path.join(item, 'addon.xml'), 'r')
    vv = re.findall('<addon id=".*?".*?version="(.*?)"', v.read(), re.DOTALL)
    v.close()
    if len(vv) == 1:
        zipname = '{}-{}'.format(os.path.basename(item), vv[0])
        zippath = os.path.join(REPODIR, os.path.basename(item), zipname)
        if not os.path.isfile(zippath+'.zip'):
            shutil.make_archive(zippath, 'zip', KODIDIR, os.path.basename(item))
    else:
        print('Error with {}'.format(item))

