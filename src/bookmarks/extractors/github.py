from src.bookmarks.extractors.base import Extractor
from src.bookmarks.schemas import Source


class GithubExtractor(Extractor):
    @property
    def source(self):
        return Source.GITHUB

    @property
    def title(self):
        return self.get_attr_or_none(
            self.page.find(attrs={"property": "og:title"}), "content"
        ).split("/")[1]

    @property
    def author(self):
        return self.get_attr_or_none(
            self.page.find(attrs={"property": "og:title"}), "content"
        ).split("/")[0]

    @property
    def image_url(self):
        return "https://clickhelp.com/images/feeds/blog/2018.06/hero_github.png"
