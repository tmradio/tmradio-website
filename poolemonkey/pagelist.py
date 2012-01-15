# encoding=utf-8

import os
import time

from poolemonkey import strip_url, parse_date_time, Config
from poolemonkey.util import get_page_author
from labels import get_page_section, Labels


class Page(object):
    def __init__(self, filename=None):
        self.filename = None
        self.props = {}
        if filename is not None:
            self.parse(filename)

    @classmethod
    def from_dict(cls, d):
        p = cls()
        p.props = d
        return p

    def parse(self, filename):
        self.filename = filename

        data = file(filename, "rb").read().decode("utf-8")
        if "---" in data:
            head, body = data.split("\n---\n", 1)
        else:
            head = data
            body = ""

        for line in head.split("\n"):
            if ":" in line:
                k, v = line.split(":", 1)
                self.props[k.strip()] = v.strip()
        self.props["#text"] = body.strip()

    def save(self):
        file(self.filename, "wb").write(self.dump().encode("utf-8"))

    def dump(self):
        output = ""
        for k, v in sorted(self.props.items()):
            if k != "#text":
                output += u"%s: %s\n" % (k, v.strip())
        output += u"---\n" + self.props["#text"] + u"\n"
        return output

    def __repr__(self):
        return str(self.props)

    def __setitem__(self, k, v):
        self.props[k] = v


def show(pages, simple=False, **kwargs):
    if simple:
        return show_simple(pages, **kwargs)
    return show_table(pages, **kwargs)


def get_page_labels(page):
    labels = [l.strip() for l in page.get('labels', '').split(',') if l.strip()]
    if page.has_key('file') and 'podcast' not in labels:
        labels.append('podcast')
    return sorted(labels)


def filter_pages(pages, limit=None, label=None, order_by="date", reverse_order=True, **kwargs):
    """Returns pages that satisfy the specified criteries.  Pages without the
    'date' field or with the 'draft' label are never shown."""
    result = []

    for page in pages:
        if order_by not in page:
            continue
        labels = get_page_labels(page)
        if "draft" in labels or "queue" in labels:
            continue
        if label is not None and label not in labels:
            continue
        result.append(page)

    result.sort(key=lambda p: (p.get(order_by), p.get("title")), reverse=reverse_order)

    if limit is not None:
        result = result[:limit]

    return result


def show_simple(pages, show_dates=True, show_comments=True, show_author=False, **kwargs):
    pages = filter_pages(pages, **kwargs)

    output = u''

    authors = list(set([p.get('author') for p in pages if p.get('author')]))
    show_author = len(authors) > 2

    for page in pages:
        output += u'<li><a href="%s">%s</a>' % (strip_index(page.get('url')), page.get('title'))
        if show_author:
            author = get_page_author(page)[1]
            if author != 'anonymous':
                output += u' (%s)' % get_page_author(page)[1]
        if limit is None and show_dates:
            date = page.date + ' 00:00'
            date = datetime.datetime.strptime(date[:16], '%Y-%m-%d %H:%M').strftime('%d.%m.%Y')
            output += u' <span class="date">%s</span>' % date
        if DISQUS_ID is not None and show_comments:
            output += u' <a class="dcc" href="%s#disqus_thread">комментировать</a>' % (strip_index(page.get('url')))
            # output += u' <a class="dcc" href="%s#disqus_thread" data-disqus-identifier="%s">комментировать</a>' % (page.get('url'), get_disqus_page_id(page))
        output += u'</li>\n'

    if output:
        output = u'<ul class="pagelist">\n' + output + u'</ul>\n'
        if DISQUS_ID is not None and show_comments:
            output += u'<script type="text/javascript">var disqus_shortname = "'+ DISQUS_ID +'"; (function () { var s = document.createElement("script"); s.async = true; s.type = "text/javascript"; s.src = "http://" + disqus_shortname + ".disqus.com/count.js"; (document.getElementsByTagName("HEAD")[0] || document.getElementsByTagName("BODY")[0]).appendChild(s); }());</script>\n'
        return output

    return u'Ничего нет.'


