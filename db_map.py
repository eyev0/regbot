from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class Users(Base):
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    file_id = Column(String(255))
    filename = Column(String(255))
