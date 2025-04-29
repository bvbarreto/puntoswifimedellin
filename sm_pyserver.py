#!python
# -*- coding: utf-8 -*-

"""
sm_pyserver.py
Servicio REST para gestion servicio de integracion con Fiware

"""

# ******************************************************************************
# Add root or main directory to python path for module execution
# ******************************************************************************
if __name__ == '__main__':
    import os
    import sys
    sys.path.append(os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..')))
# ******************************************************************************

import logging
import os
import argparse
import time
import datetime

import smcommon.smpy_util as sm
import config.smpy_config as cfg
from smpyserver.pyserver_common import NotifyParameter, get_response
from smpyserver.pyserver_common import authorization
from smpyserver.pyserver_common import RESULT_OK, RESULT_ERROR, RESULT_FAIL
from smpyserver.pyserver_common import SERVER_HOST, SERVER_PORT

from fastapi import FastAPI, Depends, HTTPException, status, Form, Request
from starlette.responses import FileResponse, JSONResponse, RedirectResponse
from uvicorn import run
import inspect
from typing import Union

from service import models
from service.db import get_db, engine
import service.models as models
import service.schemas as schemas
from service.repositories import TaskRepo
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager

# Tareas programadas
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

#from os import path
#log_file_path = path.join(path.dirname(path.abspath(__file__)), 'log.config')
#logging.config.fileConfig(log_file_path)

# %%
# ******************************************************************************
# globals
# ******************************************************************************
logger = logging.getLogger(__name__)

# Inicializa motor tareas programadas
scheduler = BackgroundScheduler()
def task1(db):
    DATETIMEKEY = str(time.strftime("%Y%m%d%H%M%S"))
    logger.info(f"task1:{DATETIMEKEY}")

    args = []
    args.append(cfg.PYTHONCMD)
    args.append(cfg.TASK1_DEVICES_PATH)
    args.append('--ref-id='+DATETIMEKEY)
    sm.execute_shell_background(args)

#scheduler.add_job(task1, cfg.TASK1_DEVICES_PERIOD_TYPE, hour = cfg.TASK1_DEVICES_PERIOD_HOUR,
#                      args=[get_db()], next_run_time=datetime.datetime.now()+datetime.timedelta(seconds=cfg.TASK1_DEVICES_NEXT_RUN_TIME_SECONDS))

# Inicializa FastAPI
app = FastAPI(title=cfg.SERVICE_NAME, version=cfg.SMPY_VERSION)

# Inicializa SQLITE DB
models.Base.metadata.create_all(bind=engine)


# %%
# ******************************************************************************
# URL handlers
# ******************************************************************************

@app.get('/smhealth')
def smhealth(option: str = "d"):
    if option == "d":
        return {"enable": True}
    if option == "detail":
        return {"enable": True, "name": cfg.SERVICE_NAME, "version": cfg.SMPY_VERSION}
    return ""

# %%
# ******************************************************************************
#
# ******************************************************************************


@app.get('/get/{type}')
def get(type: str,
        option: Union[str, None] = None,
        authorized: bool = Depends(authorization),
        db: Session = Depends(get_db)
        ) -> JSONResponse:
    logger.info("get:"+str(type))

    if type == 'tasks':
        try:
            data = TaskRepo.fetch_all(db)
            return data
        except:
            error_detail = sm.get_exception_detail(sys.exc_info())
            logger.exception('Exception in get:'+error_detail)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=RESULT_ERROR + ": " + "type invalid"
            )

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=RESULT_ERROR + ": " + "type invalid"
    )


@app.post('/create')
async def create(
    task: schemas.TaskCreate,
    authorized: bool = Depends(authorization),
    db: Session = Depends(get_db)
) -> JSONResponse:
    logger.info(f"create:{task}")

    current = TaskRepo.fetch_by_name(db, task.name)
    if current != None:
        return current
    else:
        return await TaskRepo.create(db, task=task)


@app.post('/notify/{task_code}')
async def notify(
    task_code: str,
    param: NotifyParameter,
    authorized: bool = Depends(authorization),
    db: Session = Depends(get_db)
) -> JSONResponse:
    logger.info(f"notify:{task_code}:{param}")

    referenceId = param.referenceId
    state = param.state
    detail = param.detail
    logger.debug("referenceId="+str(referenceId)+", state=" +
                 str(state)+", detail="+str(detail))
    if state not in (sm.STATE_START, sm.STATE_OK, sm.STATE_ERROR, sm.STATE_STOP_ALL, sm.STATE_START_ALL):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=RESULT_ERROR + ": state invalid"
        )

    if task_code == "all":
        tasks = TaskRepo.fetch_all(db)
        global scheduler
        if state == sm.STATE_STOP_ALL:
            task_enable = False
            scheduler.shutdown()
        elif state == sm.STATE_START_ALL:
            task_enable = True
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=RESULT_ERROR + ": state invalid")
        for task in tasks:
            task.enable = task_enable
            await TaskRepo.update(db, task)
        return get_response(RESULT_OK)

    current: schemas.Task = TaskRepo.fetch_by_name(db, task_code)
    if current == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=RESULT_ERROR + ": " + "Valor action invalido"
        )

    if state == sm.STATE_START:
        current.count += 1
    if state == sm.STATE_OK:
        current.countOK += 1
        current.lastOK = datetime.datetime.now()
    if state == sm.STATE_ERROR:
        current.countError += 1
        current.lastError = datetime.datetime.now()
        current.log = detail

    await TaskRepo.update(db, current)
    return get_response(RESULT_OK)


