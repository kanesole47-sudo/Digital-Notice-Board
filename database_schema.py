# database_schema.py
# Purpose: All database models and initialization for the Digital Notice Board

import os
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'notice_board.db')
DB_URL = f'sqlite:///{DB_PATH}'

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False)  # 'student' or 'admin'
    stream = Column(String(50), nullable=True)  # BSc CS, BSc IT, Commerce, Arts
    year = Column(String(10), nullable=True)    # FY, SY, TY
    division = Column(String(10), nullable=True)  # Div A, Div B
    seat_number = Column(String(20), nullable=True)
    profile_pic_path = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Notice(Base):
    __tablename__ = 'notices'
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)
    priority = Column(String(10), nullable=False)  # 'red', 'yellow', 'green'
    target_stream = Column(String(50), nullable=False)  # specific stream or 'All'
    target_year = Column(String(10), nullable=False)    # specific year or 'All'
    target_division = Column(String(10), nullable=False)  # specific div or 'All'
    attachment_path = Column(String(500), nullable=True)
    creator_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    creator = relationship('User', backref='notices')

class SavedNotice(Base):
    __tablename__ = 'saved_notices'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    notice_id = Column(Integer, ForeignKey('notices.id'), nullable=False)
    __table_args__ = (UniqueConstraint('user_id', 'notice_id', name='uq_user_notice_save'),)

class ReadReceipt(Base):
    __tablename__ = 'read_receipts'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    notice_id = Column(Integer, ForeignKey('notices.id'), nullable=False)
    read_at = Column(DateTime, default=datetime.utcnow)
    __table_args__ = (UniqueConstraint('user_id', 'notice_id', name='uq_user_notice_read'),)


import streamlit as st

def get_engine():
    """Returns SQLAlchemy engine (creates DB file if not exists)"""
    engine = create_engine(DB_URL, echo=False)
    return engine

get_engine = st.cache_resource(get_engine)

def get_session():
    """Returns a new SQLAlchemy session"""
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    return Session()

def init_db():
    """Creates all tables if they don't exist"""
    engine = get_engine()
    Base.metadata.create_all(engine)
    return engine
