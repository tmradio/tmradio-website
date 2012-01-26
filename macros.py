# vim: set tw=0 fileencoding=utf-8:

from xml.sax.saxutils import escape
import datetime
import email.utils
import glob
import simplejson as json
import mimetypes
import os.path
import re
import sys
import time
import urllib
import urlparse

from poolemonkey import init
from poolemonkey.pagelist import get_page_labels, filter_pages, show as pagelist
from poolemonkey.util import strip_url


init(globals())


def format_duration(value):
    hours = value // 3600
    value = value - (hours * 3600)
    minutes = value // 60
    seconds = value - (minutes * 60)

    return "%u:%02u:%02u" % (hours, minutes, seconds)


def pagelist(pages, **kwargs):
    pages = filter_pages(pages, **kwargs)

    table = u"<table class='pagelist'>\n"
    # table += u"<thead>\n<tr><th class='title'>Заголовок</th>\n"
    # table += u"<th/>\n"
    # table += u"<th/>\n"
    # table += u"<th class='date'>Дата</th>\n"
    # table += u"<th class='comments'>Комментарии</th>\n"
    # table += u"</tr>\n</thead>\n"

    total_duration = 0
    output = u"<tbody>\n"
    for page in pages:
        page_url = page.get("link", "/" + strip_url(page.get("url")))
        page_date = page.get("date") and time.strftime("%d.%m.%y", parse_date_time(page.date, as_float=False))
        output += u"<tr>\n"
        output += u"<td class='title'><a href='%s'>%s</a></td>\n" % (page_url, page["title"])
        if page.get("duration"):
            output += u"<td class='duration' title='Продолжительность записи'>%s</td>\n" % format_duration(int(page["duration"]))
            total_duration += int(page["duration"])
        else:
            output += "<td/>\n"
        if page.get("file"):
            output += u"<td class='play'><a title='Прослушать' href='%s'><span>слушать</span></a></td>\n" % page["file"]
            output += u"<td class='dl'><a title='Скачать' href='%s'><span>скачать</span></a></td>\n" % page["file"]
        else:
            output += u"<td/><td/>"
        output += u"<td class='date'>%s</td>\n" % page_date
        output += u"<td class='comments'><a href='http://www.tmradio.net%s#disqus_thread'>комментировать</a></td>\n" % page_url
        output += u"</tr>\n"
    output += u"</tbody>\n"

    if total_duration:
        table += u"<tfoot><tr><td/><td class='duration' title='Общая продолжительность'>%s</td><td colspan='4'/></tr></tfoot>\n" % format_duration(total_duration)

    table += output
    table += u"</table>\n"
    table += u"<script>$(tmradio.pagelist.ready)</script>\n"

    return table


def get_page_labels(page):
    labels = [l.strip() for l in page.get('labels', '').split(',') if l.strip()]
    if page.has_key('file') and 'podcast' not in labels:
        labels.append('podcast')
    return sorted(labels)


def get_label_url(label):
    for pattern in LABEL_PAGES:
        fn = pattern % label
        if os.path.exists(fn):
            return strip_url('/' + os.path.splitext(fn)[0].split('/', 1)[1] + '.html')

def get_label_link(label):
    text = label
    if LABEL_NAMES.has_key(label):
        text = LABEL_NAMES[label]
    return u'<a href="%s">%s</a>' % (get_label_url(label), text)


def parse_date_time(text, as_float=True):
    """Преобразует дату-время из текста в структуру.

    Поддерживаемый формат: ГГГГ-ММ-ДД ЧЧ:ММ:СС, недостающие сегменты с конца
    заполняюся нулями.
    """
    default = '0000-01-01 00:00:00'
    text = text + default[len(text):]
    result = time.strptime(text, '%Y-%m-%d %H:%M:%S')
    if as_float:
        result = time.mktime(result)
    return result


def print_menu(pages, page):
    pages = [p for p in pages if p.get('mpos')]

    output = u'<ul id="nav">'
    for p in sorted(pages, key=lambda a: int(a.mpos)):
        cls = p.get('mclass', '')
        if p.url == page.url:
            cls += u' active'
        output += u'<li class="%(class)s"><a href="%(link)s">%(title)s</a></li>' % {
            'link': p.url,
            'title': p.get('mtitle', p.get('title', 'wtf :(')),
            'class': cls,
        }
    output += u'</ul>'
    return output


