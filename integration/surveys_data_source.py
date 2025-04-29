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

#%%
#******************************************************************************
# globals
#******************************************************************************
logger = logging.getLogger(__name__)

__version__ = '0.0.1'

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
    PERSONAL_INFORMATION = "REQUEST_PERSONAL_INFORMATION"
    CUSTOMER_RESPONSE = "REQUEST_CUSTOMER_RESPONSE"


#%%
#******************************************************************************
# CLASE PRINCIPAL
#******************************************************************************
class DataSource():
    
    current_token = None

    def __init__(self, token: str, url_personal_information: str, url_customer_response: str):
        logger.info('DataSource: constructor')
        fail_param_list = []

      
        # - token
        if token is None or token == "":
            fail_param_list.append("token")
        # - url_advertising
        if url_personal_information is None or url_personal_information == "":
            fail_param_list.append("url_personal_information")
        if url_customer_response is None or url_customer_response == "":
            fail_param_list.append("url_customer_response")

      
        if len(fail_param_list) > 0:
            raise ValueError('Parametro None o Vacio: {}'.format(fail_param_list))

        self.current_token = token
        self.url_personal_information = url_personal_information
        self.url_customer_response = url_customer_response
       

        self.urls = {
            RequestType.PERSONAL_INFORMATION: url_personal_information, 
            RequestType.CUSTOMER_RESPONSE: url_customer_response          
        }

        return

        
    def _validate_response(self, response, reference_label):
        '''
        valida el que Response sea diferente de None y status_code != 200
        '''
        error_msg = None
        status_code = None

        # Verificar el estado de la respuesta y procesar los datos.
        print("response.status_code: ", response.status_code)
        #print("response: ", response.text)
        if response is None:
            error_msg = 'Fallo {}: Response es None'.format(reference_label)
        elif response.status_code != 200:     
            status_code = response.status_code
            response.close()
            error_msg = 'Fallo {}: {} - {}'.format(reference_label, status_code, response.json()['error'])

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
        logger.debug('_execute_request: {}'.format(request_url))
        response = None
        response_json = None

        headers = {
            'APIKEY-OMF': f'{self.current_token}'
        }
       
        response = requests.get(request_url, headers=headers)
       
        self._validate_response(response, '_execute_request')

        response_json = response.json()
        
        response.close()

        return response_json

    # Ejecucion con reintento y refrescamiento de token
    def _request_execution_flow(self, request_url):
        json_response = None
                
        # intenta hasta 3 veces para obtener una respuesta
        
        for i in range(1):
            logger.info('Iteración consulta: #{}'.format(i + 1))

            try:
                json_response = self._execute_request(request_url)

            #401Unauthorized
            except InvalidTokenExcepcion as ite:
                # EL token es invalido, termina el programa, el token no se refresca
                
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

  
    # Consulta, obtiene el JSON del cuerpo (segun el tipo de respuesta) y lo convierte a DataFrame
    def _get_df_data(self, request_type: RequestType) -> pd.DataFrame:
        logger.debug('_get_df_data:')
                
        fecha = datetime.date.today() - datetime.timedelta(days=1)      
        fecha = '2023-09-30'
        hora_inicio = '00:00'
        hora_final = '23:59'       
        
        filter_message = f"?fecha_inicio={fecha}&fecha_final={fecha}&hora_inicio={hora_inicio}&hora_final={hora_final}"
        json_response = self._request_execution_flow(str(self.urls[request_type]+str(filter_message)))

        return pd.DataFrame.from_dict(json_response)

    #Funcion principal: realiza  peticiones y merge
    def get_df_merge_data(self) -> pd.DataFrame:
        logger.info('Start get_df_merge_data')      
        pd.set_option('display.max_columns', None)

        df_customer_response   = self._get_df_data(RequestType.CUSTOMER_RESPONSE)
        if df_customer_response.empty == True:
            raise Exception("No hay datos en la consulta") 

        df_personal_information   = self._get_df_data(RequestType.PERSONAL_INFORMATION)
        if df_personal_information.empty == True:
            raise Exception("No hay datos en la consulta")
        
       
        #ajuste a las columnas
        #df = df_customer.rename(columns={'lugar':'nombre_zona'})  

        df = pd.merge(
            df_customer_response,
            df_personal_information,
            how="inner",
            left_on =['id_lugar','mac_usuario'],
            right_on=['id_lugar','mac_usuario']
        )
  
             
        df = df.drop_duplicates()

        df = df.loc[:, [
            'mac_usuario','id_lugar','lugar_respuesta','grupo', 'identificador',  'nombre_pregunta','pregunta','respuesta' ,'fecha_respuesta','hora_respuesta',
            'genero','nivel_educativo','rango_edad','ocupacion','estado_civil','estrato','cantidad_hijos','etnia','tipo_dispositivo','sistema_operativo','navegador']]

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
