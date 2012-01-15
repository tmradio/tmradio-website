# encoding=utf-8

import lxml.etree
import sys
import time
import urllib2


def get_feedburner_download_counts(uris):
    counts = {}

    if isinstance(uris, (str, unicode)):
        uris = [uris]

    for uri in uris:
        url = "https://feedburner.google.com/api/awareness/1.0/GetItemData?uri=%s&dates=2010-01-01,2012-01-01" % uri
        print >>sys.stderr, "Getting d/l stats for %s" % uri

        data = urllib2.urlopen(url).read()
        for item in lxml.etree.fromstring(data).xpath("//item"):
            url, count = item.get("url"), item.get("downloads")
            if count:
                if url not in counts:
                    counts[url] = 0
                counts[url] += int(count)

    return counts


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print "Usage: %s output.csv uri..." % sys.argv[0]
        exit(1)

    for url, count in sorted(get_feedburner_download_counts(sorted(sys.argv[1:])).items()):
        print "%s,%u" % (url, count)
