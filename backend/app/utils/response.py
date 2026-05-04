from typing import Any

from pydantic import BaseModel


class StandardResponse(BaseModel):
    success: bool
    data: Any = None
    message: str = ""


def success_response(data: Any = None, message: str = "ok") -> dict[str, Any]:
    return {"success": True, "data": data, "message": message}


def error_response(message: str = "error", data: Any = None) -> dict[str, Any]:
    return {"success": False, "data": data, "message": message}
