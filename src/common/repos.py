import math

from src.common.schemas import PaginationResult

MAX_ITEMS_PER_PAGE = 10000


def get_pagination(
    current_page: int,
    items_per_page: int,
    total_num_items: int,
):
    current_page = current_page
    previous_page = None
    next_page = None
    has_previous = current_page > 1
    total_num_items = total_num_items
    total_num_pages = int(math.ceil(total_num_items / float(items_per_page)))
    items_per_page = items_per_page
    has_next = current_page < total_num_pages
    if has_previous:
        previous_page = current_page - 1
    if has_next:
        next_page = current_page + 1

    return PaginationResult(
        items_per_page=items_per_page,
        current_page=current_page,
        previous_page=previous_page,
        next_page=next_page,
        has_previous=has_previous,
        has_next=has_next,
        total_num_items=total_num_items,
        total_num_pages=total_num_pages,
    )
