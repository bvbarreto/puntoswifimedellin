#!/sm/scripts/python
# -*- coding: utf-8 -*-
"""
smpy_util.py
Utilidades para manejo de scripts python con Siplex Management
"""

#******************************************************************************
# Add root or main directory to python path for module execution
#******************************************************************************
if __name__ == '__main__':    
    import os, sys
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..'))) 
#******************************************************************************
    
import logging
import requests
import subprocess
import time
import os
import datetime
import base64

from shutil import copy
from shutil import rmtree
from shutil import move
from shutil import copytree


from enum import Enum

import config.smpy_config as cfg
from smcommon.pyserver_api import PyserviceApi


#%%
#******************************************************************************
# globals
#******************************************************************************
logger = logging.getLogger(__name__)

STATE_START="START"
STATE_OK="OK"
STATE_ERROR="ERROR"
STATE_STOP_ALL="STOP_ALL"
STATE_START_ALL="START_ALL"


#%%
#******************************************************************************
# Excepciones
#******************************************************************************

class SmException(Exception):
    """
    Excepcion controlada por la libre SM
    """
    pass

#mensajes error
FILE_NOT_EXIST="Archivo no existe: "
DIR_NOT_EXIST="Carpeta no existe: "

#%%
#******************************************************************************
# functions
#******************************************************************************
def get_base64(value: str):
    """
    Retorna el string en base64
    """
    encoded_value = base64.b64encode(value.encode("utf-8"))

    return str(encoded_value.decode('utf-8'))

def encode_decode_utf8(value: str):
    """
    Retorna el string original con caracteres especiales correctamente decodificados
    """
    encoded_value = value.encode("utf-8")

    return str(encoded_value.decode('utf-8'))

def execute_shell(command):
    logger.debug("execute_shell: "+str(command))
    r=subprocess.call(command, shell=True)
    if r > 0:
        raise SmException("Error executing: "+command+" :" + str(r))  
    
def execute_shell_background(cmdList):
    from pathlib import Path
    from os import chdir
    print(cmdList)
    cwd = Path(__file__).parent.parent.resolve()
    chdir(cwd)

    if cmdList == None:
        logger.warning("execute_shell_background none")
        return None
    logger.debug("execute_shell_background: " + " ".join(cmdList))
    try:
        subprocess.Popen(cmdList)
        return None
    except Exception as exc:
        logger.exception("Exception executing command:" + str(cmdList))
        return str(exc)    
        
                
def make_dir(dirpath):
    logger.debug("make_dir: "+str(dirpath))    
    if not os.path.exists(dirpath):
        if os.name == 'posix':
            execute_shell('/bin/mkdir '+ dirpath)
        else:
            os.mkdir(dirpath)
        
def remove_dir(dirpath):
    logger.debug("remove_dir: "+str(dirpath))
    if not os.path.exists(dirpath):
        if os.name == 'posix':
            execute_shell('/bin/rm -rf '+ dirpath)
        else:
            os.rmdir(dirpath)        
       
        
def remove_file(file):
    logger.debug("remove_file: "+str(file))    
    if os.path.exists(file):
        if os.name == 'posix':
            execute_shell('/bin/rm  -f "'+ file+'"')
        else:
            os.remove(file)
    else:
        raise SmException(FILE_NOT_EXIST+file)
        
def remove_files(dirpath):
    logger.debug("remove_files: "+str(dirpath))    
    if os.path.exists(dirpath):
        if os.name == 'posix':
            execute_shell('/bin/rm  -f '+ dirpath+'/*')
        else:
            rmtree(dirpath)
    else:
        raise SmException(DIR_NOT_EXIST+dirpath)        
 
def copy_files(source, target):
    logger.debug("copy_files: "+str(source)+"->"+str(target))    
    if os.path.exists(source) and os.path.exists(os.path.dirname(target)):
        if os.name == 'posix':
            execute_shell('/bin/cp  -f '+ source+'/* '+target+'/')
        else:
            copytree(source, target)
    else:
        raise SmException("Some dir not exist: "+source+" or "+target)
        
def copy_file(file, target):
    logger.debug("copy_file: "+str(file)+"->"+str(target))
    if os.path.exists(file) and os.path.exists(os.path.dirname(target)):
        if os.name == 'posix':
            execute_shell('/bin/cp  -f "'+ file+'" '+target+'/')
        else:
            copy(file, target)
    else:
        raise SmException(FILE_NOT_EXIST+file+" or "+target)
        
def move_file(file, target):
    logger.debug("move_file: "+str(file)+"->"+str(target))   
    if os.path.exists(file) and os.path.exists(target):
        if os.name == 'posix':
            execute_shell('/bin/mv "'+ file+'" "'+target+'/"')
        else:
            move(file, target)
    else:
        raise SmException(FILE_NOT_EXIST+file+" or "+target)
        
def move_rename_file(file, newfile):
    logger.debug("move_rename_file: "+str(file)+"->"+str(newfile))
    if os.path.exists(file):
        if os.name == 'posix':
            execute_shell('/bin/mv "'+ file+'" "'+newfile+'"')
        else:
            move(file, newfile)
    else:
        raise SmException(FILE_NOT_EXIST+file)
               

