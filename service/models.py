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

from sqlalchemy import Column, Integer, String, DateTime, TEXT, Boolean
from service.db import Base
    
class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True,index=True)
    name = Column(String(80), nullable=False, unique=True,index=True)
    enable = Column(Boolean, nullable=False, default=True)
    count = Column(Integer, nullable=False, default=0)
    countOK = Column(Integer, nullable=False, default=0)
    countError = Column(Integer, nullable=False, default=0)
    lastOK = Column(DateTime)
    lastError = Column(DateTime)
    log = Column(TEXT)
    def __repr__(self):
        return f"Task(name={self.name}, count={self.count}, countOK={self.countOK}, countError={self.countError})"
    
