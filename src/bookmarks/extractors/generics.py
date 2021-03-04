from src.bookmarks.extractors.base import Extractor
from src.bookmarks.schemas import Source


class GenericExtractor(Extractor):
    @property
    def source(self):
        return Source.OTHER


class UndefinedExtractor(Extractor):
    @property
    def source(self):
        return Source.UNDEFINED


class ImageExtractor(Extractor):
    @property
    def source(self):
        return Source.IMAGE

    @property
    def image_url(self):
        return self.url
