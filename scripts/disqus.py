# encoding=utf-8

from macros import get_config, strip_url


def hook_html_disqus(html, page):
    disqus_id = get_config("disqus_id")
    if disqus_id:
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


__all__ = ["hook_html_disqus"]
