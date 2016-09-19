#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = u'sunisdown'
SITENAME = u'SunisDown'
SITEURL = ''

PATH = 'content'

TIMEZONE = 'Asia/Shanghai'

THEME='/Users/sunisdown/pelican-themes/pelican-blue'

DEFAULT_LANG = u'zh'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = 'feeds/all.atom.xml'
CATEGORY_FEED_ATOM = 'feeds/%s.atom.xml'
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None


STATIC_PATHS = ['images', 'extra/CNAME']
EXTRA_PATH_METADATA = {'extra/CNAME': {'path': 'CNAME'},}

# Social widget
SOCIAL = (('notebook', 'http://1024.today'),
          ('twitter', 'https://twitter.com/SunisD0wn'),
          ('github', 'https://github.com/sunisdown'))

MENUITEMS = (('Blog', '/index.html'),
            ('Archives', '/archives.html'),
             ('Tags', '/tags.html'),)

DEFAULT_PAGINATION = 10

# Uncomment following line if you want document-relative URLs when developing
#RELATIVE_URLS = True
