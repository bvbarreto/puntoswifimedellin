#!/sm/scripts/python
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


from pyngsi.ngsi import DataModel
from pyngsi.sources.source import Source, Row
import logging
import datetime
import geojson

import config.smpy_config as cfg
import smcommon.smpy_util as sm
import orion_conn.orion_util as ou

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

#TODO mapear los campos
properties_list =[
    {"orion": "macAddress", "record": "mac_usuario", "type": ""},
    {"orion": "zoneId", "record": "id_lugar", "type": ""},
    {"orion": "zoneName", "record": "lugar_respuesta", "type": ""},
    {"orion": "identifier", "record": "identificador", "type": ""},
    {"orion": "questionName", "record": "nombre_pregunta", "type": ""},
    {"orion": "question", "record": "pregunta", "type": ""},
    {"orion": "answer", "record": "respuesta", "type": ""},
    {"orion": "answerDate", "record": "fecha_respuesta", "type": ""},
    {"orion": "answerHour", "record": "hora_respuesta", "type": ""},
    {"orion": "zoneGroup", "record": "grupo", "type": ""},
    {"orion": "gender", "record": "genero", "type": ""},
    {"orion": "educationalLevel", "record": "nivel_educativo", "type": ""},
    {"orion": "ageRange", "record": "rango_edad", "type": ""},
    {"orion": "occupation", "record": "ocupacion", "type": ""},
    {"orion": "maritalStatus", "record": "estado_civil", "type": ""},
    {"orion": "socioeconomicStratum", "record": "estrato", "type": ""},
    {"orion": "numberChildren", "record": "cantidad_hijos", "type": ""},
    {"orion": "ethnicity", "record": "etnia", "type": ""},
    {"orion": "comunicationDevices", "record": "tipo_dispositivo", "type": ""},
    {"orion": "operatingSystem", "record": "sistema_operativo", "type": ""},
    {"orion": "webClient", "record": "navegador", "type": ""}

    ]

def build_entity(row: Row) -> str:
    logger.info('build_entity')
    fail_list = []
    mac  = row.record['mac_usuario']
    id = "urn:ngsi-ld:{}:{}".format(cfg.ENTITY_TYPE_SURVEYS, str(mac))
    
    dm_entity = DataModel(id = id, type = cfg.ENTITY_TYPE_SURVEYS)
    dm_entity.add("dataProvider", row.provider)
    
    for property in properties_list:
        ou.add_to_dm(fail_list,dm_entity, property["orion"], row.record[property["record"]], property["type"])

    
    if fail_list:
        logger.warning('[{}] Fuera del modelo de datos: {}'.format(mac, fail_list))

    str_data = '{ "actionType": "append", "entities": ['+dm_entity.json()+']}'
    
    return str_data.encode('utf-8')



def main(smTaskUtil):
    ''' 
    ===========================================================================
    Main function
    ===========================================================================     
    '''
    logger.info('main PARAMETROS:' + str(smTaskUtil))


    smTaskUtil.notify_executing_task()

    pass
    
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