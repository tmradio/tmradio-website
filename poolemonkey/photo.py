# encoding=utf-8

import cgi
import logging
import os
import re
import shutil
import subprocess
import time

from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

import poolemonkey.util
from pagelist import Page


class Exif(dict):
    def __init__(self, filename):
        super(Exif, self).__init__()

        info = Image.open(filename)
        if info is None:
            return

        exif = info._getexif()
        if exif is None:
            return

        tags = {}
        for tag, value in exif.items():
            name = TAGS.get(tag, None)
            if name is None:
                continue
            if isinstance(value, (str, unicode)) and len(value) > 100:
                continue
            if name == "GPSInfo":
                gps_data = {}
                for t in value:
                    tmp = GPSTAGS.get(t, t)
                    gps_data[tmp] = value[t]

                self["Latitude"] = self.get_ll(gps_data, "Latitude")
                self["Longitude"] = self.get_ll(gps_data, "Longitude")

                value = gps_data
            self[name] = value

    def gps_to_deg(self, value):
        d0 = value[0][0]
        d1 = value[0][1]
        d = float(d0) / float(d1)

        m0 = value[1][0]
        m1 = value[1][1]
        m = float(m0) / float(m1)

        s0 = value[2][0]
        s1 = value[2][1]
        s = float(s0) / float(s1)

        return d + (m / 60.0) + (s / 3600.0)

    def get_ll(self, data, k):
        k1 = "GPS" + k
        k2 = "GPS" + k + "Ref"

        if k1 in data and k2 in data:
            tmp = self.gps_to_deg(data[k1])
            if data[k2] != "N":
                tmp = 0 - tmp
            return tmp


def prepare_photos_hook(pages):
    logging.debug("Preparing photos.")
    r = re.compile("photo/\d+/index\.html")

    for page in pages:
        if r.match(page["url"]):
            p = Page(page["fname"])
            update = False

            if "file" not in p.props:
                filename = page["fname"][:-8] + "source.jpg"
                if os.path.exists(filename):
                    page["file"] = p.props["file"] = filename[8:]
                    page["filesize"] = p.props["filesize"] = str(os.stat(filename).st_size)
                    update = True

            if update:
                print "file* %s" % p.filename
                p.save()

            if "thumbnail" in page:
                embed = "![photo](%s)" % page["thumbnail"]
                if embed not in page.source:
                    page.source = embed + u"\n\n" + page.source


def create_versions(filename):
    """Creates a medium (x1000) and a small (75x75) version of the picture.
    Updates them if the source file changed."""
    medium = filename.replace("source.jpg", "medium.jpg")
    if not os.path.exists(medium) or os.stat(filename).st_mtime > os.stat(medium).st_mtime:
        print "file+ %s" % medium
        subprocess.Popen(["convert", filename, "-auto-orient", "-resize", "1000>", medium]).wait()

    small = filename.replace("source.jpg", "small.jpg")
    if not os.path.exists(small) or os.stat(filename).st_mtime > os.stat(small).st_mtime:
        print "file+ %s" % small
        subprocess.Popen(["convert", filename, "-auto-orient", "-thumbnail", "x150", "-resize", "150x<", "-resize", "50%", "-gravity", "center", "-crop", "75x75+0+0", "-sharpen", "1.5x1.2+1.0+0.10", "+repage", "-quality", "91", small]).wait()


def add_photo(filename):
    """Creates a new page for the specified file, copies it to its new folder."""
    page = Page.from_dict({
        "title": os.path.basename(filename),
        "date": time.strftime("%Y-%m-%d %H:%M"),
        "labels": os.environ.get("LABELS", "photo"),
        "file": "photo/{id}/source.jpg",
        "thumbnail": "photo/{id}/medium.jpg",
        "#text": u"Описание отсутствует.",
    })

    metaname = os.path.splitext(filename)[0] + ".yaml"
    if os.path.exists(metaname):
        tmp = umonkey.Page(metaname)
        if "title" in tmp.props:
            page["title"] = tmp.props["title"]
        if tmp.props.get("#text"):
            page["#text"] = tmp.props["#text"]

    exif = Exif(filename)
    if "DateTime" in exif:
        page["date"] = time.strftime("%Y-%m-%d %H:%M", time.strptime(exif["DateTime"], "%Y:%m:%d %H:%M:%S"))
    if "Latitude" in exif and "Longitude" in exif:
        page["location"] = "%s,%s" % (exif["Latitude"], exif["Longitude"])

    contents = page.dump()
    pagename = poolemonkey.util.get_new_page("photo", contents)
    picture = pagename.replace("index.md", "source.jpg")
    shutil.copy(filename, picture)
    create_versions(picture)

    if os.path.exists(metaname):
        shutil.copy(metaname, pagename.replace("index.md", "metadata.yaml"))

    return pagename


def album(pages, label, reverse=False):
    """Renders a photoalbum from pages with the specified label."""
    photo_pages = []
    for page in pages:
        if "thumbnail" not in page:
            continue
        labels = page.get("labels_parsed", [])
        if label in labels and "draft" not in labels and "queue" not in labels:
            photo_pages.append(page)

    if not photo_pages:
        return ""

    photo_pages.sort(key=lambda p: p["date"], reverse=reverse)

    output = u"<div class='photoalbum'><ul>"
    for page in photo_pages:
        output += u"<li><a href='/%(href)s' title='%(title)s'><img src='/%(src)s' alt='image'/></a></li>" % {
            "src": cgi.escape(page["thumbnail"].replace("medium.jpg", "small.jpg")),
            "href": page["url"].replace("index.html", ""),
            "title": cgi.escape(page["title"]),
        }
    return output + u"</ul><div class='break'></div></div>"


def trip_report(pages, photo_ids):
    output = u""
    for photo_id in photo_ids:
        url = "photo/%s/index.html" % photo_id
        for page in pages:
            if page["url"] == url:
                embed = "![photo](%s)" % page["thumbnail"]
                contents = page.source.replace(embed, "").strip() + "\n\n" + embed + "\n\n"
                output += contents
    return output