def show_table(pages, show_dates=True, show_categories=True, show_dlcount=True, show_comments=True, **kwargs):
    pages = filter_pages(pages, **kwargs)

    dlstats = get_dlstats()

    disqus_id = Config.get_disqus_id()
    if not disqus_id:
        show_comments = False
    base_url = Config.get().get("base_url")

    rows = []
    for page in pages:
        row = {
            "link": page.get("link", "/" + strip_url(page.get("url"))),
            "file": page.get("file"),
            "text": page.get("title"),
            "date": page.get("date") and time.strftime("%d.%m.%y", parse_date_time(page.date, as_float=False)),
            "section": get_page_section(page),
            "downloads": int(dlstats.get(page.get("file"), 0)),
        }
        row["real_link"] = row["link"]
        if "://" not in row["real_link"]:
            row["real_link"] = base_url.rstrip("/") + row["link"]
        rows.append(row)

    if not rows:
        return u"Ничего нет."

    if sum([r["downloads"] for r in rows]) == 0:
        show_dlcount = False

    output = u"<table class='pagelist'><tbody>\n"
    for idx, row in enumerate(rows):
        row["class"] = (idx % 2) and "odd" or "even"
        output += u"<tr class='first %(class)s'>" % row
        output += u"<td rowspan='2' class='date'>%(date)s</td>" % row
        output += u"<td class='title'><a title='%(link)s' href='%(link)s'>%(text)s</a></td></tr><tr class='second %(class)s'><td class='meta'>" % row
        if show_categories and row["section"]:
            output += u"<span class='section'>раздел: <a title='Показать все записи из этого раздела' href='%(link)s'>%(title)s</a></span> " % row["section"]
        if show_dlcount:
            output += u"<span class='dlcount'><a title='Скачать MP3 файл' href='%(file)s'>скачать (%(downloads)u)</a></span> " % row
        if show_comments:
            output += u'<span><a class="dcc" href="%(real_link)s#disqus_thread">комментировать</a></span> ' % row
        output += u"</td></tr>\n"

    output += u"</tbody></table>\n"

    if show_comments:
        output += u'<script type="text/javascript">var disqus_shortname = "'+ disqus_id +'"; (function () { var s = document.createElement("script"); s.async = true; s.type = "text/javascript"; s.src = "http://" + disqus_shortname + ".disqus.com/count.js"; (document.getElementsByTagName("HEAD")[0] || document.getElementsByTagName("BODY")[0]).appendChild(s); }());</script>\n'

    return output


def get_dlstats():
    data = get_dlstats_raw("input/dlstats.csv")
    for k, v in get_dlstats_raw("input/dlstats_old.csv").items():
        if k not in data:
            data[k] = 0
        data[k] = int(data[k]) + int(v)
    return data


def get_dlstats_raw(filename):
    if os.path.exists(filename):
        data = dict([l.strip().split(",") for l in file(filename, "rb").read().split("\n") if "," in l])
    else:
        data = {}
    return data


def get_page_meta(page):
    parts = []
    if 'date' in page:
        parts.append(time.strftime('%Y.%m.%d', parse_date_time(page['date'], False)))

        author = get_page_author(page)
        if author is not None:
            if not author.get("fullname"):
                author["fullname"] = author["name"]
            if author.get("profile"):
                parts.append(u"автор: <a rel=\"author\" href=\"%(profile)s\">%(fullname)s</a>" % author)
            else:
                parts.append(u"автор: %(fullname)s" % author)

    labels = Labels.from_post(page)
    if len(labels):
        tags = [t for t in [Labels.get_href(tag) for tag in labels] if t]
        if tags:
            parts.append(u"метки: " + u", ".join(tags))

    if parts:
        return u'<p class="meta pagemeta">%s</p>' % u'; '.join(parts)
    return u''


def get_page_classes(page):
    """Возвращает строку с классами CSS для поста."""
    output = u" id='%s'" % page.url.replace("/", "_").replace(".", "_")

    classes = [label for label in Labels.from_post(page)]
    if classes:
        output += u" class='%s'" % u" ".join(classes)
    return output
