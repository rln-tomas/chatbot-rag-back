"""
Database seeder script to populate test data.
Run this script to create test users and sample data.

Usage:
    python scripts/seed.py
    # or from Docker:
    docker compose exec api python scripts/seed.py
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine, Base
from app.core.security import get_password_hash
from app.auth.models import User
from app.config_management.models import Configuration, ScrapingStatus
from app.chat.models import Conversation, Message


def seed_users(db: Session):
    """Create test users."""
    print("Creating test users...")

    users_data = [
        {
            "name": "Admin User",
            "email": "admin@example.com",
            "password": "admin123"
        },
        {
            "name": "Test User",
            "email": "test@example.com",
            "password": "test123"
        },
        {
            "name": "John Doe",
            "email": "john@example.com",
            "password": "john123"
        },
        {
            "name": "Jane Smith",
            "email": "jane@example.com",
            "password": "jane123"
        }
    ]

    created_users = []
    for user_data in users_data:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == user_data["email"]).first()
        if existing_user:
            print(f"  ⚠️  User {user_data['email']} already exists, skipping...")
            created_users.append(existing_user)
            continue

        # Create new user
        user = User(
            name=user_data["name"],
            email=user_data["email"],
            hashed_password=get_password_hash(user_data["password"])
        )
        db.add(user)
        db.flush()  # Get the user ID
        created_users.append(user)
        print(f"  ✓ Created user: {user_data['email']} (password: {user_data['password']})")

    db.commit()
    return created_users


def seed_configurations(db: Session, users: list[User]):
    """Create sample URL configurations."""
    print("\nCreating sample URL configurations...")

    if len(users) < 2:
        print("  ⚠️  Not enough users to create configurations")
        return []

    configs_data = [
        {
            "user": users[0],
            "url": "https://python.langchain.com/docs/get_started/introduction",
            "status": ScrapingStatus.COMPLETED
        },
        {
            "user": users[0],
            "url": "https://docs.pinecone.io/guides/get-started/overview",
            "status": ScrapingStatus.PENDING
        },
        {
            "user": users[1],
            "url": "https://fastapi.tiangolo.com/",
            "status": ScrapingStatus.COMPLETED
        },
        {
            "user": users[1],
            "url": "https://docs.celeryq.dev/en/stable/getting-started/introduction.html",
            "status": ScrapingStatus.PENDING
        }
    ]

    created_configs = []
    for config_data in configs_data:
        # Check if configuration already exists
        existing_config = db.query(Configuration).filter(
            Configuration.user_id == config_data["user"].id,
            Configuration.url == config_data["url"]
        ).first()

        if existing_config:
            print(f"  ⚠️  Configuration for {config_data['url']} already exists, skipping...")
            created_configs.append(existing_config)
            continue

        # Create new configuration
        config = Configuration(
            user_id=config_data["user"].id,
            url=config_data["url"],
            status=config_data["status"]
        )
        db.add(config)
        db.flush()
        created_configs.append(config)
        print(f"  ✓ Created config: {config_data['url']} (status: {config_data['status'].value})")

    db.commit()
    return created_configs


def seed_conversations(db: Session, users: list[User]):
    """Create sample conversations and messages."""
    print("\nCreating sample conversations...")

    if len(users) < 2:
        print("  ⚠️  Not enough users to create conversations")
        return

    # Conversation 1 for user 1
    conv1 = db.query(Conversation).filter(
        Conversation.user_id == users[0].id,
        Conversation.title == "Introduction to LangChain"
    ).first()

    if not conv1:
        conv1 = Conversation(
            user_id=users[0].id,
            title="Introduction to LangChain"
        )
        db.add(conv1)
        db.flush()

        messages1 = [
            Message(
                conversation_id=conv1.id,
                is_user_message=True,
                content="What is LangChain?"
            ),
            Message(
                conversation_id=conv1.id,
                is_user_message=False,
                content="LangChain is a framework for developing applications powered by language models. It provides tools and abstractions to work with LLMs, chain together multiple components, and build complex AI applications."
            ),
            Message(
                conversation_id=conv1.id,
                is_user_message=True,
                content="How do I get started?"
            ),
            Message(
                conversation_id=conv1.id,
                is_user_message=False,
                content="To get started with LangChain, you should first install it using pip. Then, you can explore the basic components like LLMs, prompts, chains, and agents. The documentation provides excellent tutorials for beginners."
            )
        ]
        db.add_all(messages1)
        print(f"  ✓ Created conversation: 'Introduction to LangChain' with {len(messages1)} messages")
    else:
        print(f"  ⚠️  Conversation 'Introduction to LangChain' already exists, skipping...")

    # Conversation 2 for user 2
    conv2 = db.query(Conversation).filter(
        Conversation.user_id == users[1].id,
        Conversation.title == "FastAPI Basics"
    ).first()

    if not conv2:
        conv2 = Conversation(
            user_id=users[1].id,
            title="FastAPI Basics"
        )
        db.add(conv2)
        db.flush()

        messages2 = [
            Message(
                conversation_id=conv2.id,
                role="user",
                content="What are the advantages of FastAPI?"
            ),
            Message(
                conversation_id=conv2.id,
                role="assistant",
                content="FastAPI offers several advantages: high performance comparable to NodeJS and Go, automatic API documentation with Swagger UI, built-in data validation using Pydantic, type hints support, and async/await capabilities for handling concurrent requests efficiently."
            )
        ]
        db.add_all(messages2)
        print(f"  ✓ Created conversation: 'FastAPI Basics' with {len(messages2)} messages")
    else:
        print(f"  ⚠️  Conversation 'FastAPI Basics' already exists, skipping...")

    db.commit()


def main():
    """Main seeder function."""
    print("=" * 60)
    print("Starting database seeding...")
    print("=" * 60)

    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)

    # Create database session
    db = SessionLocal()

    try:
        # Seed users
        users = seed_users(db)

        # Seed configurations
        seed_configurations(db, users)

        # Seed conversations
        seed_conversations(db, users)

        print("\n" + "=" * 60)
        print("Seeding completed successfully!")
        print("=" * 60)
        print("\nTest users created:")
        print("-" * 60)
        for user in users:
            print(f"  Email: {user.email}")
        print("\nDefault password for test users:")
        print("  admin@example.com -> admin123")
        print("  test@example.com  -> test123")
        print("  john@example.com  -> john123")
        print("  jane@example.com  -> jane123")
        print("-" * 60)

    except Exception as e:
        print(f"\n❌ Error during seeding: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
