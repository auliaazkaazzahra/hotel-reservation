from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from ...config import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class JWTHandler:
    """
    Handler untuk operasi JWT (encode/decode token)
    """

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verifikasi password"""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        """Hash password"""
        return pwd_context.hash(password)

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """
        Buat JWT access token

        Args:
            data: Data yang akan di-encode (biasanya {"sub": username})
            expires_delta: Durasi token valid

        Returns:
            JWT token string
        """
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

        return encoded_jwt

    @staticmethod
    def decode_access_token(token: str) -> Optional[str]:
        """
        Decode JWT token dan ambil username

        Args:
            token: JWT token string

        Returns:
            Username jika valid, None jika invalid
        """
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            username: str = payload.get("sub")

            if username is None:
                return None

            return username

        except JWTError:
            return None
