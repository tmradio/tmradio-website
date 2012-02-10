# encoding=utf-8

import binascii
import cgi
import email.utils
import logging
import mimetypes
import os
import re
import time
import yaml


pages = None

config = None


def init_poole_extensions(_pages):
    """Initializes the module by saving a reference to the list of pages."""
    global pages
    pages = _pages
    logging.getLogger().setLevel(logging.INFO)


def hook_preconvert_sitemap_alt():
    """Creates a sitemap of all pages.  Set the "sitemap" config option to
    "yes" to make this work."""
    if get_config("sitemap") != True:
        return

    base_url = get_config("base_url")
    if base_url is None:
        logging.warning("Can't build a sitemap: base_url not set.")
        return

    sitemap = "<?xml version='1.0' encoding='UTF-8'?>\n"
    sitemap += "<urlset xmlns='http://www.sitemaps.org/schemas/sitemap/0.9\'>\n"
    for page in sorted(pages, key=lambda p: p["url"]):
        labels = get_page_labels(page)
        if "draft" in labels or "queue" in labels:
            continue
        sitemap += "<url><loc>%s</loc></url>\n" % get_page_url(page)

    sitemap += "</urlset>\n"

    file("output/sitemap.xml", "wb").write(sitemap)
    file("output/robots.txt", "wb").write("Sitemap: %s" % _full_url("sitemap.xml"))


def hook_html_ueb(html, page):
    """Adds a link to the page editor, if you set the "ueb_pattern" config
    option."""
    pattern = get_config("ueb_pattern")
    if pattern is not None:
        link = pattern % page.fname[2:]
        html = _add_to_head(html, "<link rel='alternate' type='application/wiki' title='Edit this page!' href='%s'/>" % link)
    return html


def hook_postconvert_feeds():
    """Creates RSS files."""
    for feed in get_config("feeds", []):
        matching_pages = pages
        if "labels" in feed:
            matching_pages = _get_pages_with_labels(matching_pages, feed["labels"])
        _write_feed(feed, matching_pages)


def hook_postconvert_anchors():
    """Adds paragraph anchors."""
    add_para_anchors = get_config("add_paragraph_anchors")
    add_head_anchors = get_config("add_header_anchors")
    toc_mark = get_config("toc_mark", u"<!--TOC-->")
    min_toc_length = int(get_config("min_toc_length", 3))
    toc_caption = get_config("toc_caption", u"Table of contents:")

    for page in pages:
        html = page.html
        if add_head_anchors:
            html = _add_head_anchors(html, toc_mark, min_toc_length, toc_caption)
        if add_para_anchors:
            html = _add_para_anchors(html)
        page.html = html


def hook_html_meta_keywords(html, page):
    """Adds meta keywords."""
    keywords = u""

    if "summary" in page:
        keywords += u"<meta name='description' content='%s'/>\n" % _escape_xml(page["summary"])
    if "keywords" in page:
        keywords += u"<meta name='keywords' content='%s'/>\n" % _escape_xml(page["keywords"])
    keywords += u"<link rel='canonical' href='%s'/>\n" % strip_url(get_page_url(page))

    return html.replace("</head>", keywords + "</head>")


def pagelist(label=None, limit=None, date=None, order="-date"):
    """Renders and returns a list of links to pages."""

    reverse_order = order.startswith("-")
    order_field = order.lstrip("-")

    def _filter(page):
        labels = get_page_labels(page)
        if "queue" in labels or "draft" in labels:
            return False
        if label is not None and label not in labels:
            return False
        if date is not None and "date" not in page:
            return False
        if order_field not in page:
            return False
        return True

    matching_pages = sorted([p for p in pages if _filter(p)],
        key=lambda p: (p[order_field].lower(), p["url"]), reverse=reverse_order)

    if limit is not None:
        del matching_pages[limit:]

    if not matching_pages:
        return "(no matching pages)"

    output = u"<ul class='pagelist'>\n"
    for page in matching_pages:
        output += u"<li>"
        output += u"<a href='/%s'>%s</a>" % (strip_url(page["url"]), _escape_xml(page["title"]))
        if date is not None:
            output += u" (%s)" % time.strftime(date, get_page_date(page))
        output += u"</li>\n"
    output += u"</ul>\n"

    return output


def page_classes(page):
    """Returns a string which adds page-specific classes to an HTML node."""
    output = u" id='%s'" % re.sub("[-./]", "_", page["url"])

    labels = get_page_labels(page)
    if labels:
        output += u" class='%s'" % " ".join(labels)

    return output


def page_meta(page):
    """Renders the page metadata block."""
    parts = []

    if "date" in page:
        parts.append(time.strftime("%Y.%m.%d", get_page_date(page)))

        author = get_page_author(page)
        if author is not None:
            if author.get("url"):
                parts.append(u"автор: <a rel='author' href='%s'>%s</a>" % (_escape_xml(author["url"]), _escape_xml(author["name"])))
            else:
                parts.append(u"автор: %s" % _escape_xml(author["name"]))

        labels = get_page_labels(page)
        if labels:
            labels = [_get_label_info(l) for l in labels]
            printable = [_format_label(l) for l in sorted(labels, key=lambda l: l[1].lower())]
            parts.append(u"метки: %s" % u", ".join(printable))

    if not parts:
        return ""

    return u"<p class='meta pagemeta'>%s</p>" % u"; ".join(parts)


