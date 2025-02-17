from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core import config

engine = create_engine(config.get_settings().supabase_postgres_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
