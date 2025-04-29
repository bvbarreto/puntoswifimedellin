#!python
# -*- coding: utf-8 -*-
'''
smpy_config.py
parametros globales

'''

#******************************************************************************
# Add root or main directory to python path for module execution
#******************************************************************************
if __name__ == '__main__':    
    import os, sys
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..'))) 
#******************************************************************************
    
import logging
import socket
import os
from enum import Enum

#%%
#******************************************************************************
# Globales
#******************************************************************************

logger = logging.getLogger(__name__)


#%%
#******************************************************************************
# functions
#******************************************************************************

def print_config():
    ''' 
    ===========================================================================
    Main function
    ===========================================================================     
    '''      
    print('HOSTNAME   : '+str(HOSTNAME))
    print('HOSTIPADDR : '+str(HOSTIPADDR))
    print('OSTYPE     : '+str(OSTYPE))
    print('os.name    : '+str(os.name))

def load_environ(parameter, default_value, param_type: type = str):
    ''' 
    ===========================================================================
    Busca variable de entorno, si no encuentra asigna valor por defecto
    ===========================================================================     
    '''

    new_param = os.environ[parameter] if parameter in os.environ else default_value

    if param_type == bool:
        new_param = True if str(new_param).lower() in ['true', 'enable'] else False

    elif param_type == int:
        new_param = int(new_param)

    # captura del nivel de logger
    if parameter == 'LOG_LEVEL':
        # Se obtiene el entero que representa el nivel de logger
        logger_level_int = logging.getLevelName(new_param)

        if isinstance(logger_level_int, int):
            new_param = logger_level_int
        else:
            # sino es un entero entonces el nivel por defecto INFO
            new_param = logging.INFO
    
    if parameter not in ['PYSERVER_PWD', 'SRC_TOKEN', 'ORION_TOKEN_PASSWORD']:
        print('load_environ - {}, {}: {}'.format(param_type, parameter, new_param))

    return new_param


#******************************************************************************
# Configuracion
#******************************************************************************


SERVICE_NAME="Agente Fiware Puntos WiFi"
SMPY_VERSION='1.0.0'
#Autenticacion servicio gestion
PYSERVICE_USR=load_environ('PYSERVER_USER','fiwaremed')
PYSERVICE_PWD=load_environ('PYSERVER_PWD','ospFiw23')

# CONFIG TAREA DEVICES
TASK1_DEVICES_CODE="TASK1_DEVICES"  # config: flow
TASK1_DEVICES_PATH="integration/devices_flow.py" # config: pyserver
TASK1_DEVICES_PERIOD_TYPE="cron" # config: pyserver

TASK2_ADVERTISING_CODE="TASK2_ADVERTISING"  # config: flow
TASK2_ADVERTISING_PATH="integration/advertising_flow.py" # config: pyserver
TASK2_ADVERTISINGS_PERIOD_TYPE="cron" # config: pyserver

TASK3_SURVEYS_CODE="TASK3_SURVEYS"  # config: flow
TASK3_SURVEYS_PATH="integration/surveys_flow.py" # config: pyserver
TASK3_SURVEYS_PERIOD_TYPE="cron" # config: pyserver


'''
    formato de tiempo 24horas
'''
TASK1_DEVICES_PERIOD_HOUR=int(load_environ('TASK1_DEVICES_PERIOD_HOUR','13',int)) # config: pyserver
TASK1_DEVICES_NEXT_RUN_TIME_SECONDS=int(load_environ('TASK1_DEVICES_NEXT_RUN_TIME_SECONDS','0',int)) # config: pyserver

TASK2_ADVERTISING_PERIOD_HOUR=int(load_environ('TASK2_ADVERTISING_PERIOD_HOUR','5',int)) # config: pyserver
TASK2_ADVERTISINGS_NEXT_RUN_TIME_SECONDS=int(load_environ('TASK2_ADVERTISINGS_NEXT_RUN_TIME_SECONDS','0',int)) # config: pyserver

TASK3_SURVEYS_PERIOD_HOUR=int(load_environ('TASK3_SURVEYS_PERIOD_HOUR','6',int)) # config: pyserver
TASK3_SURVEYS_NEXT_RUN_TIME_SECONDS=int(load_environ('TASK3_SURVEYS_NEXT_RUN_TIME_SECONDS','0',int)) # config: pyserver

# DATA SOURCE 

#SRC_CSV_PATH = load_environ('SRC_CSV_PATH','./integration/csv')
SRC_CSV_PATH = load_environ('SRC_CSV_PATH','./csv')
SRC_CSV_LOCATION_DATA = load_environ('SRC_CSV_LOCATION_DATA','datos.csv')

SRC_TOKEN = load_environ('SRC_TOKEN','6nJKqbpkYuEbpXRd1Q3YLtw1')
SRC_SOURCE_PROVIDER = load_environ('SRC_SOURCE_PROVIDER','www.ohmyfi.com/apiV2')

#TASK1
SRC_URL_GET_DEVICES = load_environ('SRC_URL_GET_DEVICES','https://www.ohmyfi.com/apiV2/dispositivos')
SRC_URL_GET_USERS = load_environ('SRC_URL_GET_USERS','https://www.ohmyfi.com/apiV2/usuarios')
SRC_URL_GET_LOGINS_VS_VISITS = load_environ('SRC_URL_GET_LOGINS_VS_VISITS','https://www.ohmyfi.com/apiV2/logins_vs_visitas_por_lugares')
SRC_URL_GET_GENERAL_STATISTICS = load_environ('SRC_URL_GET_GENERAL_STATISTICS','https://www.ohmyfi.com/apiV2/estadisticas_generales_del_tablero')