def get_rss_table(label=None):
    pass  # FIXME
    """
    labels = get_label_stats(pages).keys()
    pages_ = [page for page in pages if os.path.splitext(page.url)[0] in labels or page.get('rsstitle')]

    if label is not None:
        pages_ = [p for p in pages_ if p.get("labels") == label]

    pages_.sort(key=lambda p: (p.get("order", "5"), p.get("rsstitle", p.get("title")).lower()))

    html = u'<table class="skel" id="rsst"><tbody>\n'
    for page in pages_:
        page['name'] = os.path.splitext(page.url)[0]
        page['rsstitle'] = page.get('rsstitle', page.get('title'))
        if not page['rsstitle']:
            continue
        page['rsslink'] = page.get('rsslink', page.get('name') + '.xml')
        page['jsonlink'] = page.get('jsonlink', page.get('name') + '.json')
        page['page_url'] = strip_url(page.get('url'))
        html += u'<tr><td><a href="%(page_url)s">%(rsstitle)s</a></td><td><a href="%(rsslink)s">RSS</a></td>' % page
        html += u'<td><a href="%s">iTunes</a></td>' % itunes_link(page['rsslink'])
        if page['jsonlink']:
            html += u'<td><a href="%(jsonlink)s">JSON</a>' % page
        html += u'</td></tr>\n'
    if label is None:
        html += u'<tr><td>Всё подряд</td><td><a href="http://rss.tmradio.net/tmradio/all">RSS</a></td><td><a href="itpc://rss.tmradio.net/tmradio/all">iTunes</a></td><td><a href="/rss.json">JSON</a></td></tr>\n'
    html += u'</tbody></table>\n'

    return html
    """

def itunes_link(link):
    if '://' not in link:
        link = BASE_URL + '/' + link.lstrip('/')
    return link.replace('http://', 'itpc://')


def get_yandex_money_stats():
    data = {"in": 0.0, "out": 0.0, "history": []}

    filename = "input/support/donate/yandex/history.csv"
    for line in file(filename, "rb").read().decode("utf-8").strip().split("\n"):
        parts = line.split(",", 2)
        parts[1] = float(parts[1])
        parts[0] = time.strftime("%d.%m.%y", time.strptime(parts[0], "%Y-%m-%dT%H:%M:%SZ"))

        if parts[1] < 0:
            data["out"] -= parts[1]
        else:
            data["in"] += parts[1]
        data["history"].append(parts)

    return data


def yandex_money_stats():
    stats = get_yandex_money_stats()
    data = {
        "income": stat["in"],
        "outcome": stats["out"],
        "left": stats["in"] - stats["out"],
    }
    return u'Яндекс.Деньгами собрано: %(income).2f, потрачено: %(outcome).2f, осталось: %(left).2f (информация обновляется примерно раз в неделю); доступен <a href="/support/donate/yandex/">полный список транзакций</a>.' % data


def yandex_money_table():
    data = get_yandex_money_stats()

    output = u'<table class="skel" id="yamoney">\n'

    output += u'<tfoot>\n'
    output += u'<tr><td/><td>%.2f</td><td>Всего получено</td></tr>\n' % (data['in'])
    output += u'<tr><td/><td>%.2f</td><td>Всего потрачено</td></tr>\n' % (data['out'])
    output += u'<tr><td/><td>%.2f</td><td>Текущий остаток</td></tr>\n' % (data['in'] - data['out'])
    output += u'</tfoot>\n'

    output += u'<tbody>\n'
    for t in data['history']:
        cls = "in"
        if float(t[1]) < 0:
            cls = "out"
        output += u"<tr class='%s'>" % cls
        output += u'<td>%s</td><td>%.2f</td><td>%s</td></tr>\n' % tuple(t)
    output += u'</tbody></table>\n'
    return output


