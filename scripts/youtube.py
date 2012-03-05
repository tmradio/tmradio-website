#!/usr/bin/env python
# vim: set fileencoding=utf-8 tw=0:

"""YouTube extension for Poole.

Replaces YouTube links with players.
"""

import re


PATTERN = '<iframe width="560" height="315" ' \
    'src="http://www.youtube.com/embed/%s" frameborder="0" ' \
    'allowfullscreen></iframe>'


def get_video_id_from_url(url):
    url = url.replace("&amp;", "&")
    for part in url.split("?", 1)[1].split("&"):
        if part.startswith("v="):
            return part[2:]
    return None


def hook_html_youtube(html, page):
    for m in re.finditer("<p>(http://(www\.)?(youtube\.com|youtu\.be)/[^<]+)</p>", html):
        video_id = get_video_id_from_url(m.group(1))
        if video_id is not None:
            html = html.replace(m.group(0), PATTERN % video_id)
    return html


__all__ = ["hook_html_youtube"]
