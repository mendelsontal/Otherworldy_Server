# server/db/characters.py
import re
from sqlalchemy import select
from .database import SessionLocal
from .models import Character


# Only allow letters, numbers, underscores; max 12 characters
NAME_REGEX = re.compile(r"^[A-Za-z0-9_]{1,12}$")

def check_name(name: str) -> tuple[bool, str | None]:
    """
    Validate a character name.
    Returns (ok, reason) where:
      - ok = True if valid and available
      - ok = False with reason string otherwise
    """
    if not NAME_REGEX.match(name):
        return False, "Invalid name: only letters, numbers, underscores, 1-12 characters allowed"

    session = SessionLocal()
    try:
        existing = session.execute(
            select(Character).where(Character.name == name)
        ).one_or_none()

        if existing is not None:
            return False, "Character name already exists"

        return True, None
    finally:
        session.close()

def create_character(user_id: int, name: str, gender: str = "Male", hair: str | None = None):
    ok, reason = check_name(name)
    if not ok:
        raise ValueError(reason)

    session = SessionLocal()
    try:
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
            int=0,
            appearance={
                "gender": gender,
                "hair": hair,
            },          
            gear={
                "helm": None,
                "armor": None,
                "pants": None,
                "accessory": None,
                "weapon": None
            }
                )
        
        session.add(char)
        session.commit()
        session.refresh(char)
        return char
    finally:
        session.close()


def delete_character(user_id: int, char_id: int) -> bool:
    """Delete a character only if it belongs to the given user."""
    session = SessionLocal()
    try:
        char = session.execute(
            select(Character).where(Character.id == char_id, Character.user_id == user_id)
        ).scalar_one_or_none()

        if not char:
            return False  # Not found or doesn’t belong to this user

        session.delete(char)
        session.commit()
        return True
    finally:
        session.close()
