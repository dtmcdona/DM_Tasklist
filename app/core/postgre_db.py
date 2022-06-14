from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_utils import database_exists, create_database
from settings import postgresql as settings

import logging

log = logging.getLogger(__name__)


def get_database():
    """Connect to database and returns engine"""
    try:
        engine = get_engine_from_settings()
        log.info("Connected to PostgreSQL database!")
    except IOError:
        log.exception("Failed to get database connection!")
        return None, 'fail'

    return engine


def get_engine(user, password, host, port, db):
    """Creates and returns engine"""
    url = f"postgresql://{user}:{password}@{host}:{port}/{db}"
    if not database_exists(url):
        create_database(url)
    engine = create_engine(url, pool_size=50, echo=False)
    return engine


def get_engine_from_settings():
    """Gets PostgreSQL credentials from settings.py"""
    keys = ['pguser', 'pgpassword', 'pghost', 'pgport', 'pgdb']
    if not all(key in keys for key in settings.keys()):
        raise Exception('Bad config file')

    return get_engine(settings['pguser'],
                      settings['pgpassword'],
                      settings['pghost'],
                      settings['pgport'],
                      settings['pgdb'])


def get_session():
    """Creates and returns session"""
    engine = get_engine_from_settings()
    new_session = sessionmaker(bind=engine)()
    return new_session


db = get_database()
session = get_session()
Base = declarative_base()
