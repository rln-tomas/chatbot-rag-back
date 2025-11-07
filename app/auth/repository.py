"""
User repository for database operations.
Implements data access layer for User model.
"""

from typing import Optional
from sqlalchemy.orm import Session
from app.auth.models import User


class UserRepository:
    """Repository for User database operations."""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: int) -> Optional[User]:
        """
        Get user by ID.

        Args:
            user_id: User ID

        Returns:
            User instance or None if not found
        """
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email.

        Args:
            email: User email

        Returns:
            User instance or None if not found
        """
        return self.db.query(User).filter(User.email == email).first()

    def create(self, name: str, email: str, hashed_password: str) -> User:
        """
        Create a new user.

        Args:
            name: User name
            email: User email
            hashed_password: Hashed password

        Returns:
            Created User instance
        """
        user = User(
            name=name,
            email=email,
            hashed_password=hashed_password
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def email_exists(self, email: str) -> bool:
        """
        Check if email already exists.

        Args:
            email: Email to check

        Returns:
            True if email exists, False otherwise
        """
        return self.db.query(User).filter(User.email == email).first() is not None

    def get_all(self, skip: int = 0, limit: int = 100):
        """
        Get all users with pagination.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of User instances
        """
        return self.db.query(User).offset(skip).limit(limit).all()
