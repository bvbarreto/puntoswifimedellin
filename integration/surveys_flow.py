#!python
# -*- coding: utf-8 -*-

'''
Created 2023/10/01
'''

#******************************************************************************
# Add root or main directory to python path for module execution
#******************************************************************************
if __name__ == '__main__':    
    import os, sys
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..'))) 
#******************************************************************************
from pyngsi.agent import NgsiAgent
import pandas as pd

import logging
import argparse

import config.smpy_config as cfg
import smcommon.smpy_util as sm
import integration.surveys_data_model as dm
from integration.surveys_data_source import DataSource
from orion_conn.orion_source import OrionSource
from orion_conn.orion_sink import OrionSink

#%%
#******************************************************************************
# globals
#******************************************************************************
logger = logging.getLogger(__name__)

#%%
#******************************************************************************
# functions
#******************************************************************************

def process_arguments():
    """ 
    ===========================================================================
    Parse command Line arguments 
    =========================================================================== 
    If args are invalid program must exit    
    """
    programName=os.path.basename(__file__)            
    parser = argparse.ArgumentParser(prog=programName)  
    sm.base_add_args(parser, cfg.SMPY_VERSION)     
    args = parser.parse_args()  
    logger.info("args:"+str(args))
    return args

def get_data_from_source():
    # Se consultan los datos de la fuente
    try:
        source_api = DataSource(           
            token=cfg.SRC_TOKEN,
            url_personal_information=cfg.SRC_URL_GET_PERSONAL_INFORMATION ,
            url_customer_response=cfg.SRC_URL_GET_CUSTOMER_RESPONSES          
        )

        return source_api.get_df_merge_data()
    except Exception as e:
        logger.exception('Fallo: consulta de los datos de origen - excepción: %s', e)
        raise Exception('Fallo: consulta de los datos de origen')


def get_source_to_agent(df_data_from_source: pd.DataFrame):
    # Se crea el Source para peticion a Orion
    try:
        return OrionSource(
            df_data=df_data_from_source,
            provider=cfg.SRC_SOURCE_PROVIDER)
    except Exception as e:
        logger.exception('Fallo: construccion del SOURCE para Orion - excepción: %s', e)
        raise Exception('Fallo: construccion del SOURCE para Orion')

def get_sink_to_agent():
    # Se crea el SINK para peticion a Orion
    try:
        sink_orion_constructor = OrionSink(
            host_name=cfg.ORION_URL,
            port=cfg.ORION_PORT,

            orion_token_user_name=cfg.ORION_TOKEN_USER_NAME,
            orion_token_password=cfg.ORION_TOKEN_PASSWORD,
            orion_token_url=cfg.ORION_TOKEN_URL,

            service=cfg.SINK_SERVICE,
            service_path=cfg.SINK_SERVICE_PATH,
            secure=cfg.SINK_SECURE,
            base_url=cfg.SINK_BASE_URL,
            enable_auth_token=cfg.SINK_ENABLE_AUTH_TOKEN
        )
        return sink_orion_constructor.getSinkOrion()
    except Exception as e:
        logger.exception('Fallo: construccion del SINK para Orion - excepción: %s', e)
        raise Exception('Fallo: construccion del SINK para Orion')

def main(smTaskUtil):
    ''' 
    ===========================================================================
    Main function
    ===========================================================================     
    '''
    logger.info('main PARAMETROS:' + str(smTaskUtil))

    smTaskUtil.notify_executing_task()

    logger.info('- Paso 1: Consulta de datos desde la fuente')
    df_data_from_source = get_data_from_source()

    logger.info('- Paso 2: Construccion del objeto SOURCE par el agente de ORION')
    src = get_source_to_agent(df_data_from_source)

    logger.info('- Paso 3: Construccion del objeto SINK par el agente de ORION')
    sink = get_sink_to_agent()

    logger.info('- Paso 4: Construccion del objeto  NgsiAgent')
    agent = NgsiAgent.create_agent(src, sink, process=dm.build_entity)

    logger.info('- Paso 5: Ejecucion de insercion los datos en ORION')
    agent.run()
    
    smTaskUtil.notify_finish_task(sm.STATE_OK)


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
    logutil.configure_logger(cfg.LOG_BASEPATH+os.path.basename(__file__)+'.log', cfg.LOG_LEVEL)
    logger.info('Start module execution')
    
    sm.base_init()
    args=process_arguments()
    smTaskUtil = sm.SmTaskUtil(reference_id=args.reference_id, task_name=cfg.TASK3_SURVEYS_CODE, test_mode=False)

    try:
        main(smTaskUtil)
    except:
        error_detail = sm.get_exception_detail(sys.exc_info())
        logger.exception('Exception in main:'+error_detail)
        smTaskUtil.notify_finish_task(sm.STATE_ERROR, error_detail)
    
    logger.info('End module execution')