from src.bookmarks.extractors.base import Extractor
from src.bookmarks.schemas import Source


class MediumExtractor(Extractor):
    @property
    def source(self):
        return Source.MEDIUM
