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

import os
import pandas as pd
import logging
import datetime
import time

import requests

import config.smpy_config as cfg
import smcommon.smpy_util as sm
from enum import Enum
from pathlib import Path
import csv
#%%
#******************************************************************************
# globals
#******************************************************************************
logger = logging.getLogger(__name__)

__version__ = '0.0.1'

CLEAN_FILE_CSV = "clean.csv"
#%%
#******************************************************************************
# Otras clases utilitarias
#******************************************************************************
# excepcion que permitira identificar cuando se requiere solictar un nuevo token
class InvalidTokenExcepcion(Exception):
    def __init__(self, message):
        super().__init__(message)

# Enumerador de tipos de peticion
class RequestType(Enum):
    ADVERTISING = "REQUEST_ADVERTISING"
    ADVERTISING_SUMMARY = "REQUEST_ADVERTISING_SUMMARY"


#%%
#******************************************************************************
# CLASE PRINCIPAL
#******************************************************************************
class DataSource():
    
    current_token = None

    def __init__(self, token: str, url_advertising: str, url_advertising_summary: str):
        logger.info('DataSource: constructor')
        fail_param_list = []

      
        # - token
        if token is None or token == "":
            fail_param_list.append("token")

        # - url_advertising
        if url_advertising is None or url_advertising == "":
            fail_param_list.append("url_advertising")

        # - url_advertising_summary
        if url_advertising_summary is None or url_advertising_summary == "":
            fail_param_list.append("url_advertising_summary")
      
        if len(fail_param_list) > 0:
            raise ValueError('Parametro None o Vacio: {}'.format(fail_param_list))

        self.current_token = token
        self.url_advertising = url_advertising
        self.url_advertising_summary = url_advertising_summary
       

        self.urls = {
            RequestType.ADVERTISING: url_advertising,
            RequestType.ADVERTISING_SUMMARY: url_advertising_summary          
        }

        return

        
    def _validate_response(self, response, reference_label):
        logger.info('_validate_response: {}'.format(response))
        '''
        valida el que Response sea diferente de None y status_code != 200
        '''
        error_msg = None
        status_code = None
        print("response: ", response)
        print("code: ", response.status_code)
        # Verificar el estado de la respuesta y procesar los datos.
        if response is None:
            error_msg = 'Fallo {}: Response es None'.format(reference_label)
        elif response.status_code != 200:
            status_code = response.status_code
            try:
                error_msg = 'Fallo {}: {} - {}'.format(reference_label, status_code, response.json()['error'])
            except Exception as err:
                error_msg = 'Fallo {}: {} - {}'.format(reference_label, status_code, response.json()['msg'])
            response.close()

        if error_msg:
            logger.error(error_msg)

            # 401 / EL token es invalido.
            if status_code == 401:
                raise InvalidTokenExcepcion(error_msg)

            raise Exception(error_msg)

        return
           
    def _get_token(self, refresh_token=False):
        ''' 
        ===========================================================================
        Obtiene el token de seguridad para realizar las peticiones al API 
        ===========================================================================     
        '''       
        if refresh_token or self.current_token is None:
            logger.info('Se refresca el Token')

            data = {
                'user': self.token_user_name,
                'pass': self.token_password
            }

            # Solicitud POST para obtener el token.
            response = requests.post(self.token_url, data=data)
            self._validate_response(response, '_get_token')

            self.current_token = response.json()['token']

            if self.current_token:
                logger.info('Nuevo token obtenido!')
            response.close()
        return

    def _execute_request(self, request_url):
        logger.info('_execute_request: {}'.format(request_url))
        response = None
        response_json = None

        headers = {
            'APIKEY-OMF': f'{self.current_token}'
        }
       
        response = requests.get(request_url, headers=headers)
       
        self._validate_response(response, '_execute_request')

        response_json = response.json()
        #print(response_json)
        response.close()

        return response_json

    # Ejecucion con reintento y refrescamiento de token
    def _request_execution_flow(self, request_url):
        json_response = None
        #self._get_token()
        
        # intenta hasta 3 veces para obtener una respuesta
        #get_refresh_token = False

        for i in range(1):
            logger.info('Iteración consulta: #{}'.format(i + 1))

            try:
                json_response = self._execute_request(request_url)

            #401Unauthorized
            except InvalidTokenExcepcion as ite:                
                logger.error('EL token es invalido: %s', ite)
                break

            except Exception as e:
                # no requiere reinteos
                logger.exception('Error en ejecución de la petición a la fuente: %s', e)
                raise

            # finaliza el loop
            if json_response: 
               break           

        return json_response    

