from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel

from ..config import settings
from ..infrastructure.auth import JWTHandler, User, UserRepository

# Router
router = APIRouter(prefix="/api/auth", tags=["Authentication"])

# User repository (singleton)
user_repo = UserRepository()

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


# DTOs
class Token(BaseModel):
    """Response DTO untuk token"""

    access_token: str
    token_type: str


class UserResponse(BaseModel):
    """Response DTO untuk user info"""

    username: str
    email: str
    full_name: str


class RegisterRequest(BaseModel):
    """Request DTO untuk registrasi"""

    username: str
    email: str
    full_name: str
    password: str


# Endpoints


@router.post("/login", response_model=Token, summary="Login User")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Login endpoint - menggunakan OAuth2 password flow

    Username dan password dikirim via form data:
    - username: admin
    - password: admin123
    """
    user = user_repo.authenticate_user(form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Buat access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = JWTHandler.create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED, summary="Register User")
async def register(request: RegisterRequest):
    """
    Register new user
    """
    try:
        user = user_repo.create_user(
            username=request.username, email=request.email, full_name=request.full_name, password=request.password
        )

        return UserResponse(username=user.username, email=user.email, full_name=user.full_name)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/me", response_model=UserResponse, summary="Get Current User")
async def get_current_user_info(token: str = Depends(oauth2_scheme)):
    """
    Get current logged in user info
    """
    username = JWTHandler.decode_access_token(token)

    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = user_repo.get_user(username)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return UserResponse(username=user.username, email=user.email, full_name=user.full_name)
