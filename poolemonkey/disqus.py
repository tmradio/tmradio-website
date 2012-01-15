# encoding=utf-8

import logging

from config import Config
from util import strip_url


def _page_has_comments(page):
    labels = Config.get().get("comment_labels", [])
    if not labels:
        return False
    if not set(page["labels_parsed"]) & set(labels):
        return False
    return True

def get_extra_headers(page):
    disqus_id = Config.get().get("disqus_id")
    if not disqus_id:
        return ""

    base_url = Config.get_base_url()
    disqus_url = page.get("disqus_url", base_url + strip_url("/" + page.url))

    settings = ''
    settings += u"var disqus_url = '%s'; " % page.get("disqus_url", disqus_url)
    settings += u"var disqus_shortname = '%s'; " % disqus_id
    settings += u"var disqus_identifier = '%s'; " % page.url
    settings += u"var disqus_developer = (window.location.href.indexOf('http://localhost:') == 0); "
    settings += u"var disqus_title = '%s'; " % page["title"]

    return "<script type='text/javascript'>%s</script>\n" % settings.strip()


def get_extra_footers(page):
    disqus_id = Config.get().get("disqus_id")
    if not disqus_id:
        return ""

    base_url = Config.get_base_url()
    disqus_url = page.get("disqus_url", base_url + strip_url("/" + page.url))

    if _page_has_comments(page):
        script_url = "http://%s.disqus.com/embed.js" % disqus_id
    elif '#disqus_thread' in page.html:
        script_url = "http://%s.disqus.com/count.js" % disqus_id
    else:
        return ""

    return '<script type="text/javascript"> (function() { var dsq = document.createElement(\'script\'); dsq.type = \'text/javascript\'; dsq.async = true; dsq.src = \'%s\'; (document.getElementsByTagName(\'head\')[0] || document.getElementsByTagName(\'body\')[0]).appendChild(dsq); })();</script>' % script_url


def enable_comments(page):
    page.html = page.html.replace("</body>", get_extra_headers(page) + "</body>")


def get_comment_form(page):
    if not Config.get().get("disqus_id"):
        return ""

    if not _page_has_comments(page):
        return ""

    return '<div id="disqus_thread"></div>'


def enable_comments_hook(pages):
    disqus_id = Config.get().get("disqus_id")
    if not disqus_id:
        logging.debug("Not enabling disqus: disqus_id not set.")
        return

    logging.info("Enabling disqus for %u pages (account name: %s)." % (len(pages), disqus_id))
    for page in pages:
        enable_comments(page)