# %%
# ******************************************************************************
#
# ******************************************************************************
@app.post('/downloadLog')
async def downloadLog(request: Request,
                      filename: str = Form(..., description="log filename"),
                      authorized: bool = Depends(authorization)) -> FileResponse:

    sig, downloadLog_locals = inspect.signature(downloadLog), locals()
    parameters = {
        param.name: downloadLog_locals[param.name]
        for param in sig.parameters.values() if param.name not in ['authorized', 'request']
    }
    # Ceremonia para traer Argumentos no declarados en la firma del metodo
    form = await request.form()
    parameters.update(dict(form))
    logger.info("downloadLog: " + str(parameters))

    if filename == None or len(filename) == 0:
        logger.warning("filename invalid")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=RESULT_ERROR + ": filename missing or invalid"
        )

    pathlog = f"{cfg.LOG_BASEPATH}{filename}.log"

    if not os.path.exists(pathlog):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=RESULT_ERROR + f": {filename}.log not found"
        )

    return FileResponse(path=pathlog, media_type="text/plain")

# %%
# ******************************************************************************
# Funciones complementarias sm_pyserver
# ******************************************************************************


def process_arguments():
    """ 
    ===========================================================================
    Parse command Line arguments 
    =========================================================================== 
    If args are invalid program must exit    
    """

    programName = os.path.basename(__file__)

    parser = argparse.ArgumentParser(prog=programName)
    sm.base_add_args(parser, cfg.SMPY_VERSION)
    parser.add_argument("-p", "--port",
                        dest="port",
                        help="TCP service port",
                        required=False,
                        type=int,
                        default=SERVER_PORT
                        )

    args = parser.parse_args()
    print("args:"+str(args))
    return args
# %%
# ******************************************************************************
# Tarea automatica para ejecutarse perioticamente
# ******************************************************************************




def task2(db):
    DATETIMEKEY = str(time.strftime("%Y%m%d%H%M%S"))
    logger.info(f"task1:{DATETIMEKEY}")

    args = []
    args.append(cfg.PYTHONCMD)
    args.append(cfg.TASK2_ADVERTISING_PATH)
    args.append('--ref-id='+DATETIMEKEY)
    sm.execute_shell_background(args)

def task3(db):
    DATETIMEKEY = str(time.strftime("%Y%m%d%H%M%S"))
    logger.info(f"task1:{DATETIMEKEY}")

    args = []
    args.append(cfg.PYTHONCMD)
    args.append(cfg.TASK3_SURVEYS_PATH)
    args.append('--ref-id='+DATETIMEKEY)
    sm.execute_shell_background(args)


# %%
# ******************************************************************************
# Module Main Code
# This code run only if this script is called directly
# This code helps to developer to test and know the usage of the module
# ******************************************************************************
if __name__ == '__main__':
    args = process_arguments()
    sm.base_init()
    import smcommon.logging_util as logutil
    print("log: ", cfg.LOG_BASEPATH)
    logutil.configure_logger(
        cfg.LOG_BASEPATH+os.path.basename(__file__)+"."+str(args.port)+'.log', cfg.LOG_LEVEL)
    logger.info('Start module execution in port: '+str(args.port))
    logger.info("args:"+str(args))

    # Agrega la tarea al planificador y establece el intervalo de tiempo
    scheduler.add_job(task1, 'interval', minutes=90,
                      args=[get_db()])
    
    # Agrega la tarea al planificador y establece el intervalo de tiempo
    ###scheduler.add_job(task2, cfg.TASK2_ADVERTISINGS_PERIOD_TYPE, hour = cfg.TASK2_ADVERTISING_PERIOD_HOUR,
    ###                  args=[get_db()], next_run_time=datetime.datetime.now()+datetime.timedelta(seconds=cfg.TASK2_ADVERTISINGS_NEXT_RUN_TIME_SECONDS)  )
    
    # Agrega la tarea al planificador y establece el intervalo de tiempo
    ###scheduler.add_job(task3, cfg.TASK3_SURVEYS_PERIOD_TYPE, hour = cfg.TASK3_SURVEYS_PERIOD_HOUR,
    ###                  args=[get_db()], next_run_time=datetime.datetime.now()+datetime.timedelta(seconds=cfg.TASK3_SURVEYS_NEXT_RUN_TIME_SECONDS))
    
    scheduler.start()
    
    # Inicia FastAPI
    logger.info("SERVER_HOST: {} / SERVER_PORT: {}".format(SERVER_HOST, str(SERVER_PORT)))
    if cfg.OSTYPE == cfg.OsType.WINDOWS:
        logger.info("Inicia en modo pruebas...")
        run("__main__:app", host=SERVER_HOST,port=SERVER_PORT, log_config="log.ini")
    else:
        logger.info("Inicia en modo server...")
        #run("__main__:app", host=SERVER_HOST, port=SERVER_PORT,workers=2, log_config="/sm/core/py/smpyserver/log.ini")
        run("__main__:app", host=SERVER_HOST, port=SERVER_PORT,workers=2, log_config="log.ini")

    logger.info('End module execution')
