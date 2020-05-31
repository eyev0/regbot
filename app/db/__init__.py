import sqlalchemy.orm
from sqlalchemy.orm import scoped_session, sessionmaker

from app import config
from app.db.models import Base

# postres_connect_str = 'postgres://docker:docker@localhost:32323/docker'
# engine = sqlalchemy.create_engine(f'sqlite:///{config.db_path}')
engine = sqlalchemy.create_engine(config.db.connect_str)

Base.metadata.create_all(engine)

session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)

from .util import *
