"""
Authentication service with business logic.
Handles user registration, login, and token management.
"""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.auth.repository import UserRepository
from app.auth.schemas import UserCreate, UserLogin, TokenResponse
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token
)


class AuthService:
    """Service for authentication operations."""

    def __init__(self, db: Session):
        self.repository = UserRepository(db)
        self.db = db

    def register_user(self, user_data: UserCreate) -> TokenResponse:
        """
        Register a new user.

        Args:
            user_data: User registration data

        Returns:
            Token response with access and refresh tokens

        Raises:
            HTTPException: If email already exists
        """
        # Check if email already exists
        if self.repository.email_exists(user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Hash password
        hashed_password = get_password_hash(user_data.password)

        # Create user
        user = self.repository.create(
            name=user_data.name,
            email=user_data.email,
            hashed_password=hashed_password
        )

        # Generate tokens
        access_token = create_access_token(data={"sub": str(user.id)})
        refresh_token = create_refresh_token(data={"sub": str(user.id)})

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token
        )

    def login_user(self, login_data: UserLogin) -> TokenResponse:
        """
        Authenticate user and generate tokens.

        Args:
            login_data: User login credentials

        Returns:
            Token response with access and refresh tokens

        Raises:
            HTTPException: If credentials are invalid
        """
        # Get user by email
        user = self.repository.get_by_email(login_data.email)

        # Verify user exists and password is correct
        if not user or not verify_password(login_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Generate tokens
        access_token = create_access_token(data={"sub": str(user.id)})
        refresh_token = create_refresh_token(data={"sub": str(user.id)})

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token
        )

    def refresh_access_token(self, refresh_token: str) -> TokenResponse:
        """
        Generate new access token from refresh token.

        Args:
            refresh_token: Valid refresh token

        Returns:
            Token response with new access and refresh tokens

        Raises:
            HTTPException: If refresh token is invalid
        """
        payload = decode_token(refresh_token)

        if payload is None or payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user_id = payload.get("sub")

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Verify user still exists
        user = self.repository.get_by_id(int(user_id))

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Generate new tokens
        access_token = create_access_token(data={"sub": user_id})
        new_refresh_token = create_refresh_token(data={"sub": user_id})

        return TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh_token
        )
