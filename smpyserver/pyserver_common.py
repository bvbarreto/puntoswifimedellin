#!/sm/scripts/python
# -*- coding: utf-8 -*-

"""
pyserver_common.py
Funciones comunes para todos los elementos de pyserver
"""

#******************************************************************************
# Add root or main directory to python path for module execution
#******************************************************************************
if __name__ == '__main__':    
    import os, sys
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..'))) 
#******************************************************************************

import logging
from pydantic import Field
from typing import Optional
from pydantic import BaseModel, Field

from fastapi import  Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from secrets import compare_digest

import config.smpy_config as cfg


#%%
#******************************************************************************
# globals
#******************************************************************************
logger = logging.getLogger(__name__)

USERNAME=cfg.GLOBAL_PYSERVICE_CORE_USER
PASSWORD=cfg.GLOBAL_PYSERVICE_CORE_PWD
SERVER_HOST=cfg.GLOBAL_PYSERVICE_SERVER_HOST
SERVER_PORT=cfg.GLOBAL_PYSERVICE_CORE_PORT

RESULT_OK='OK'
RESULT_ERROR='ERROR'
RESULT_FAIL='FAIL'

security = HTTPBasic()

#%%
#******************************************************************************
# Declaraciones de clases para el API del smpyserver
# Se requiere para el swagger
#******************************************************************************

class NotifyParameter(BaseModel):
    referenceId: str = Field(None, description="referenceId de la tarea")    
    state: str = Field(None, description="Estado: START,OK,ERROR")
    detail: Optional[str] = Field(None, description="Detalle")
    

#%%
#******************************************************************************
# functions
#******************************************************************************
 
def authorization(credentials: HTTPBasicCredentials = Depends(security)):
    current_username_bytes = credentials.username.encode("utf8")
    correct_username_bytes = USERNAME.encode("utf8")
    is_correct_username = compare_digest(
        current_username_bytes, correct_username_bytes
    )
    current_password_bytes = credentials.password.encode("utf8")
    correct_password_bytes = PASSWORD.encode("utf8")
    is_correct_password = compare_digest(
        current_password_bytes, correct_password_bytes
    )
    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )

    return True       
 
def get_response(result, detail=None, data=None):
    logger.info("get_response:"+str(result)+" : "+str(detail))
    return {
            'result' : result,
            'detail' : detail,
            'data' : data
            } 


#%%
#******************************************************************************
# Module Main Code
# This code run only if this script is called directly
# This code helps to developer to test and know the usage of the module
#******************************************************************************
if __name__ == '__main__':   
    import smcommon.logging_util as logutil
    logutil.configure_logger_basic()
    logger.info('Start module execution')
    
    n=NotifyParameter(referenceId="1234", result="OK")
    print(n)
    
    logger.info('End module execution')
