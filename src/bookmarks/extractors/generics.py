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




