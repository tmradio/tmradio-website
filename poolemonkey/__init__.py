# encoding=utf-8

import logging
import os
import time

from config import Config
from util import get_page_author, strip_url, parse_date_time
from pagelist import get_page_classes


class MainMenu(object):
    output = None

    @classmethod
    def get(self, pages, page):
        if self.output is None:
            mpages = [p for p in pages if "menu-position" in p]
            mpages.sort(key=lambda p: int(p["menu-position"]))
            entry = u'<li><a href="%s">%s</a></li>\n'
            self.output = u''
            for p in mpages:
                style = p["title"] == page["title"] and "current" or ""
                self.output += entry % (strip_url(p["url"]), p.get('mtitle', p["title"]))
        return self.output


class Navigation(object):
    def __init__(self, pages):
        self.pages = pages

    def build(self):
        logging.debug("Building the navigation index.")
        for page in self.pages:
            self.get_page(page)

    def get_page(self, page):
        if "nav_links" not in page:
            links = {}
            if "date" in page:
                links["first"], links["prev"], links["next"], links["last"] = self._get_page_neighbors(page)
            links["index"] = self._get_page_index(page)
            page["nav_links"] = links
        return page["nav_links"]

    def get_head(self, page):
        output = ""
        links = self.get_page(page)
        for k, rel in {"prev": "prev", "next": "next", "first": "first", "last": "last", "index": "index"}.items():
            link = links.get(k)
            if link:
                href = link
                if isinstance(href, dict):
                    href = href["url"]
                output += "<link rel='%s' type='text/html' href='%s'/>\n" % (rel, href)
        return output

    def _get_page_neighbors(self, page):
        left = []
        right = []

        filter = set(page["labels_parsed"])
        for _page in self.pages:
            if "date" not in _page:
                continue
            if not filter & set(_page["labels_parsed"]):
                continue
            if _page["date"] > page["date"]:
                right.append(_page)
            elif _page["date"] < page["date"]:
                left.append(_page)

        _first, _prev, _next, _last = None, None, None, None

        url = lambda page: {"url": "/" + page["url"].replace("/index.html", "/"), "title": page["title"]}

        if len(left):
            left.sort(key=lambda p: p["date"])
            _first = url(left[0])
            _prev = url(left[-1])
        if len(right):
            right.sort(key=lambda p: p["date"])
            _next = url(right[0])
            _last = url(right[-1])

        return _first, _prev, _next, _last

    def _get_page_index(self, page):
        if len(page["url"].split("/")) < 3:
            return None
        path = os.path.dirname(os.path.dirname("/" + page["url"]))
        while not os.path.exists("input" + path + "/index.md"):
            path = os.path.dirname(path)
        return path


def hook_preconvert(_globals):
    from photo import prepare_photos_hook

    logging.getLogger().setLevel(logging.DEBUG)

    pages = _globals["pages"]

    import labels
    labels.parse_labels_hook(pages)
    labels.find_authors_hook(pages)

    Navigation(pages).build()

    prepare_photos_hook(pages)

    import flattr
    flattr.pre_hook(_globals)


def hook_postconvert(_globals):
    from util import fix_typo_hook
    fix_typo_hook(_globals["pages"])

    from rss import write_rss_hook
    write_rss_hook(_globals)

    from sitemap import write_sitemap_hook
    write_sitemap_hook(_globals)

    from disqus import enable_comments_hook
    enable_comments_hook(_globals["pages"])

    from textools import process_pages
    process_pages(_globals["pages"])


def get_extra_headers(page):
    output = u""

    import disqus
    output += disqus.get_extra_headers(page)

    return output


def get_extra_footers(page):
    output = u""

    import disqus
    output += disqus.get_extra_footers(page)

    return output


def get_ueb_code(page, link_only=False):
    pattern = Config.get().get("ueb_pattern")
    link = (pattern or "%s") % page.fname[2:]

    if link_only:
        return link
    elif not pattern:
        return ""
    return "<link rel='alternate' type='application/wiki' title='Edit this page!' href='%s'/>" % link


def init(_globals):
    """Initializes the extensions."""
    _globals["hook_preconvert_00"] = lambda: hook_preconvert(_globals)
    _globals["hook_postconvert_00"] = lambda: hook_postconvert(_globals)

    _globals["page_classes"] = get_page_classes
    _globals["universal_edit_button"] = get_ueb_code

    _globals["Navigation"] = Navigation
    _globals["get_head_nav_links"] = lambda page: Navigation(_globals["pages"]).get_head(page)

    from pagelist import get_page_meta
    _globals["page_meta"] = get_page_meta

    _globals["poolemonkey_headers"] = get_extra_headers
    _globals["poolemonkey_footers"] = get_extra_footers

    import flattr
    _globals["flattr_this"] = flattr.get_flattr_button

    import share
    _globals["buttons"] = share.get_buttons

    import disqus
    _globals["comment_form"] = disqus.get_comment_form

    import util
    _globals["embed_player"] = util.get_player
    _globals["play_file"] = util.get_file_player
    _globals["page_url"] = util.page_url