def monthly_stats(date):
    data = json.load(open('input/blog/monthly.json', 'rb'))
    if date not in data:
        return u'Нет данных за указанный период.'

    columns = [
        ('connection_count', u'Количество <a href="/player.html">подключений</a>', str),
        ('connection_avg', u'Среднее время прослушивания, мин.', lambda x: str(x / 60)),
        ('connection_max', u'<a href="http://files.tmradio.net/pictures/stats/max-listeners/%s.png">Максимальное число одновременных подключений</a>' % re.sub('[^0-9]', '', date), str),
        ('unique_ips', u'<a href="/listeners/#map">Уникальных IP-адресов</a>', str),
        ('track_count', u'Количество дорожек в медиатеке', str),
        ('track_length', u'Общая продолжительность медиатеки, ч.', lambda x: str(x / 3600)),
        ('traffic_stream', u'Трафик от прослушивания, Гб', str),
        ('traffic_total', u'<a href="http://stream.tmradio.net/">Общий трафик</a>, Гб', str),
        ('money_in', u'Пришло <a href="/support/donate/">пожертвований</a>, р.', str),
        ('money_out', u'Потрачено пожертвований, р.', str),
    ]

    output = u'<table class="mstat">\n<tbody>\n'
    for k, h, conv in columns:
        if k in data[date]:
            output += u'<tr><th>%s:</th><td>%s</td></th>\n' % (h, conv(data[date][k]))
    output += u'</tbody>\n</table>\n<p>Эти данные доступны также <a href="/blog/monthly.json">в формате JSON</a> (для машинной обработки).</p>'
    return output

def run(args):
    import subprocess
    subprocess.Popen(args).wait()


def player(page):
    podcast = page.get("file", "")
    if not podcast.lower().endswith(".mp3"):
        return ""

    _ill = page.get("illustration", "http://files.tmradio.net/audio/sosonews/listeners/2011.09.22.png")
    _ill += u" 481 174"

    illustration, width, height = _ill.split(" ")[:3]

    return file("player.html", "rb").read().decode("utf-8") % {
        "width": width,
        "height": height,
        "author": u"Микроша",
        "description": page.get("title"),
        "podcast": podcast,
        "illustration": illustration,
        "duration": page.get("duration", ""),
    }


def navigate(page, pages):
    """Renders the navigation links for the current page, docbook style."""
    _player = player(page)
    if not _player:
        return ""

    links = Navigation(pages).get_page(page)
    if not links:
        return ""

    output = u"<table class='nav'><tbody><tr>"
    if links.get("first"):
        output += u"<td><a href='%s' title='First: %s'><img src='/images/buttons/first.png' alt='first'/></a></td>" % (links["first"]["url"], links["first"]["title"])
    if links.get("prev") and links["prev"]["url"] != links["first"]["url"]:
        output += u"<td><a href='%s' title='Previous: %s'><img src='/images/buttons/prev.png' alt='prev'/></a></td>" % (links["prev"]["url"], links["prev"]["title"])
    if "file" in page:
        output += u"<td width='300'>%s</td>" % _player
        output += u"<td><a href='%s' title='Скачать запись'><img src='/images/buttons/download.png' alt='download'/></a></td>" % page["file"]
    if links.get("next") and links["next"]["url"] != links["last"]["url"]:
        output += u"<td><a href='%s' title='Next: %s'><img src='/images/buttons/next.png' alt='next'/></a></td>" % (links["next"]["url"], links["next"]["title"])
    if links.get("last"):
        output += u"<td><a href='%s' title='Last: %s'><img src='/images/buttons/last.png' alt='last'/></a></td>" % (links["last"]["url"], links["last"]["title"])
    output += u"</tr></tbody></table>"
    return output


def illustration(page):
    if "illustration" not in page:
        return ""
    return u"<img src='%s' title='Иллюстрация к записи' alt='illustration'/>" % page["illustration"]


def format_shownotes(text, title=None):
    if not text.strip():
        return u"Ссылок пока нет."

    if type(text) != unicode:
        text = text.decode("utf-8")

    if title is None:
        title = u"Основные новости"

    output = title + u"\n\n"

    title = link = None
    for line in text.strip().split("\n"):
        if line.startswith("- "):
            title = line[2:].strip()
        else:
            link = line.strip()
            output += u"- [%s](%s)\n" % (title, link)

    return output


def _format_shownote_block(text):
    lines = []

    for line in text.split("\n"):
        if line.startswith("-"):
            lines.append(line)
        elif not lines:
            return text
        elif not lines[-1].startswith("- "):
            return text
        elif not "://" in line:
            return text
        elif not line.startswith("  "):
            return text
        else:
            lines[-1] = "- [%s](%s)" % (lines[-1][2:], line.strip())

    return "\n".join(lines)


def _format_shownotes(text):
    blocks = []
    for block in text.split("\n\n"):
        blocks.append(_format_shownote_block(block))
    return "\n\n".join(blocks)


def hook_preconvert_shownotes():
    for page in pages:
        if "podcast" not in getattr(page, "labels", ""):
            continue
        page.source = _format_shownotes(page.source)
