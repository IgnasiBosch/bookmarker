from src.bookmarks.extractors.base import Extractor
from src.bookmarks.schemas import Source


class GoogleBooksExtractor(Extractor):
    @property
    def source(self):
        return Source.GOOGLE_BOOKS
