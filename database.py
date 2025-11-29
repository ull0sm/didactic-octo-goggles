"""
Database models for EntryDesk application
"""
from sqlalchemy import create_engine, Column, Integer, String, Date, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.pool import NullPool, QueuePool
from datetime import datetime
import os
import logging
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to read DATABASE_URL from Streamlit secrets if running in Streamlit,
# fall back to environment variable, then to local SQLite as a last resort.
secret_url = None
try:
    import streamlit as st
    secret_url = st.secrets.get("DATABASE_URL", None)
except Exception:
    pass

DB_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "entrydesk.db"))
DATABASE_URL = secret_url or os.getenv("DATABASE_URL", f"sqlite:///{DB_FILE}")

# Log which database we're using (without exposing credentials)
if DATABASE_URL.startswith("postgresql"):
    logger.info("Using PostgreSQL database (cloud/persistent storage)")
elif DATABASE_URL.startswith("sqlite"):
    logger.warning("Using SQLite database (local/temporary storage - not recommended for production)")
elif DATABASE_URL.startswith("mysql"):
    logger.info("Using MySQL database")
elif DATABASE_URL.startswith("oracle"):
    logger.info("Using Oracle database")
else:
    # For unknown database types, just log that we're using a database
    # without exposing the URL or credentials
    logger.info("Using custom database configuration")

# Configure engine based on database type
if DATABASE_URL.startswith("sqlite"):
    # SQLite-specific configuration
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=NullPool  # SQLite doesn't benefit from connection pooling
    )
elif DATABASE_URL.startswith("postgresql"):
    # PostgreSQL-specific configuration with connection pooling
    engine = create_engine(
        DATABASE_URL,
        poolclass=QueuePool,
        pool_size=5,  # Number of connections to maintain
        max_overflow=10,  # Maximum number of connections to create beyond pool_size
        pool_pre_ping=True,  # Verify connections before using them
        pool_recycle=3600,  # Recycle connections after 1 hour
        echo=False  # Set to True for SQL debugging
    )
else:
    # Generic configuration for other databases
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Coach(Base):
    """Coach/User model"""
    __tablename__ = "coaches"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    google_id = Column(String, unique=True, index=True)
    is_admin = Column(Integer, default=0)  # 1 for admin, 0 for regular coach
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    athletes = relationship("Athlete", back_populates="coach")


class Athlete(Base):
    """Athlete/Participant model"""
    __tablename__ = "athletes"
    
    id = Column(Integer, primary_key=True, index=True)
    unique_id = Column(Integer, unique=True, index=True, nullable=False)  # Global unique ID
    name = Column(String, nullable=False)
    dob = Column(Date, nullable=False)
    dojo = Column(String, nullable=False)
    belt = Column(String, nullable=False)
    day = Column(String, nullable=False)  # 'Saturday' or 'Sunday'
    gender = Column(String, nullable=True)  # 'Male' or 'Female' - nullable for backward compatibility
    coach_id = Column(Integer, ForeignKey("coaches.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    coach = relationship("Coach", back_populates="athletes")


def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database and create all tables"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise


def check_db_connection():
    """
    Check if database connection is working.
    Returns True if connection is successful, False otherwise.
    """
    try:
        db = next(get_db())
        # Try a simple query
        db.execute("SELECT 1")
        db.close()
        logger.info("Database connection check: OK")
        return True
    except Exception as e:
        logger.error(f"Database connection check failed: {e}")
        return False


def get_next_unique_id(db):
    """Generate next unique ID for athlete"""
    max_id = db.query(Athlete.unique_id).order_by(Athlete.unique_id.desc()).first()
    if max_id:
        return max_id[0] + 1
    return 1  # Start from 1


def normalize_string(s):
    """Normalize string: lowercase and remove extra spaces"""
    if not s:
        return ""
    return " ".join(str(s).strip().lower().split())


def check_duplicate_athlete(db, name, dob, dojo=None, coach_id=None):
    """
    Check if an athlete with the same name, DOB, and dojo already exists.
    Uses case-insensitive comparison and removes extra spaces.
    If coach_id is provided, only check within that coach's athletes.
    Returns the existing athlete if found, None otherwise.
    """
    # Normalize the input name and dojo
    normalized_name = normalize_string(name)
    normalized_dojo = normalize_string(dojo) if dojo else None
    
    # Get all athletes with matching DOB
    query = db.query(Athlete).filter(Athlete.dob == dob)
    if coach_id:
        query = query.filter(Athlete.coach_id == coach_id)
    
    # Check each athlete with normalized comparison
    for athlete in query.all():
        athlete_normalized_name = normalize_string(athlete.name)
        if athlete_normalized_name == normalized_name:
            # If dojo is provided, also check dojo match
            if normalized_dojo:
                athlete_normalized_dojo = normalize_string(athlete.dojo)
                if athlete_normalized_dojo == normalized_dojo:
                    return athlete
            else:
                # If dojo not provided, just match by name and DOB
                return athlete
    
    return None
