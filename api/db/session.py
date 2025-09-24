from typing import Generator, Optional
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from api.config import settings

ENGINE = None
SessionLocal: Optional[sessionmaker] = None

if settings.DATABASE_URL:
    ENGINE = create_engine(settings.DATABASE_URL, future=True)
    SessionLocal = sessionmaker(bind=ENGINE, autoflush=False, autocommit=False, future=True)

def get_engine():
    return ENGINE

def get_db() -> Generator[Session, None, None]:
    """
    Dependencia para FastAPI: yield a SQLAlchemy Session
    """
    if SessionLocal is None:
        raise RuntimeError("DATABASE_URL no configurada")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
