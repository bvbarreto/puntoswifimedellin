#!/sm/scripts/python
# -*- coding: utf-8 -*-

'''
Created 2023/07/01
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
properties_list =[
        {"orion":"identifier", "record":"identificador", "type":""},
        {"orion":"zoneName", "record":"nombre_zona", "type":""},
        {"orion":"zoneGroup", "record":"grupo", "type":""},
        {"orion":"uniqueDevices", "record":"dispositivos_unicos", "type":""},
        {"orion":"averageDeviceDay", "record":"promedio_dispositivos_dia", "type":""},
        {"orion":"maximumTotalDevices", "record":"total_max_dispositivos", "type":""},
        {"orion":"minimumTotalDevices", "record":"total_min_dispositivos", "type":""},
        {"orion":"averageSmartphoneDay", "record":"promedio_smartphone_dia", "type":""},
        {"orion":"totalSmartphone", "record":"total_smartphone", "type":""},
        {"orion":"averageTabletDay", "record":"promedio_tablet_dia", "type":""},
        {"orion":"totalTablet", "record":"total_tablet", "type":""},
        {"orion":"averagePcDay", "record":"promedio_pc_dia", "type":""},
        {"orion":"totalPc", "record":"total_pc", "type":""},
        {"orion":"dataDate", "record":"fecha_de_los_datos", "type":""},
        {"orion":"newDevices", "record":"dispositivos_nuevos", "type":""},
        {"orion":"recurringDevices", "record":"dispositivos_recurrentes", "type":""},
        {"orion":"sessionTimeMinutes", "record":"tiempo_de_sesion_minutos", "type":""},
        {"orion":"megabyteUpload", "record":"subida_megabytes", "type":""},
        {"orion":"megabyteDownload", "record":"bajada_megabytes", "type":""},
        {"orion":"sessions", "record":"sesiones_generales", "type":""},
        {"orion":"consumers", "record":"consumidores", "type":""},
        {"orion":"logins", "record":"logins", "type":""},
        {"orion":"averageDailyLogins", "record":"promedio_logins_dia", "type":""},
        {"orion":"averageLoginTime", "record":"tiempo_promedio_login", "type":""},
        {"orion":"maximumTotalLogins", "record":"total_max_logins", "type":""},
        {"orion":"minimumTotalLogins", "record":"total_min_logins", "type":""},
        {"orion":"visits", "record":"visitas", "type":""},
        {"orion":"averageDailyVisits", "record":"promedio_visitas_dia", "type":""},
        {"orion":"maximumTotalVisits", "record":"total_max_visitas", "type":""},
        {"orion":"minimumTotalVisits", "record":"total_min_visitas", "type":""},
        {"orion":"averageDailySessions", "record":"total_max_sesiones", "type":""},
        {"orion":"maximumTotalSessions", "record":"total_smartphone", "type":""},
        {"orion":"minimumTotalSessions", "record":"total_min_sesiones", "type":""}

    ]

def build_entity(row: Row) -> str:
    logger.info('build_entity')
    fail_list = []
    id_lugar  = row.record['id_lugar']
    id = "urn:ngsi-ld:{}:{}".format(cfg.ENTITY_TYPE_DEVICES, str(id_lugar))
    
    dm_entity = DataModel(id = id, type = cfg.ENTITY_TYPE_DEVICES)
    dm_entity.add("dataProvider", row.provider)
    
    for property in properties_list:
        ou.add_to_dm(fail_list,dm_entity, property["orion"], row.record[property["record"]], property["type"])


    ou.add_geojson_to_dm(fail_list,dm_entity, "location", float(row.record["Longitud"]), float(row.record["Latitud"]))
    
    if fail_list:
        logger.warning('[{}] Fuera del modelo de datos: {}'.format(id_lugar, fail_list))

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