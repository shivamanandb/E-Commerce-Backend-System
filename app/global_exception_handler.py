from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from .configuration import logger_config
import logging

logger = logging.getLogger(__name__)

def add_exception_handlers(app):  
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        logging.warning(f"HTTP Exception: {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": True,
                "message": exc.detail,
                "code": exc.status_code
            }
        )
        
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        msg = [error['msg'] for error in exc.errors()]
        logger.error(f"Validation Error: {msg[0]}")
        return JSONResponse(
            status_code=422,
            content={
                "error": True,
                "message":msg[0],
                "code": 422
            }
        )
        
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        logger.exception(f"Unhandled Exception: {exc}")
        return JSONResponse(
            status_code=500,
            content={
                "error": True, 
                "message": "Internal Server Error", 
                "code": 500
            }
        )