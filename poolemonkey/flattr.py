# encoding=utf-8

"""Adds a flattr button to any page.

The idea is taken from Hyde:
https://github.com/melpomene/Flattr-auto-submit-for-Hyde
"""

import logging
from cgi import escape
from urllib import quote

from config import Config
from util import strip_url


def add_flattr_buttons_hook(pages):
    """Adds the flattr button HTML code to the flattr_button property of all pages."""
    user_name = Config.get_flattr_name()
    if not user_name:
        return

    language = Config.get().get("language", "en_US")
    default_category = Config.get().get("flattr_category", "text")
    base_url = Config.get_base_url()
    default_description = Config.get().get("flattr_description", "")
    on_labels = set(Config.get().get("flattr_labels", ["blog"]))

    logging.debug("Adding flattr buttons (user=%s, cat=%s, lang=%s)." % (user_name, default_category, language))
    for page in pages:
        if "podcast" in page["labels_parsed"]:
            category = "audio"
        elif "video" in page["labels_parsed"]:
            category = "video"
        else:
            category = page.get("flattr_category", default_category)

        if not set(page["labels_parsed"]) & on_labels:
            continue

        summary = page.get("summary")
        if not summary:
            summary = page.get("section", {}).get("default_summary")
        if not summary:
            summary = default_description

        post_author = user_name
        if "author_info" in page and "flattr_name" in page["author_info"]:
            post_author = page["author_info"]["flattr_name"]

        page["flattr_button"] = "<div class='flattr_button'><a target='_blank' title='Flattr this page' href='https://flattr.com/submit/auto?user_id=%(user)s&amp;url=%(url)s&amp;title=%(title)s&amp;description=%(description)s&amp;language=%(language)s&amp;tags=%(tags)s&amp;category=%(category)s'><img src='http://api.flattr.com/button/flattr-badge-large.png' alt='Flattr this page'/></a></div>" % {
            "user": quote(post_author),
            "url": strip_url(quote(base_url + "/" + quote(page.url))),
            "title": quote(page["title"].encode("utf-8")),
            "language": page.get("language", language),
            "tags": quote(u",".join(page["labels_parsed"]).encode("utf-8")),
            "category": quote(page.get("category", category)),
            "description": quote(summary.encode("utf-8")),
        }


def get_flattr_init_code(page):
    return "<script type='text/javascript'>/* <![CDATA[ */ (function() { var s = document.createElement('script'), t = document.getElementsByTagName('script')[0]; s.type = 'text/javascript'; s.async = true; s.src = 'http://api.flattr.com/js/0.6/load.js?mode=auto'; t.parentNode.insertBefore(s, t); })(); /* ]]> */ </script>"


def get_flattr_button(page):
    if not page.get("no_flattr"):
        return page.get("flattr_button", "")
    return ""


def pre_hook(_globals):
    add_flattr_buttons_hook(_globals["pages"])