def get_page_labels(page):
    """Returne a list of page's labels read from the "labels" property.  The
    result is cached, next calls are fast."""
    if "_parsed_labels" not in page:
        _raw_labels = page.get("labels", "").strip()
        if not _raw_labels:
            page["_parsed_labels"] = []
        else:
            page["_parsed_labels"] = re.split(",\s+", _raw_labels)
    return page["_parsed_labels"]


def strip_url(url):
    """Stripts the /index.html suffix if the URL is local, if the "strip_urls"
    config option is enabled."""
    if not get_config("strip_urls"):
        return url
    if not url.endswith("/index.html"):
        return url
    if "://" in url and not url.startswith(get_config("base_url")):
        return url
    return url[:-10]


def get_page_date(page):
    if "date" not in page:
        return None
    if "_parsed_date" not in page:
        date = _get_full_datetime(page["date"])
        page["_parsed_date"] = time.strptime(date, "%Y-%m-%d %H:%M")
    return page["_parsed_date"]


def get_page_url(page):
    """Returns the page's fully-qualified URL."""
    return _full_url(page["url"])


def get_page_author(page):
    """Returns page author description as a dictionary with keys "name",
    "email" and "url"."""
    authors = get_config("authors")
    if authors is None:
        return None

    authors_dict = dict([(a["name"], a) for a in authors])

    if "author" in page and page["author"] in authors_dict:
        author = authors_dict[page["author"]]
    else:
        author = authors[0]

    return author


def get_navigation(page):
    """Returns information about siblings."""
    if "_parsed_navigation" in page:
        return page["_parsed_navigatoin"]

    nav = {"first": None, "prev": None, "next": None, "last": None, "index": None}

    labels = get_page_labels(page)
    if not labels:
        return None  # current page has no labels

    matching_pages = [p for p in pages if is_page_visible(p) and labels[0] in get_page_labels(p)]
    if not matching_pages:
        return None  # no other pages with this label (can't be)

    matching_pages.sort(key=lambda p: (p.get("date"), p.get("title")))
    nav["first"] = matching_pages[0]
    nav["last"] = matching_pages[-1]

    for p in matching_pages:
        if p["url"] == page["url"]:
            break
        nav["prev"] = p

    for p in reversed(matching_pages):
        if p["url"] == page["url"]:
            break
        nav["next"] = p

    linfo = _get_label_info(labels[0])
    if linfo[2]:
        nav["index"] = linfo[2]

    page["_parsed_navigatoin"] = nav
    return nav


# --- utility functions ---

def get_config(key, default=None):
    global config
    if config is None:
        config = yaml.load(file("config.yaml", "rb").read().decode("utf-8"))
    return config.get(key, default)


def _full_url(url):
    base_url = get_config("base_url")
    if not base_url.endswith("/"):
        base_url += "/"
    return strip_url(base_url + url.lstrip("/"))


def is_page_visible(page):
    """Returns True is the page is OK to list."""
    labels = get_page_labels(page)
    if "draft" in labels or "queue" in labels:
        return False
    return True


def _escape_xml(value):
    return cgi.escape(value)


def _add_to_head(html, header):
    """Adds a new header before the closing HEAD tag."""
    return html.replace("</head>", header.strip() + "\n</head>")


def _get_label_info(label):
    """"Returns label description as a tuple: (name, title, link)."""
    labels = get_config("labels", [])
    for k in labels:
        if k["name"] == label:
            return (label, k.get("title", label), k.get("link"))
    return (label, label, None)


def _format_label(label):
    if not label[2]:
        return label[1]
    return u"<a rel='tag' href='%s'>%s</a>" % (_escape_xml(label[2]), label[1])


def _get_full_datetime(value):
    default = "0000-00-00 00:00"
    return (value + default[len(value):])[:len(default)]


def _format_rfc_date(value):
    ts = time.strptime(_get_full_datetime(value), "%Y-%m-%d %H:%M")
    return email.utils.formatdate(time.mktime(ts))


def _get_pages_with_labels(pages, labels):
    result = []
    labels = set(labels)
    f = lambda p: set(get_page_labels(p)) & labels
    return filter(f, pages)


