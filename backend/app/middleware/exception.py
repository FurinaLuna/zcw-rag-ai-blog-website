from fastapi import Request, HTTPException, status
from loguru import logger


async def exception_handler_middleware(request: Request, call_next):
    try:
        response = await call_next(request)
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unhandled exception: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"success": False, "message": "Internal server error", "data": None},
        )
