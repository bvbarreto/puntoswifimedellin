#!/sm/scripts/python
# -*- coding: utf-8 -*-

'''
Created 2023/09/01
'''

#******************************************************************************
# Add root or main directory to python path for module execution
#******************************************************************************
if __name__ == '__main__':    
    import os, sys
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..'))) 
#******************************************************************************

from pyngsi.sources.source import Source, Row

import pandas as pd
import logging
import datetime

import config.smpy_config as cfg
import smcommon.smpy_util as sm


#%%
#******************************************************************************
# globals
#******************************************************************************
logger = logging.getLogger(__name__)

__version__ = '0.0.1'

#%%
#******************************************************************************
# functions
#******************************************************************************
class OrionSource(Source):
    def __init__(self, df_data: pd.DataFrame, provider: str = "api"):
        logger.info('OrionSource: constructor')
        self.provider = provider

        if df_data is None or df_data.empty:
            logger.warning('OrionSource: No hay datos en el DataFrame')

        self.record = df_data

    def __iter__(self):
        if self.record is not None:
            for index, response in self.record.iterrows():
                yield Row(self.provider, response)


def main(smTaskUtil):
    ''' 
    ===========================================================================
    Main function
    ===========================================================================     
    '''
    logger.info('main PARAMETROS:' + str(smTaskUtil))


    smTaskUtil.notify_executing_task()
    #data_dic = {}

    data_dic = {
        "id": "urn:ngsi-ld:Vehicle:010",
        "type": "Vehicle",
        "category": "servicios municipales",
        "idEquipment": 36000,
        "refVehicleModel": None,
        "typeDevice": "Vehicle",
        "vehiclePlateIdentifier": "002",
        "vehicleStatus": "1",
        "vehicleType": "lorry",
        "dateModified": "2023-06-27T19:30:38.297Z"
    }
    df_data = pd.DataFrame(data_dic, index=[0])

    src = OrionSource(df_data)

    smTaskUtil.notify_finish_task(sm.FinishType.OK)

    

#%%
#******************************************************************************
# Module Main Code
# Run if script call directoy
#******************************************************************************
if __name__ == '__main__':
    ''' 
    ===========================================================================
    configure logger, utilities and call main function
    ===========================================================================     
    '''
    import smcommon.logging_util as logutil
    logutil.configure_logger(cfg.LOG_BASEPATH+os.path.basename(__file__)+'.log', logging.DEBUG)
    logger.info('Start module execution')
    
    sm.base_init()
    programName = os.path.basename(__file__)
    dt_now_format = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')

    smTaskUtil = sm.SmTaskUtil(programName+'-'+dt_now_format, taskType='TASK', testMode=True)

    try:
        main(smTaskUtil)

    except:
        errorDetail = sm.get_exception_detail(sys.exc_info())
        logger.exception('Exception in main:'+errorDetail)
        smTaskUtil.notify_finish_task(sm.FinishType.ERROR, errorDetail)
    
    logger.info('End module execution')