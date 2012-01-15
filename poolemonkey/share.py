# encoding=utf-8

"""Adds share buttons to certain pages."""


import urllib

from config import Config


def get_buttons(page):
    """Returns buttons for this page."""
    conf = Config.get()

    if not conf.get("buttons"):
        return ""

    need_labels = conf["buttons"]["labels"]
    if not set(need_labels) & set(page["labels_parsed"]):
        return ""

    output = u""
    for item in conf["buttons"]["items"]:
        category = page.get("category", "text")
        if "podcast" in page["labels_parsed"]:
            category = "audio"
        elif "video" in page["labels_parsed"]:
            category = "video"

        link = item["link"] % {
            "url": urllib.quote(conf["base_url"].rstrip("/") + "/" + page["url"].replace("/index.html", "/")),
            "title": urllib.quote(page.get("title").encode("utf-8")),
            "image": urllib.quote(page.get("illustration", "")),
            "summary": page.get("summary", ""),
            "labels": u",".join(page["labels_parsed"]),
            "category": category,
        }

        output += u"<a class='%(type)s' href='%(url)s' title='%(title)s' target='_blank'><span>%(caption)s</span></a>" % {
            "type": item["type"],
            "url": link,
            "title": item["title"],
            "caption": item.get("caption", item.get("title", item.get("type"))),
        }

    if len(output):
        output = u"<div class='share_buttons'><span>%(prefix)s</span>%(buttons)s</div>" % {
            "prefix": conf["buttons"].get("prefix", ""),
            "buttons": output,
        }
    return output
