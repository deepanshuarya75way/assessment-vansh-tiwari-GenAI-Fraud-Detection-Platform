from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session, sessionmaker

from app.backend.core.config import get_settings
from app.backend.db.base import Base
# Import enterprise models to register them with Base
from app.backend.db import enterprise_models as _models

settings = get_settings()
database_url = make_url(settings.database_url)
engine_kwargs: dict[str, object] = {
    "future": True,
    "echo": settings.database_echo,
    "pool_pre_ping": settings.database_pool_pre_ping,
}

if database_url.get_backend_name() == "sqlite":
    engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(settings.database_url, **engine_kwargs)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)

Base.metadata.create_all(bind=engine)


def get_db_session() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
