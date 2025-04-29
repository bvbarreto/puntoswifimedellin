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

from sqlalchemy.orm import Session

import service.models as models
import service.schemas as schemas


class TaskRepo:
    
 async def create(db: Session, task: schemas.TaskCreate):
        db_task = models.Task(name=task.name)
        db.add(db_task)
        db.commit()
        db.refresh(db_task)
        return db_task
    
 def fetch_by_id(db: Session,_id):
     return db.query(models.Task).filter(models.Task.id == _id).first()
 
 def fetch_by_name(db: Session,name):
     return db.query(models.Task).filter(models.Task.name == name).first()
 
 def fetch_all(db: Session, skip: int = 0, limit: int = 100):
     return db.query(models.Task).offset(skip).limit(limit).all()
 
 async def delete(db: Session,task_id):
     db_task= db.query(models.Task).filter_by(id=task_id).first()
     db.delete(db_task)
     db.commit()
       
 async def update(db: Session,task_data):
    updated_task = db.merge(task_data)
    db.commit()
    return updated_task
    
