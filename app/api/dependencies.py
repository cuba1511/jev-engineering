from fastapi import Request

from app.jev import Jev


def get_jev(request: Request) -> Jev:
    return request.app.state.jev
