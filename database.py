from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config import NEON_DB_URL

DATABASE_URL = NEON_DB_URL

if not DATABASE_URL:
    raise ValueError("NEON_DB_URL environment variable is not set")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# --- Dependency for FastAPI ---
def get_db():
    """
    A dependency function to get a database session for each request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# A function to create all tables (optional, but useful for setup)
def create_database_tables():
    """
    Creates all the tables in the database based on the models.
    """
    Base.metadata.create_all(bind=engine)