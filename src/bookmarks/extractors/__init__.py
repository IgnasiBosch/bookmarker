import logging
from typing import Dict, Type

from bs4 import BeautifulSoup

from src.bookmarks.extractors.base import Extractor
from src.bookmarks.extractors.generics import (
    GenericExtractor,
    ImageExtractor,
    UndefinedExtractor,
)
from src.bookmarks.extractors.github import GithubExtractor
from src.bookmarks.extractors.google_books import GoogleBooksExtractor
from src.bookmarks.extractors.medium import MediumExtractor
from src.bookmarks.extractors.youtube import YoutubeExtractor
from src.bookmarks.schemas import Source

extractors: Dict[Source, Type[Extractor]] = {
    Source.MEDIUM: MediumExtractor,
    Source.GITHUB: GithubExtractor,
    Source.GOOGLE_BOOKS: GoogleBooksExtractor,
    Source.IMAGE: ImageExtractor,
    Source.OTHER: GenericExtractor,
    Source.UNDEFINED: UndefinedExtractor,
    Source.YOUTUBE: YoutubeExtractor,
}


logger = logging.getLogger(__name__)


def get_source(page: BeautifulSoup, content_type: str, url: str) -> Source:
    if "image" in content_type:
        logger.debug(f"IMAGE source: {url}")
        return Source.IMAGE
    source = Extractor.get_attr_or_none(
        page.find(attrs={"property": "og:site_name"}), "content"
    )
    if source is None:
        logger.debug(f"UNDEFINED source: {url}")
        return Source.UNDEFINED

    try:
        source = Source(source.lower())
        logger.debug(f"{source} source: {url}")
        return source

    except Exception:
        logger.debug(f"OTHER source: {url}")
        return Source.OTHER


def extractor_factory(url: str, content: str, content_type: str) -> Extractor:
    page = BeautifulSoup(content, "html.parser")
    source = get_source(page, content_type, url)
    extractor = extractors[source]

    return extractor(url=url, page=page)
