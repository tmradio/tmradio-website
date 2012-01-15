# encoding=utf-8

"""Poolemonkey extension that makes the text prettier.

Generates a TOC, adds header/paragraph anchors, etc."""

import binascii
import re

from config import Config


def process_text(text):
    """Processes the text according to current settings."""
    conf = Config.get()
    crc32 = lambda _str: "%08x" % (binascii.crc32(_str.strip().encode("utf-8")) & 0xffffffff)

    if conf.get("add_header_anchors", False):
        headers = []
        for match in re.findall("(^<(h\d)>((?:(?!</h\d>).)*)</h\d>$)", text, re.S | re.M):
            _hash = crc32(match[2])
            _repl = u"<%s><a name='%s'></a>%s <a class='anchor' href='#%s'>#</a></%s>" % (match[1], _hash, match[2], _hash, match[1])
            text = text.replace(match[0], _repl)
            headers.append((match[1], _hash, match[2]))

        tocmark = conf.get("toc_mark", u"<!--TOC-->")
        if len(headers) >= conf.get("min_toc_length", 3) and tocmark in text:
            _toc = u"<div class='toc'><p>%s</p>\n<ul>\n" % conf.get("toc_caption", u"Table of contents:")
            _toc += u"".join([u"<li><a href='#%s'>%s</a></li>\n" % (_href, _text) for _level, _href, _text in headers])
            _toc += u"</ul>\n</div>\n"
            text = text.replace(tocmark, _toc)

    if conf.get("add_paragraph_anchors", False):
        for match in re.findall("(^<p>((?:(?!/p).)*)</p>$)", text, re.S | re.M):
            if "<img" in match[1]:
                continue
            _hash = crc32(match[1])
            repl = u"<p><a name='%s'></a>%s <a class='anchor' href='#%s'>#</a></p>" % (_hash, match[1], _hash)
            text = text.replace(match[0], repl)

    return text


def process_pages(pages):
    """Processes all pages."""
    for page in pages:
        page.html = process_text(page.html)
