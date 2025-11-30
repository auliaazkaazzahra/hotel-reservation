from typing import Dict, Optional
from dataclasses import dataclass

from .jwt_handler import JWTHandler


@dataclass
class User:
    """
    Simple User model untuk autentikasi
    """
    username: str
    email: str
    full_name: str
    hashed_password: str
    is_active: bool = True


class UserRepository:
    """
    Repository untuk User (in-memory storage)
    Untuk production, ganti dengan database
    """
    
    def __init__(self):
        self._users: Dict[str, User] = {}
        self._initialize_default_users()
    
    def _initialize_default_users(self):
        """Buat default users untuk testing"""
        # User: admin / admin123
        self.create_user(
            username="admin",
            email="admin@hotel.com",
            full_name="Hotel Administrator",
            password="admin123"
        )
        
        # User: user / user123
        self.create_user(
            username="user",
            email="user@hotel.com",
            full_name="Regular User",
            password="user123"
        )
    
    def create_user(self, username: str, email: str, full_name: str, password: str) -> User:
        """Buat user baru"""
        if username in self._users:
            raise ValueError(f"Username {username} already exists")
        
        hashed_password = JWTHandler.get_password_hash(password)
        
        user = User(
            username=username,
            email=email,
            full_name=full_name,
            hashed_password=hashed_password
        )
        
        self._users[username] = user
        return user
    
    def get_user(self, username: str) -> Optional[User]:
        """Ambil user berdasarkan username"""
        return self._users.get(username)
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """
        Autentikasi user
        
        Returns:
            User object jika valid, None jika invalid
        """
        user = self.get_user(username)
        
        if not user:
            return None
        
        if not JWTHandler.verify_password(password, user.hashed_password):
            return None
        
        return user