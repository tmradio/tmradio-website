import logging

from poolemonkey import Config
from util import strip_url


class Labels:
    lst = None

    @classmethod
    def get_all(cls):
        if cls.lst is None:
            cls.lst = {}
            for x in Config.get().get('labels', []):
                cls.lst[x['name']] = x
        return cls.lst

    @classmethod
    def get_url(cls, label):
        return cls.get_all().get(label, {}).get('link')

    @classmethod
    def get_href(cls, label):
        label = cls.get_all().get(label)
        if label is None or not label.get('link'):
            return None
        return u'<a class="tag" href="%s">%s</a>' % (strip_url(label['link']), label.get('title', label))

    @classmethod
    def get_links(cls, labels):
        if not isinstance(labels, (list, tuple)):
            labels = [labels]
        result = []
        for label in labels:
            tmp = cls.get_all().get(label)
            if tmp is not None and tmp.get("link") is not None:
                result.append((strip_url(tmp['link']), tmp.get('title', label)))
        return sorted(result, key=lambda x: x[1].lower())

    @classmethod
    def from_post(cls, post):
        if not 'labels_parsed' in post:
            if 'labels' not in post:
                labels = []
            else:
                labels = [l.strip() for l in post['labels'].split(',')]
            if 'file' in post and post['file'].endswith('.mp3') and 'podcast' not in labels:
                labels.append('podcast')
            if post.url.startswith('blog.') and 'blog' not in labels:
                labels.append('blog')
            post['labels_parsed'] = sorted(labels)
        return post['labels_parsed']


def parse_labels_hook(pages):
    logging.debug("Parsing page labels and sections.")

    sections = Config.get_sections()
    all_labels = Labels.get_all()

    for page in pages:
        labels = []
        if "labels" in page:
            labels = [l.strip() for l in page["labels"].split(",") if l.strip()]
        page["labels_parsed"] = labels

        for section in sections:
            if section in labels:
                page["section"] = all_labels.get(section)
                if page["section"]:
                    break


def find_authors_hook(pages):
    logging.debug("Finding authors for %u pages." % len(pages))

    authors = Config.get_authors()
    if not authors:
        logging.warning("No authors in config.yaml, please add some.")
        authors = [{"name": "nobody", "email": "nobody@example.com", "profile": "http://www.example.com/"}]

    def get_page_author(page):
        author_name = page.get("author", authors[0]["name"])
        for author in authors:
            if author["name"] == author_name:
                return author
        return authors[0]

    for page in pages:
        page["author_info"] = get_page_author(page)


def filter_pages(pages, label, with_dates=False):
    output = []

    for page in pages:
        if with_dates and "date" not in page:
            continue
        if "labels_parsed" not in page:
            print page
        if "photo" in page["labels_parsed"]:
            continue
        if label is not None:
            if label not in page["labels_parsed"]:
                continue
        output.append(page)

    return output


def get_page_section(page):
    """Returns section name for the specified page."""
    return page.get("section")
