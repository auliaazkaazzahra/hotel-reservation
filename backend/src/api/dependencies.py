from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from ..infrastructure.auth import JWTHandler, UserRepository, User

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# User repository
user_repo = UserRepository()


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """
    Dependency untuk mendapatkan current user dari JWT token
    
    Digunakan untuk protect endpoints yang memerlukan autentikasi
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    username = JWTHandler.decode_access_token(token)
    
    if username is None:
        raise credentials_exception
    
    user = user_repo.get_user(username)
    
    if user is None:
        raise credentials_exception
    
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Dependency untuk memastikan user active
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    return current_user