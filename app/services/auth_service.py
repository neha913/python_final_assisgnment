from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import settings
from app.repositories.user_repository import UserRepository
from app.schemas import TokenData
from app.models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    def __init__(self, session: AsyncSession):
        self.user_repo = UserRepository(session)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
        return encoded_jwt

    @staticmethod
    def verify_token(token: str) -> Optional[TokenData]:
        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
            email: str = payload.get("sub")
            user_id: int = payload.get("user_id")
            role_str: str = payload.get("role")
            if email is None or user_id is None or role_str is None:
                return None
            # Convert string role to UserRole enum for TokenData
            from app.models import UserRole
            try:
                role = UserRole(role_str)
            except ValueError:
                return None
            return TokenData(email=email, user_id=user_id, role=role)
        except JWTError:
            return None

    async def register(self, email: str, password: str, role: str, name: str) -> User:
        # Check if user already exists
        existing_user = await self.user_repo.get_by_email(email)
        if existing_user:
            raise ValueError("User with this email already exists")

        # Convert string role to UserRole enum
        from app.models import UserRole
        try:
            user_role = UserRole(role)
        except ValueError:
            raise ValueError(f"Invalid role: {role}. Must be 'Doctor' or 'Patient'")

        password_hash = self.get_password_hash(password)
        user = await self.user_repo.create(email, password_hash, user_role, name)
        return user

    async def login(self, email: str, password: str) -> Optional[str]:
        user = await self.user_repo.get_by_email(email)
        if not user:
            return None

        if not self.verify_password(password, user.password_hash):
            return None

        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = self.create_access_token(
            data={"sub": user.email, "user_id": user.id, "role": user.role.value},
            expires_delta=access_token_expires
        )
        return access_token

    async def forgot_password(self, email: str) -> bool:
        """Mock forgot password flow - just checks if user exists"""
        user = await self.user_repo.get_by_email(email)
        return user is not None

