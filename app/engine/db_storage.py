import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from models.base_model import Base

class DBStorage:
    __engine = None
    __session = None

    def __init__(self):
        user = os.getenv('DB_USER', 'root')
        password = os.getenv('DB_PASSWORD', '')
        host = os.getenv('DB_HOST', 'localhost')
        db = os.getenv('DB_NAME', 'cluster_db')

        self.__engine = create_engine(f'mysql+mysqldb://{user}:{password}@{host}/{db}')
        self.__session = scoped_session(sessionmaker(bind=self.__engine))

    def reload(self):
        Base.metadata.create_all(self.__engine)

    @property
    def session(self):
        return self.__session()

    def close(self):
        self.__session.remove()

# Initialize the DBStorage
storage = DBStorage()
