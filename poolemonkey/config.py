import os
import yaml


class Config:
    data = None
    filename = 'config.yaml'

    @classmethod
    def get(cls):
        if cls.data is None:
            cls.data = os.path.exists(cls.filename) and yaml.load(file(cls.filename)) or {}
        return cls.data

    @classmethod
    def get_authors(cls):
        return cls.get().get("authors", [{
            "name": "alice",
            "email": "alice@example.com",
            "profile": "http://example.com/~alice"
        }])

    @classmethod
    def get_default_author(cls):
        return cls.get().get('author', 'alice@example.com (Alice)')

    @classmethod
    def get_base_url(cls):
        return cls.get().get('base_url', 'http://example.com/').rstrip('/')

    @classmethod
    def get_sections(cls):
        return cls.get().get("sections", [])

    @classmethod
    def get_disqus_id(cls):
        return cls.get().get("disqus_id")

    @classmethod
    def get_flattr_name(cls):
        return cls.get().get("flattr_name")
