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
import json

dir_path = os.path.dirname(os.path.realpath(__file__))

config_path = os.path.join(dir_path, 'database_config.json')

with open(config_path) as f:
    config = json.load(f)
    username = config['username']
    password = config['password']
    host = config['host']
    database_name = config['database_name']

SQLALCHEMY_DATABASE_URL = f'mysql://{username}:{password}@{host}:3306/{database_name}'

engine = create_engine(
    SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

