"""
original author: Dominik Cedro
created: 2024-08-29
license: ###
description: src setup with sqlalchemy
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

username = os.getenv('DB_USERNAME')
password = os.getenv('DB_PASSWORD')
host = os.getenv('DB_HOST')
database_name = os.getenv('DB_NAME')

SQLALCHEMY_DATABASE_URL = f'mysql://{username}:{password}@{host}:3306/{database_name}'

engine = create_engine(
    SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()