def list_files(dirpath):
    logger.debug("list_files:"+str(dirpath))
    if os.path.exists(dirpath):
       return os.listdir(dirpath)
    else:
        raise SmException(DIR_NOT_EXIST+dirpath)

def datetime2array(dt):
    '''
    Convierte datetime to array, para permitir serializacion a json de tipo datetime
    Ejemplo: executionTime = sm.datetime2array(datetime.datetime.now())
    '''
    if dt == None: return None    
    return [dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second ,dt.microsecond]  

def date2array(d):
    '''
    Convierte date to array, para permitir serializacion a json de tipo date
    Ejemplo: executionTime = sm.date2array(datetime.date.today())
    '''
    if d == None: return None
    return [d.year, d.month, d.day]

def time2array(t):
    '''
    Convierte time to array, para permitir serializacion a json de tipo datetime
    Ejemplo: executionTime = sm.time2array(datetime.datetime.now().time())
    '''
    if t == None: return None    
    return [t.hour, t.minute, t.second ,t.microsecond]  

def restvalue_to_datetime(datetime_str):
    """ 
    ===========================================================================
    Convierte valor retornado en metodo REST a tipo datetime
    Ejemplo: 2021-06-30T03:57:54.911
    ===========================================================================     
    """ 
    if datetime_str == None: return None
    if '.' in datetime_str: dateformat = '%Y-%m-%dT%H:%M:%S.%f'
    else: dateformat = '%Y-%m-%dT%H:%M:%S'
    return datetime.datetime.strptime(datetime_str, dateformat)
    
    
def restvalue_to_date(date_str):
    """ 
    ===========================================================================
    Convierte valor retornado en metodo REST a tipo datetime
    Ejemplo: 2021-06-30
    ===========================================================================     
    """
    if date_str == None: return None
    return datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
    
        
def get_exception_detail(exc_info):
    if exc_info == None:
        return "Error desconocido"
    error_code=""
    if len(exc_info) > 1: error_code = str(exc_info[0])
    error_detail=""
    if len(exc_info) > 2: error_detail = str(exc_info[1])
    return error_code + ": " + error_detail

#%%
#******************************************************************************
# funciones para script integracion
#******************************************************************************

def base_init():
    #Deshabilia mensajes de log detallados del request
    requests.packages.urllib3.disable_warnings()
    make_dir("./sm/log")
    make_dir("./sm/files")
    
    
def base_add_args(parser, version):
    parser.add_argument("-t", "--test-mode", 
                        dest="test_mode",
                        help="Test mode execution",
                        required=False,
                        default=True,
                        action="store_true"
                        ) 
    parser.add_argument("-rid", "--ref-id", 
                        dest="reference_id",
                        help="Reference Key",
                        required=False, 
                        default=None
                        )
#%%
#******************************************************************************
# classes
#******************************************************************************




  
class SmTaskUtil:
    def __init__(self, reference_id, task_name=None, test_mode=False, args=None):
        self.reference_id = str(reference_id)
        self.task_name=task_name
        self.test_mode = test_mode
        
        self.init_datekey()
        self.init_datetimekey()
        if self.test_mode: return
        self.pyservice_api=PyserviceApi(ip=cfg.GLOBAL_PYSERVICE_CORE_IP, port=cfg.GLOBAL_PYSERVICE_CORE_PORT, username=cfg.GLOBAL_PYSERVICE_CORE_USER, password=cfg.GLOBAL_PYSERVICE_CORE_PWD)
        self.pyservice_api.create(task_name)

    def init_datetimekey(self):
        self.DATETIMEKEY=str(time.strftime("%Y%m%d%H%M%S"))
        logger.debug("init_datetimekey:"+self.DATETIMEKEY)
        
    def init_datekey(self):
        self.DATEKEY=str(time.strftime("%Y%m%d"))
        logger.debug("init_datekey:"+self.DATEKEY)
      
    def notify_executing_task(self):
        logger.info('notify_executing_task')
        if self.test_mode: return
        self.pyservice_api.notify(task_code=self.task_name, reference_id=self.reference_id, state=STATE_START)

    def notify_finish_task(self, code, detail=None):
        logger.info(f'notify_finish_task {code}:{detail}')
        if self.test_mode: return
        self.pyservice_api.notify(task_code=self.task_name, reference_id=self.reference_id, state=code, detail=detail)
    


#%%
#******************************************************************************
# Module Main Code
# This code run only if this script is called directly
# This code helps to developer to test and know the usage of the module
#******************************************************************************
if __name__ == '__main__':   
    import smcommon.logging_util as logutil
    logutil.configure_logger_basic()
    #logutil.configure_logger('/tmp/log.log', logging.DEBUG)
    logger.info('Start module execution')
    
    tstUtil = SmTaskUtil(1)
    
    s = "/tmp/s"
    t = "/tmp/t"
    
    make_dir(s)
    make_dir(t)
    remove_files(s)
    remove_files(t)
    
    if cfg.OSTYPE == cfg.OsType.LINUX:
        execute_shell("echo hola  > "+s+"/source1.txt")
        execute_shell("echo hola2 > "+s+"/source2.txt")
        copy_files(s, t)
        remove_files(s)
        logger.debug(list_files(t))    

    
    logger.info('End module execution')
