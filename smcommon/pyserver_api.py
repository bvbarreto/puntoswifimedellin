#!/sm/scripts/python
# -*- coding: utf-8 -*-
"""
pyserver.api.py

"""

#******************************************************************************
# Add root or main directory to python path for module execution
#******************************************************************************
if __name__ == '__main__':    
    import os, sys
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..'))) 
#******************************************************************************
    
import logging
import time
import requests
from requests.auth import HTTPBasicAuth


#%%
#******************************************************************************
# globals
#******************************************************************************
logger = logging.getLogger(__name__)


#%%
#******************************************************************************
# functions
#****************************************************************************** 

class PyserviceApi:
    def __init__(self, ip='127.0.0.1', port=4999, username=None, password=None): 
         self.ip=ip
         self.port=port
         self.username=username
         self.password=password              

    def notify(self, task_code, reference_id, state, detail=None):
        logger.debug(f"notify:{task_code}:{state}")
        
        headers = {'Content-type': 'application/json;charset=utf-8', 'Accept-Encoding': 'gzip,deflate'}
        jsonData={
                "state" : state,
                "detail" : detail,
                "referenceId" : reference_id,           
                }
        url=f"http://{self.ip}:{self.port}/notify/{task_code}"
        try:
            #Se envia request POST. verify=False: deshabilita verificacion de certificado SSL
            requestResponse = requests.post(url, auth=HTTPBasicAuth(self.username, self.password), headers=headers, json=jsonData,verify=False)
            if requestResponse.status_code != 200: #Si diferente de OK
                logger.error(f"request:{url}:{requestResponse.status_code}:{requestResponse.reason}")
                return False
            else:
                return True
        except Exception as exc:
            logger.exception(f"Exception in monitor:{exc}")
            return False
        
    def create(self, name):
        logger.debug(f"create:{name}")
        time.sleep(1)
        headers = {'Content-type': 'application/json;charset=utf-8', 'Accept-Encoding': 'gzip,deflate'}
        jsonData={
                "name" : name           
                }
        url=f"http://{self.ip}:{self.port}/create"
        try:
            #Se envia request POST. verify=False: deshabilita verificacion de certificado SSL
            requestResponse = requests.post(url, auth=HTTPBasicAuth(self.username, self.password), headers=headers, json=jsonData,verify=False)
            if requestResponse.status_code != 200: #Si diferente de OK
                logger.error(f"request:{url}:{requestResponse.status_code}:{requestResponse.reason}")
                return False
            else:
                return True
        except Exception as exc:
            logger.exception(f"Exception in monitor:{exc}")
            return False         

     
        




#%%
#******************************************************************************
# test functions
#******************************************************************************
if __name__ == '__main__':
    import smcommon.logging_util as logutil
    logutil.configure_logger_basic()
    logger.info('Start module execution')
        
    import config.smpy_config as cfg

    task_code="T2" 
    reference_id="123" 
    state="START" 
    detail=None
    api=PyserviceApi(ip=cfg.GLOBAL_PYSERVICE_CORE_IP, port=cfg.GLOBAL_PYSERVICE_CORE_PORT, username=cfg.GLOBAL_PYSERVICE_CORE_USER, password=cfg.GLOBAL_PYSERVICE_CORE_PWD)
    data=api.create(task_code)
    logger.info("response="+str(data))
    data=api.notify(task_code, reference_id, state, detail)
    logger.info("response="+str(data))
    logger.info('End module execution')