# server/db/characters.py
import re
from sqlalchemy import select
from .database import SessionLocal
from .models import Character


# Only allow letters, numbers, underscores; max 12 characters
NAME_REGEX = re.compile(r"^[A-Za-z0-9_]{1,12}$")

def create_character(user_id: int, name: str):
    # Validate name
    if not NAME_REGEX.match(name):
        raise ValueError(
            "Invalid name: only letters, numbers, underscores, 1-12 characters allowed"
        )

    session = SessionLocal()
    try:
        # Check global uniqueness
        existing = session.execute(
            select(Character).where(Character.name == name)
        ).scalar_one_or_none()

        if existing:
            raise ValueError("Character name already exists")

        char = Character(
            user_id=user_id,
            name=name,
            x=100,
            y=100,
            map_id=100001,
            level=0,
            exp=0,
            hp=50,
            mp=0,
            str=0,
            dex=0,
            agi=0,
            vit=0,
            int=0
        )
        session.add(char)
        session.commit()
        session.refresh(char)
        return char
    finally:
        session.close()
