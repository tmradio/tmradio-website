# encoding=utf-8

"""RSS ping sender.

Pings several hosts with all your configured feeds.
"""

import cgi
import urllib
import urllib2
import urlparse
import yaml


SERVERS = (
    "http://ping.feedburner.com/",
    "http://blogsearch.google.com/ping",
    "http://rpc.weblogs.com/RPC2",
    "http://audiorpc.weblogs.com/RPC2",
)

XML = u"""<?xml version='1.0' encoding='UTF-8'?>
<methodCall>
    <methodName>weblogUpdates.extendedPing</methodName>
    <params>
        <param><value>%s</value></param>
        <param><value>%s</value></param>
    </params>
</methodCall>"""


def ping_feed(url, feed):
    for server in sorted(SERVERS):
        print "Ping: %s => %s" % (feed["name"], urlparse.urlparse(server).netloc)
        xml = XML % (cgi.escape(feed["title"]), url)
        urllib2.urlopen(server, xml.encode("utf-8"))


def push_feed(server, feed_url):
    data = urllib.urlencode({
        "hub.url": feed_url,
        "hub.mode": "publish",
    })

    server_name = urlparse.urlparse(server).netloc
    feed_name = feed_url.split("/")[-1]

    try:
        urllib2.urlopen(server, data)
        print "Ping: %s => %s" % (feed_name, server_name)
    except (IOError, urllib2.HTTPError), e:
        if hasattr(e, "code") and e.code == 204:
            return
        error = ""
        if hasattr(e, "read"):
            error = e.read()
        print "Ping: %s => %s failed: %s" % (feed_name, server_name, error)


def ping_all_feeds():
    config = yaml.load(file("config.yaml", "rb").read().decode("utf-8"))

    base_url = config.get("base_url")
    if base_url is None:
        return

    feeds = config.get("feeds")
    if feeds is None:
        return

    push = config.get("rss_push")

    for feed in sorted(feeds, key=lambda f: f["name"].lower()):
        url = base_url.rstrip("/") + "/" + feed["name"]
        ping_feed(url, feed)
        if push is not None:
            push_feed(push, url)


ping_all_feeds()
