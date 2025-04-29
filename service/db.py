#!/sm/scripts/python
# -*- coding: utf-8 -*-

"""
sm_pyserver.py
Servicio REST para gestion servicio de integracion con Fiware

"""

#******************************************************************************
# Add root or main directory to python path for module execution
#******************************************************************************
if __name__ == '__main__':    
    import os, sys
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..'))) 
#******************************************************************************

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
import os

basedir = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URL = 'sqlite:///'+os.path.join(basedir, "data_pyserver.db")
#SQLALCHEMY_DATABASE_URL = "sqlite:////sm/files/data_pyserver.db"


engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False},echo=True
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()