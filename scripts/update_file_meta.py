# encoding=utf-8
"""Adds missing file sizes and MP3 file duration."""

import os
import sys
import tempfile
import urllib2

try:
    import mad
    HAVE_MAD = True
except ImportError:
    HAVE_MAD = False


def get_filesize(url):
    try:
        req = urllib2.Request(url)
        req.get_method = lambda: "HEAD"
        res = urllib2.urlopen(req)
        return int(res.headers["content-length"])
    except:
        raise Exception("could not fetch %s" % url)


def get_duration(url):
    ext = os.path.splitext(url)[1]
    if ext != ".mp3":
        return None

    tmp = tempfile.mktemp(suffix=ext)

    try:
        req = urllib2.urlopen(url)
        file(tmp, "wb").write(req.read())
        return int(mad.MadFile(tmp).total_time() / 1000)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def process_page(filepath):
    file_idx = filesize_idx = duration_idx = None

    lines = file(filepath, "rb").read().split("\n")
    for idx, line in enumerate(lines):
        if "---" == line:
            break
        if line.startswith("file:"):
            file_idx = idx
        elif line.startswith("filesize:"):
            filesize_idx = idx
        elif line.startswith("duration:"):
            duration_idx = idx

    if file_idx is None:
        return

    url = lines[file_idx][5:].strip()

    try:
        if filesize_idx is None:
            filesize = get_filesize(url)
            if filesize is not None:
                print "%s: adding filesize %u" % (filepath, filesize)
                lines.insert(file_idx + 1, "filesize: %u" % filesize)

        if duration_idx is None:
            duration = get_duration(url)
            if duration is not None:
                print "%s: adding duration %u" % (filepath, duration)
                lines.insert(file_idx + 1, "duration: %u" % duration)

        file(filepath, "wb").write("\n".join(lines))
    except Exception, e:
        print "%s: %s" % (filepath, e)


def process_all_pages():
    for path, folders, filenames in os.walk("input"):
        for filename in filenames:
            if not filename.endswith(".md"):
                continue
            filepath = os.path.join(path, filename)
            process_page(filepath)


if __name__ == "__main__":
    process_all_pages()
