# encoding=utf-8

import glob
import os
import re
import time
from urllib import quote
from xml.sax.saxutils import escape

from config import Config


def get_new_page(prefix, template):
    root = os.path.dirname(os.path.dirname(__file__))

    existing = glob.glob(os.path.join(root, "input", prefix, "*", "index.md"))
    ids = [int(fn.split(os.path.sep)[-2]) for fn in existing] + [0]
    next_id = max(ids) + 1

    folder = os.path.join(root, "input", prefix, str(next_id))
    if not os.path.exists(folder):
        os.mkdir(folder)

    template = template.replace("{id}", str(next_id))

    filename = os.path.join(folder, "index.md")
    file(filename, "wb").write(template.encode("utf-8"))

    return filename


def edit_file(filename):
    subprocess.Popen(["vim", filename]).wait()


def page_url(page):
    base_url = Config.get().get("base_url")
    if not base_url:
        raise Exception("config.yaml does not define base_url")
    return (base_url.rstrip("/") + "/" + page.url).replace("/index.html", "/")


def get_page_author(page):
    return page["author_info"]


def strip_url(url):
    if url.endswith('/index.html'):
        url = url[:-10]
    return url


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


def fix_typo_hook(pages):
    r = re.compile(u'  +')
    for page in pages:
        html = page.html
        html = html.replace("\n  ", " ")  # new line in a list
        html = html.replace(u' —', u'&nbsp;—')
        html = html.replace(u'. ', u'.&nbsp; ')
        html = html.replace(u'? ', u'?&nbsp; ')
        html = html.replace(u'! ', u'!&nbsp; ')
        html = r.sub(u'&nbsp; ', html)
        page.html = html


def get_file_player(url, downloadable=True):
    html = u'<object type="application/x-shockwave-flash" data="/files/player.swf" width="200" height="20"><param name="movie" value="/files/player.swf"/><param name="bgcolor" value="#eeeeee"/><param name="FlashVars" value="mp3=%s&amp;buttoncolor=000000&amp;slidercolor=000000&amp;loadingcolor=808080"/></object>' % quote(url)
    if downloadable:
        html += u" или <a href='%s'>скачать файл</a>" % url
    return u"<div class='player'>%s</div>" % html


def get_player(page):
    if "file" in page and page["file"].endswith(".mp3"):
        return get_file_player(page["file"])
    return ""
