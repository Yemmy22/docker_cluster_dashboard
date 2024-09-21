#!/usr/bin/python3

import logging
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, DateTime, Integer
from datetime import datetime

Base = declarative_base()


class BaseModel(Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at = Column(DateTime, nullable=True)  # Optional soft delete

    def save(self, session):
        try:
            session.add(self)
            session.commit()
        except Exception as e:
            session.rollback()
            logging.error(f"Error saving model: {str(e)}")
            raise e

    def delete(self, session, soft_delete=False):
        try:
            if soft_delete:
                self.deleted_at = datetime.utcnow()
            else:
                session.delete(self)
            session.commit()
        except Exception as e:
            session.rollback()
            logging.error(f"Error deleting model: {str(e)}")
            raise e

