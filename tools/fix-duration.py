#!/usr/bin/env python
# encoding=utf-8

"""This script find pages with audio files but without duration, downloads the
media and adds the duration header."""

import httplib
import os
import urllib
import urlparse
import tempfile

import mad

from poolemonkey.pagelist import Page


def get_audio_url(filename):
    head = file(filename, "rb").read().decode("utf-8").split("\n---\n", 1)[0]

    lines = head.strip().split("\n")
    items = dict([l.split(":", 1) for l in lines])

    if "duration" in items:
        return None
    if "file" not in items:
        return None
    if not items["file"].strip().endswith(".mp3"):
        return None
    return items["file"].strip()


def find_pages(folder):
    output = {}

    for path, folders, files in os.walk(folder):
        for filename in files:
            if filename.endswith(".md"):
                filepath = os.path.join(path, filename)
                output[filepath] = Page(filepath)

    return output


def get_file_size_from_url(url):
    print "Looking for length of %s" % url

    parts = urlparse.urlparse(url)

    conn = httplib.HTTPConnection(parts.netloc)
    conn.request("HEAD", parts.path)
    res = conn.getresponse()

    if res.status != 200:
        return None

    return res.getheader("content-length")


def get_duration_from_url(url):
    print "Downloading %s" % url

    tmp = tempfile.mktemp(suffix=".mp3")

    try:
        file(tmp, "wb").write(urllib.urlopen(url).read())
        return int(mad.MadFile(tmp).total_time() / 1000)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def add_duration(filename, duration):
    data = file(filename, "rb").read()
    data = "duration: %u\n%s" % (duration, data)
    file(filename, "wb").write(data)


pages = find_pages("input")
for filename, page in sorted(pages.items()):
    if "file" not in page:
        continue

    if not page["file"].endswith(".mp3"):
        continue

    update = False

    if "filesize" not in page:
        page["filesize"] = get_file_size_from_url(page["file"])
        if page["filesize"] is not None:
            update = True

    if "duration" not in page:
        page["duration"] = get_duration_from_url(page["file"])
        update = True

    if update:
        page.save()
