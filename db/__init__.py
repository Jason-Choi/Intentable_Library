
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.scoping import scoped_session

from config import config

engine = create_engine(config.DB_URL, encoding="utf-8")
db_session = sessionmaker(bind=engine)


def get_db():
    db = db_session()
    try:
        yield db
    finally:
        db.close()