#TASK2
SRC_URL_GET_ADVERTISING_VS_CUSTOMER = load_environ('SRC_URL_GET_ADVERTISING_VS_CUSTOMER','https://www.ohmyfi.com/apiV2/publicidad_vs_datos_clientes')
SRC_URL_GET_ADVERTISING_SUMMARY = load_environ('SRC_URL_GET_ADVERTISING_SUMMARY','https://www.ohmyfi.com/apiV2/resumen_visualizacion_publicidades')

#TASK3
#TODO ENCUESTAS
SRC_URL_GET_CUSTOMER_RESPONSES = load_environ('SRC_URL_GET_CUSTOMER_RESPONSES','https://www.ohmyfi.com/apiV2/respuestas_cliente')
SRC_URL_GET_PERSONAL_INFORMATION = load_environ('SRC_URL_GET_PERSONAL_INFORMATION','https://www.ohmyfi.com/apiV2/datos_personales')

# ORION
#ORION_TOKEN_USER_NAME = load_environ('ORION_TOKEN_USER_NAME','admin-user')
#ORION_TOKEN_PASSWORD = load_environ('ORION_TOKEN_PASSWORD','admin-user')
ORION_TOKEN_USER_NAME = load_environ('ORION_TOKEN_USER_NAME','admin-user@hopu.eu')
ORION_TOKEN_PASSWORD = load_environ('ORION_TOKEN_PASSWORD','5uLFJdgF65DqcMbGUzArLd29L4TAAdFHAMq8')

# SINK
SINK_SERVICE = load_environ('SINK_SERVICE','WifiPoints')

SINK_SERVICE_PATH = load_environ('SINK_SERVICE_PATH','/medellin')

# ENTITYS
ENTITY_TYPE_DEVICES = load_environ('ENTITY_TYPE_DEVICES','WifiPointOfInterest')
ENTITY_TYPE_ADVERTISING = load_environ('ENTITY_TYPE_ADVERTISING','AdvertisingWifiPointOfInterest')
ENTITY_TYPE_SURVEYS = load_environ('ENTITY_TYPE_SURVEYS','SurveysWifiPointOfInterest')

'''
# ****** AZURE ******
# - ORION
ORION_TOKEN_URL = load_environ('URL_KEYCLOACK','https://medellinciudadinteligente.co/keycloak/auth/realms/fiware-server/protocol/openid-connect/token')
ORION_URL = load_environ('IP_ORION','medellinciudadinteligente.co')
ORION_PORT = load_environ('PORT_ORION','443')
# - SINK
SINK_SECURE = load_environ('SSL_ORION', True, bool)
SINK_ENABLE_AUTH_TOKEN = load_environ('ENABLE_AUTH_TOKEN', True, bool)
SINK_BASE_URL = load_environ('BASE_URL_ORION','/orion')
'''


# ****** OPENSHIFT ******
# - ORION
ORION_TOKEN_URL = load_environ('URL_KEYCLOACK','https://keycloak-fiware.apps.preprodalcaldia.medellin.gov.co/keycloak/auth/realms/fiware-server/protocol/openid-connect/token')
ORION_URL = load_environ('IP_ORION','orion-fiware.apps.preprodalcaldia.medellin.gov.co')
#ORION_PORT = load_environ('PORT_ORION','80')
ORION_PORT = load_environ('PORT_ORION','')
# - SINK
SINK_SECURE = load_environ('SSL_ORION', False, bool)
SINK_ENABLE_AUTH_TOKEN = load_environ('ENABLE_AUTH_TOKEN', True, bool)
#SINK_BASE_URL = load_environ('BASE_URL_ORION','/orion')
SINK_BASE_URL = load_environ('BASE_URL_ORION','/')



#%%
#******************************************************************************
# classes
#******************************************************************************
    
class OsType(Enum):
    ND=0
    LINUX=1
    WINDOWS=2    

#%%
#******************************************************************************
# Config bajo nivel
#******************************************************************************


HOSTNAME = socket.gethostname()
HOSTIPADDR =  socket.gethostbyname(HOSTNAME)
OSTYPE = OsType.ND
if os.name == 'posix':
    OSTYPE = OsType.LINUX
elif os.name == 'nt':
    OSTYPE = OsType.WINDOWS

# *** LOG Config ***
LOG_BASEPATH='./sm/log/'
LOG_LEVEL=load_environ('LOG_LEVEL','INFO') # 'CRITICAL', 'FATAL', 'ERROR', 'WARN', 'WARNING', 'INFO', 'DEBUG', 'NOTSET'

if OSTYPE == OsType.LINUX:
    PYTHONCMD='python'
    PY_BASEDIR='/sm/core/py/'    
elif OSTYPE == OsType.WINDOWS:
    PYTHONCMD='python'
    PY_BASEDIR='C:/sm/core/py/' 

#Microservicio pyserver (Gestion agente)
GLOBAL_PYSERVICE_CORE_IP='127.0.0.1'
GLOBAL_PYSERVICE_CORE_PORT=4999
GLOBAL_PYSERVICE_CORE_USER=PYSERVICE_USR
GLOBAL_PYSERVICE_CORE_PWD=PYSERVICE_PWD
GLOBAL_PYSERVICE_SERVER_HOST='0.0.0.0'   


#%%
#******************************************************************************
# Module Main Code
# Run if script call directoy
#******************************************************************************
if __name__ == '__main__':
    ''' 
    ===========================================================================
    Configure logger, utilities and call main function
    ===========================================================================     
    '''   
    import smcommon.logging_util as logutil
    logutil.configure_logger_basic()
    logger.info('Start module execution')

    try:
        print_config()
    except:
        logger.exception('Exception in main:')    
    
    logger.info('End module execution')
