#!/usr/bin/env python
# encoding=utf-8

import glob
import os
import re
import subprocess
import sys
import time


MAILTO = "sosonews@googlegroups.com"


def get_pages():
    for path, folders, files in os.walk("input"):
        for fn in files:
            if fn.endswith(".md"):
                yield os.path.join(path, fn)


def get_last_episode():
    yesterday = time.time() - 86400
    prefix = time.strftime("date: %Y-%m-%d 21:", time.localtime(yesterday))

    for fn in get_pages():
        data = file(fn, "rb").read()
        if prefix in data:
            return fn, data


def get_last_episode():
    filename = sorted(glob.glob("input/programs/tsn/*/index.md"))[-1]
    with file(filename, "rb") as f:
        return filename, f.read()


def mail_episode(fn, data):
    mp3s = re.findall("^file: (.*)", data, re.M)
    if not mp3s:
        return

    title = re.findall("^title: (.*)", data, re.M)[0]
    url = "http://www.tmradio.net/" + fn[6:-8]

    head, body = data.split("\n---\n", 1)
    body = body.replace("  /guests/", "  http://www.tmradio.net/guests/")

    message = "Скачать выпуск:\n%s\n\n" % mp3s[0]
    message += "Обсуждение:\n%s\n\n" % url
    message += body

    if "-n" in sys.argv:
        print message
    else:
        p = subprocess.Popen(["mail", "-s", title, MAILTO],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate(message)

        if p.returncode != 0:
            print "Could not send mail: %s" % err
            exit(1)


def main():
    root = os.path.join(os.path.dirname(__file__), "..")
    os.chdir(root)

    last = get_last_episode()
    if last is not None:
        mail_episode(last[0], last[1])


if __name__ == "__main__":
    main()
