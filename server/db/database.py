from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker, declarative_base
from server.config.database import DATABASE_URL
from passlib.context import CryptContext

# Engine and session
engine = create_engine(DATABASE_URL, echo=True, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class
Base = declarative_base()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Initialize DB tables
def init_db():
    # Import models here to avoid circular import
    from . import models
    Base.metadata.create_all(bind=engine)

class Database:
    @staticmethod
    def create_user(username: str, password: str):
        from .models import User
        session = SessionLocal()
        try:
            password_hash = pwd_context.hash(password)
            user = User(username=username, password_hash=password_hash)
            session.add(user)
            session.commit()
            return user
        finally:
            session.close()

    @staticmethod
    def verify_user(username: str, password: str) -> bool:
        from .models import User
        session = SessionLocal()
        try:
            stmt = select(User).where(User.username == username)
            user = session.execute(stmt).scalar_one_or_none()
            if not user:
                return False
            return pwd_context.verify(password, user.password_hash)
        finally:
            session.close()
    
    # <<< Add this method
    @staticmethod
    def get_user(username: str):
        from .models import User
        session = SessionLocal()
        try:
            stmt = select(User).where(User.username == username)
            return session.execute(stmt).scalar_one_or_none()
        finally:
            session.close()
