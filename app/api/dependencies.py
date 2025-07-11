import logging
from typing import Generator

from fastapi import Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordBearer

from app.core.security import get_current_active_user, get_current_active_superuser
from app.models.schemas import User
from app.config import settings

logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_user_dependency():
    return get_current_active_user


def get_superuser_dependency():
    return get_current_active_superuser


def get_api_key_header_dependency():
    async def validate_api_key(x_api_key: str = Header(...)):
        if x_api_key != settings.API_KEY:
            logger.warning("Authentication failed: Invalid API key provided")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key",
            )
        return x_api_key
    
    return validate_api_key