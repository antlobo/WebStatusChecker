# Standard library imports
import os
import logging

# Third party imports
try:
    from sqlalchemy import create_engine
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import sessionmaker, scoped_session
except ImportError:
    logging.warning("Package sqlalchemy need to be installed")
    raise ImportError("Package sqlalchemy need to be installed")

SQL_CONNECTION = os.getenv('SQL_CONNECTION')

__logger = logging.getLogger(__name__)
__logger.info(f"Initiating Database connection")
__logger.debug(f"Initiating Database connection to {SQL_CONNECTION}")

Base = declarative_base()


def get_engine():
    return create_engine(SQL_CONNECTION)  # , connect_args={"check_same_thread": False})


def get_session():
    engine = get_engine()
    Session = scoped_session(sessionmaker(bind=engine))
    session = Session()
    return session
