from datetime import datetime, timezone
from typing import Optional

from bs4 import Tag, BeautifulSoup

from src.bookmarks.schemas import Bookmark


class Extractor:
    def __init__(self, url: str, page: BeautifulSoup):
        self.url = url
        self.page = page

    @staticmethod
    def get_attr_or_none(tag: Optional[Tag], attr: str) -> Optional[str]:
        if tag is None:
            return None

        return tag.get(attr)

    @property
    def title(self):
        return self.get_attr_or_none(
            self.page.find(attrs={"property": "og:title"}), "content"
        )

    @property
    def description(self):
        desc = self.get_attr_or_none(
            self.page.find(attrs={"property": "og:description"}), "content"
        )

        return desc[:500] if desc else desc

    @property
    def image_url(self):
        return self.get_attr_or_none(
            self.page.find(attrs={"property": "og:image"}), "content"
        )

    @property
    def author(self):
        return self.get_attr_or_none(
            self.page.find(attrs={"name": "author"}), "content"
        ) or self.get_attr_or_none(
            self.page.find(attrs={"name": "twitter:creator"}), "content"
        )

    @property
    def source(self):
        raise NotImplemented

    def to_bookmark(self):
        return Bookmark(
            title=self.title,
            url=self.url,
            source=self.source,
            author=self.author,
            description=self.description,
            image_url=self.image_url,
            last_fetch_at=datetime.now(timezone.utc),
            failed_attemtps=0,
        )
