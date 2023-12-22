import datetime

from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship

from .core import Base


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    uid = Column(Integer, nullable=False)
    state = Column(String(50), default='start')
    access_token = Column(String(250), nullable=True)


class PageToken(Base):
    __tablename__ = 'page_tokens'
    id = Column(Integer, primary_key=True)
    page_number = Column(Integer)
    next_page_token = Column(Text)
    short_token = Column(String(20), unique=True, index=True)
    prev_page_id = Column(Integer, ForeignKey('page_tokens.id'), nullable=True)
    prev_page = relationship('PageToken', remote_side=[id])
