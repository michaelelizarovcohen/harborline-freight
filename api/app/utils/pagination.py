from flask import request

DEFAULT_PAGE_SIZE = 25
MAX_PAGE_SIZE = 100


def page_params() -> tuple[int, int]:
    try:
        page = max(int(request.args.get("page", 1)), 1)
    except ValueError:
        page = 1
    try:
        size = int(request.args.get("per_page", DEFAULT_PAGE_SIZE))
    except ValueError:
        size = DEFAULT_PAGE_SIZE
    return page, min(max(size, 1), MAX_PAGE_SIZE)


def paginate(query, serializer=lambda obj: obj.to_dict()) -> dict:
    page, size = page_params()
    total = query.count()
    items = query.offset((page - 1) * size).limit(size).all()
    return {
        "items": [serializer(i) for i in items],
        "page": page,
        "per_page": size,
        "total": total,
        "pages": (total + size - 1) // size,
    }