def _write_feed(feed, pages):
    rss_url = _full_url(feed["name"])

    xml = u"<?xml version='1.0' encoding='UTF-8'?>\n"
    xml += u"<rss version='2.0' xmlns:atom='http://www.w3.org/2005/Atom' xmlns:itunes='http://www.itunes.com/dtds/podcast-1.0.dtd'>\n"
    xml += u"<channel>\n"
    xml += u"<atom:link href='%s' rel='self' type='application/rss+xml'/>\n" % rss_url
    if "language" in feed:
        xml += u"<language>%s</language>\n" % feed["language"]
    xml += u"<docs>http://blogs.law.harvard.edu/tech/rss</docs>\n"
    xml += u"<generator>Poole + extensions</generator>\n"
    xml += u"<description>%s</description>\n" % _escape_xml(feed.get("description", "No description").strip())
    xml += u"<title>%s</title>\n" % _escape_xml(feed.get("title", "No title").strip())
    xml += u"<link>%s</link>\n" % _full_url(feed.get("link", ""))

    push = get_config("rss_push")
    if push is not None:
        xml += u"<atom:link rel='hub' href='%s'/>\n" % _escape_xml(push)

    limit = feed.get("limit", 20)

    real_pages = sorted(pages, key=lambda p: p.get("date"), reverse=True)
    for page in real_pages[:limit]:
        xml += _get_rss_item(page)

    xml += u"</channel>\n"
    xml += u"</rss>\n"

    filepath = os.path.join("output", feed["name"])
    file(filepath, "wb").write(xml.encode("utf-8"))
    logging.info("Wrote %s" % filepath)


def _get_rss_item(page):
    labels = get_page_labels(page)
    if "draft" in labels or "queue" in labels:
        return ""
    if "date" not in page:
        return ""

    xml = u"<item>\n"
    xml += u"\t<title>%s</title>\n" % _escape_xml(page["title"])
    xml += u"\t<guid>%s</guid>\n" % _full_url(page["url"])
    xml += u"\t<pubDate>%s</pubDate>\n" % _format_rfc_date(page["date"])

    if "file" in page:
        _filename = page["file"].split("/")[-1]
        mime_type = mimetypes.guess_type(_filename)[0]
        xml += u"\t<enclosure url='%s' type='%s' length='%s'/>\n" % (page["file"], mime_type, page.get("filesize", "0"))

    if get_config("rss_with_bodies") != False:
        xml += u"\t<description>%s</description>\n" % _escape_xml(_fix_rss_item_description(page.html, page))

    author = get_page_author(page)
    if author is not None:
        xml += u"\t<author>%s</author>\n" % author.get("email", "alice@example.com")

    xml += u"</item>\n"
    return xml

def _fix_rss_item_description(text, page):
    patterns = "href='([^']+)'", 'href="([^"]+)"', 'src="([^"]+)"', "src='([^']+)'"
    for pattern in patterns:
        for match in re.finditer(pattern, text):
            link = match.group(1)
            if link.startswith("mailto:"):
                continue
            if link.startswith("#"):
                link = "/" + strip_url(page["url"]) + link
            if "://" not in link:
                link = config["base_url"].rstrip("/") + "/" + link.lstrip("/")

            tmp = match.group(0).replace(match.group(1), link)
            text = text.replace(match.group(0), tmp)

    text = re.sub("<iframe\s.*></iframe>\s*", "", text)
    text = re.sub("<object\s.*></object>\s*", "", text)
    text = re.sub("<p>\s*</p>", "", text)

    return text


def _crc32(value):
    return "%08x" % (binascii.crc32(value.strip().encode("utf-8")) & 0xffffffff)


def _add_head_anchors(text, toc_mark, min_toc_length, toc_caption):
    headers = []
    for match in re.findall("(^<(h\d)>((?:(?!</h\d>).)*)</h\d>$)", text, re.S | re.M):
        _hash = _crc32(match[2])
        _repl = u"<%s><a name='%s'></a>%s <a class='anchor' href='#%s'>#</a></%s>" % (match[1], _hash, match[2], _hash, match[1])
        text = text.replace(match[0], _repl)
        headers.append((match[1], _hash, match[2]))

    if len(headers) >= min_toc_length and toc_mark in text:
        _toc = u"<div class='toc'><p>%s</p>\n<ul>\n" % toc_caption
        _toc += u"".join([u"<li><a href='#%s'>%s</a></li>\n" % (_href, _text) for _level, _href, _text in headers])
        _toc += u"</ul>\n</div>\n"
        text = text.replace(toc_mark, _toc)

    return text


def _add_para_anchors(text):
    for match in re.findall("(^<p>((?:(?!/p).)*)</p>$)", text, re.S | re.M):
        if "<img" in match[1]:
            continue
        _hash = _crc32(match[1])
        repl = u"<p><a name='%s'></a>%s&nbsp;<a class='anchor' href='#%s'>#</a></p>" % (_hash, match[1], _hash)
        text = text.replace(match[0], repl)
    return text


__all__ = [
    "get_config",
    "get_navigation",
    "get_page_author",
    "get_page_date",
    "get_page_labels",
    "get_page_url",
    "hook_html_meta_keywords",
    "hook_html_ueb",
    "hook_postconvert_anchors",
    "hook_postconvert_feeds",
    "hook_preconvert_sitemap_alt",
    "init_poole_extensions",
    "is_page_visible",
    "page_classes",
    "page_meta",
    "pagelist",
    "strip_url",
]
