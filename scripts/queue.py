# encoding=utf-8
"""Delayed publishing for Poole.

This script finds all pages in the input/ folder that have the 'queue' label
and removes the label from one of them, thus publishing it.  Pages with the
'draft' label are ignored.

If a page has a date -- it will be published as soon as that date comes,
otherwise the page will be published as soon as possible.

Example of publishing a random page three times a week, except for weekends,
using cron:

    0 12,16,20 * * 0-5 make -C ~/website process-queue commit
"""

import os
import random
import re
import time


def parse_page(filename):
    """Returns page contents with the "queue" label removed or None, if the
    page can't be published."""
    date = None
    labels_idx = None

    lines = file(filename, "rb").read().split("\n")
    for idx, line in enumerate(lines):
        if line == "---":
            break
        if line.startswith("labels:"):
            labels_idx = idx
        elif line.startswith("date:"):
            date = line[5:].strip()

    if date is not None:
        default_date = "0000-00-00 00:00"
        date = (date + default_date[len(date):])[:len(default_date)]
        if date > time.strftime("%Y-%m-%d %H:%M"):
            return None

    if labels_idx is None:
        return None

    labels = re.split(",\s+", lines[labels_idx][7:].strip())
    if "draft" in labels:
        return None
    if "queue" not in labels:
        return None

    labels.remove("queue")
    if not labels:
        del lines[labels_idx]
    else:
        lines[labels_idx] = "labels: %s" % ", ".join(labels)

    return "\n".join(lines)


def find_pending_pages():
    """Returns a dictionary of pages that can be published.  Keys are file
    names, values are contents that needs to be written to that file to publish
    the page."""
    pending = {}

    for path, folders, filenames in os.walk("input"):
        for filename in filenames:
            if not filename.endswith(".md"):
                continue
            filepath = os.path.join(path, filename)
            page = parse_page(filepath)
            if page is None:
                continue
            pending[filepath] = page

    return pending


def publish_random_page(pages):
    if not pages:
        return

    filename = random.choice(pages.keys())
    file(filename, "wb").write(pages[filename])
    print "Published %s" % filename


if __name__ == "__main__":
    publish_random_page(find_pending_pages())
