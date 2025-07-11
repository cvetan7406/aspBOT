import logging
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


class ASPBotException(Exception):
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class DocumentProcessingError(ASPBotException):
    def __init__(self, message: str):
        super().__init__(message, status_code=500)


class VectorStoreError(ASPBotException):
    def __init__(self, message: str):
        super().__init__(message, status_code=500)


class SpeechProcessingError(ASPBotException):
    def __init__(self, message: str):
        super().__init__(message, status_code=500)


class WakeWordError(ASPBotException):
    def __init__(self, message: str):
        super().__init__(message, status_code=500)


class RAGError(ASPBotException):
    def __init__(self, message: str):
        super().__init__(message, status_code=500)


class NoRelevantDocumentsError(ASPBotException):
    def __init__(self):
        super().__init__(
            "No relevant documents found for the query", 
            status_code=404
        )


async def asp_bot_exception_handler(request: Request, exc: ASPBotException):
    logger.error(f"ASP Bot exception: {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message},
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    logger.error(f"HTTP exception: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()},
    )


def register_exception_handlers(app):
    app.add_exception_handler(ASPBotException, asp_bot_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)