# encoding=utf-8

import logging
import os

from email.utils import formatdate
from mimetypes import guess_type
from urlparse import urlparse
from xml.sax.saxutils import escape

from config import Config
from labels import Labels
from util import strip_url, parse_date_time, get_page_author


class RSS(object):
    def __init__(self, globals):
        self.globals = globals
        self.base = Config.get_base_url()

    def write(self, filename, title, description, label=None, lopts=None):
        lopts = lopts or {}

        pages = [p for p in self.globals.get('pages', []) if self.filter(p, label)]
        pages.sort(key=lambda p: p.get('date'), reverse=True)
        del pages[10:]

        logging.debug("Writing %s with %u items" % (filename, len(pages)))

        if pages:
            feed_pub_date = formatdate(parse_date_time(pages[0].date))
        else:
            feed_pub_date = None

        xml = u'<?xml version="1.0"?>\n'
        xml += u'<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom" xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd">\n'
        xml += u'<channel>\n'
        xml += u'<atom:link href="%(base)s/%(filename)s" rel="self" type="application/rss+xml"/>\n' % {
            'base': self.base,
            'filename': filename,
        }
        xml += u'<language>ru-RU</language>\n'
        xml += u'<docs>http://blogs.law.harvard.edu/tech/rss</docs>\n'
        for cat in lopts.get('itunes_categories', 'Society & Culture').split(','):
            xml += u'<itunes:category text="%s"/>\n' % escape(cat.strip())
        xml += u'<generator>Poole</generator>\n'
        xml += u'<title>%s</title>\n' % escape(title)
        xml += u'<description>%s</description>\n' % escape(description)
        if label is None:
            xml += u'<link>%s/</link>\n' % strip_url(self.base)
        else:
            xml += u'<link>%s</link>\n' % strip_url(self.base + Labels.get_url(label))
        xml += u'<pubDate>%s</pubDate>\n' % feed_pub_date
        xml += u'<lastBuildDate>%s</lastBuildDate>\n' % feed_pub_date

        # process first 10 items
        for p in pages:
            xml += u'<item>\n'
            xml += u'\t<title>%s</title>\n' % escape(p.title)
            link = u"%s/%s" % (self.base, p.url)
            xml += u'\t<link>%s</link>\n' % strip_url(link)
            xml += u'\t<description>%s</description>\n' % escape(p.html)
            date = parse_date_time(p.date)
            xml += u'\t<pubDate>%s</pubDate>\n' % formatdate(date)
            xml += u'\t<guid>%s</guid>\n' % link
            if 'file' in p:
                mime_type = guess_type(urlparse(p.file).path)[0]
                xml += u'\t<enclosure url="%s" type="%s" length="%s"/>\n' % (p.file, mime_type, p.get('filesize', 1))
            for l in Labels.from_post(p):
                xml += u'\t<category>%s</category>\n' % l
            xml += u'\t<author>%(email)s (%(name)s)</author>\n' % get_page_author(p)
            if 'illustration' in p or 'image' in p:
                xml += u'\t<itunes:image href="%s"/>\n' % escape(p.get('image', p.get('illustration')))
            xml += u'</item>\n'

        xml += u'</channel>\n'
        xml += u'</rss>\n'

        print "info   : writing %s" % filename
        fp = open(os.path.join(self.globals.get('output', '.'), filename), 'w')
        fp.write(xml.encode('utf-8'))
        fp.close()

    def write_all(self):
        conf = Config.get()
        self.write('rss.xml',
            conf.get('title', 'My Website'),
            conf.get('description', 'This is my Poole powered website.'))

    def write_labels(self):
        for label, props in Labels.get_all().items():
            if props.get('rss_file'):
                title = props.get('rss_title', u'Posts: %s' % label)
                description = props.get('rss_description', u'Posts from my website that have the "%s" label.' % label)
                self.write(props['rss_file'], title, description, label, lopts=props)

    def filter(self, post, label):
        labels = Labels.from_post(post)
        if label is not None and label not in labels:
            return False
        if 'draft' in labels or 'queue' in labels:
            return False
        if not post.get('date'):
            return False
        if '://' in post.get('url', ''):
            return False
        return True


def write_rss_hook(_globals):
    logging.info("Writing RSS feeds.")
    writer = RSS(_globals)
    writer.write_all()
    writer.write_labels()
