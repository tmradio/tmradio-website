# encoding=utf-8

import logging
import os
import time

from config import Config
from util import parse_date_time, strip_url


class Sitemap(object):
    url_str = "<url>\n    <loc>%s</loc>\n    <lastmod>%s</lastmod>\n    <changefreq>%s</changefreq>\n    <priority>%s</priority>\n</url>\n\n"
    all_str = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<urlset xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\">\n\n%s</urlset>\n"

    def __init__(self, globals):
        self.globals = globals

    def write(self):
        """Generate Google sitemap.xml file."""
        urls = []
        base_url = Config.get_base_url()
        for p in sorted(self.globals.get('pages', []), key=lambda p: p.url):
            url = p.url
            if '://' not in url:
                url = base_url + '/' + url
                item = '<url>\n'
                item += '    <loc>%s</loc>\n' % strip_url(url)
                changefreq = 'weekly'
                priority = 0.4
                if p.get('date'):
                    item += '    <lastmod>%s</lastmod>\n' % time.strftime('%Y-%m-%d', parse_date_time(p['date'], False))
                    changefreq = 'monthly'
                item += '    <changefreq>%s</changefreq>\n' % p.get('changefreq', changefreq)
                item += '    <priority>%s</priority>\n' % p.get('priority', priority)
                item += '</url>\n'
                urls.append(item)
        fname = os.path.join(self.globals['options'].project, "..", "sitemap.xml")
        fp = open(fname, 'w')
        fp.write(self.all_str % "".join(urls))
        fp.close()


def write_sitemap_hook(_globals):
    logging.info("Writing sitemap.xml")
    Sitemap(_globals).write()
