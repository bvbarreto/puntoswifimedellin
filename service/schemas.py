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

from typing import Optional
from pydantic import BaseModel
import datetime

class TaskBase(BaseModel):
    name: str
    enable: bool
    count : int
    countOK : int
    countError : int
    lastOK : Optional[datetime.datetime] = None
    lastError : Optional[datetime.datetime] = None
    log: Optional[str] = None

class TaskCreate(BaseModel):
    name: str

class Task(TaskBase):
    id: int

    class Config:
        orm_mode = True

