"""
original author: Dominik Cedro
created: 2024-08-29
license: BSD 3.0
description: Script to create new user from server side
"""
from sqlalchemy.orm import Session
from .database import SessionLocal
import crud
import schemas


def create_admin_user():
    db: Session = SessionLocal()
    try:
        user = schemas.UserCreate(
            username="admin",
            email="admin@example.com",
            full_name="Admin User",
            password="adminpassword"
        )
        crud.create_user(db, user)
        print("Admin user created successfully.")
    except Exception as e:
        print(f"Error creating admin user: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_admin_user()