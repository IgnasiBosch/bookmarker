from src.bookmarks.extractors.base import Extractor
from src.bookmarks.schemas import Source


class YoutubeExtractor(Extractor):
    @property
    def source(self):
        return Source.YOUTUBE
