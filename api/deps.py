# from typing import Generator

# from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
# from jose import jwt
# from sqlalchemy.orm import Session

from core.config import settings
# from db.session import SessionLocal


# reusable_oauth2 = OAuth2PasswordBearer(
#     tokenUrl=f"{settings.API_V1_STR}/login/access-token"
# )