# Consulta, obtiene el DF del csv y lo convierte a DataFrame
    def _get_df_csv_data(self) -> pd.DataFrame:
        logger.debug('_get_df_csv_data:')   

        #si existe datos
        data_csv = Path(cfg.SRC_CSV_PATH) / cfg.SRC_CSV_LOCATION_DATA
        df = None
        
        if data_csv.exists():
            df = pd.read_csv(data_csv)
            df = df.rename(columns={"Lugar":'nombre_zona'})
            df = df.drop_duplicates()
            df = df.dropna()            
           
        else:
           raise Exception("No se encuentra la ruta {} o el archivo {}".format(cfg.SRC_CSV_PATH,cfg.SRC_CSV_LOCATION_DATA)) 

        return df
    
    # Consulta, obtiene el JSON del cuerpo (segun el tipo de respuesta) y lo convierte a DataFrame
    def _get_df_data(self, request_type: RequestType) -> pd.DataFrame:
        logger.debug('_get_df_data:')

        #fecha = datetime.date.today() - datetime.timedelta(days=1)   
        fecha = '2023-07-11'     
        hora_inicio = '00:00'
        hora_final = '23:59'       
        
        filter_message = f"?fecha_inicio={fecha}&fecha_final={fecha}&hora_inicio={hora_inicio}&hora_final={hora_final}"
        json_response = self._request_execution_flow(str(self.urls[request_type]+str(filter_message)))

        return pd.DataFrame.from_dict(json_response)

    #Funcion principal: hace las dos peticiones
    def get_df_merge_data(self) -> pd.DataFrame:
        logger.info('Start get_df_merge_data')      
        
        pd.set_option('display.max_columns', None)

        df_advertising   = self._get_df_data(RequestType.ADVERTISING)
        if df_advertising.empty == True:
            raise Exception("No hay datos en la consulta advertising") 
        
        df_advertising_summary   = self._get_df_data(RequestType.ADVERTISING_SUMMARY)
        if df_advertising_summary.empty == True:
            raise Exception("No hay datos en la consulta summary") 

        df = pd.merge(
            df_advertising,
            df_advertising_summary,
            how="inner",
            left_on =['id_lugar','nombre_publicacion'],
            right_on=['id_lugar','publicidad']
        )

        df = df.loc[:, [
            'mac_usuario','id_lugar','lugar_clic', 'genero',  'ciudad','rango_edad', 
            'nivel_educativo','id_publicacion', 'nombre_publicacion','fecha_clic','creado_db','grupo']]
  
             
        df = df.drop_duplicates()

        # Limpian espacios multiples en medio y se eliminan espacios al inicio y al final
        df['mac_usuario'] = df['mac_usuario'].fillna('')
        df['mac_usuario'] = df['mac_usuario'].str.strip()
        df['mac_usuario'] = df['mac_usuario'].replace(r"\s+", " ", regex=True)
        df = df[df['mac_usuario'] != ""]
        return df


#%%
#******************************************************************************
# functions utilitarias
#******************************************************************************

def main(smTaskUtil):
    '''
    ===========================================================================
    Main function
    ===========================================================================
    '''
    logger.info('main PARAMETROS:' + str(smTaskUtil))

    smTaskUtil.notify_executing_task()

    # construir payload
    wifi_points = DataSource()

    df_data = wifi_points.get_df_merge_data()
    print(df_data.head(2))
    smTaskUtil.notify_finish_task(sm.FinishType.OK)

    # return response_devices, response_devices_now

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
