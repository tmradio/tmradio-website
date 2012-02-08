# encoding=utf-8

from macros import get_config, strip_url, get_page_labels


def _page_has_comments(html, page):
    return '<div id="disqus_thread">' in html


def _add_header(html, page, disqus_id):
    base_url = get_config("base_url")

    disqus_url = page.get("disqus_url", base_url + strip_url("/" + page.url))

    settings = ''
    settings += u"var disqus_url = '%s'; " % page.get("disqus_url", disqus_url)
    settings += u"var disqus_shortname = '%s'; " % disqus_id
    settings += u"var disqus_identifier = '%s'; " % page.url
    settings += u"var disqus_developer = (window.location.href.indexOf('http://localhost:') == 0); "
    settings += u"var disqus_title = '%s'; " % page["title"]

    header = "<script type='text/javascript'>%s</script>\n" % settings.strip()
    html = html.replace("</head>", header + "</head>")
    return html


def _add_body(html, page, disqus_id):
    base_url = get_config("base_url")
    disqus_url = page.get("disqus_url", base_url + strip_url("/" + page.url))

    if _page_has_comments(html, page):
        script_url = "http://%s.disqus.com/embed.js" % disqus_id
    elif '#disqus_thread' in page.html:
        script_url = "http://%s.disqus.com/count.js" % disqus_id
    else:
        return html

    script = '<script type="text/javascript"> (function() { var dsq = document.createElement(\'script\'); dsq.type = \'text/javascript\'; dsq.async = true; dsq.src = \'%s\'; (document.getElementsByTagName(\'head\')[0] || document.getElementsByTagName(\'body\')[0]).appendChild(dsq); })();</script>' % script_url
    return html.replace("</body>", script + "</body>")


def hook_html_disqus(html, page):
    disqus_id = get_config("disqus_id")
    if disqus_id:
        html = _add_header(html, page, disqus_id)
        html = _add_body(html, page, disqus_id)
    return html


__all__ = ["hook_html_disqus"]
