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
    
import logging
import sys
import smcommon.smpy_util as sm

from pyngsi.sink import SinkOrion

import requests
import json

from os import environ

#%%
#******************************************************************************
# globals
#******************************************************************************
logger = logging.getLogger(__name__)

#%%
#******************************************************************************
# CLASE PRINCIPAL
#******************************************************************************
class OrionSink():

    def __init__(self, host_name: str, port: int, service: str, service_path: str, secure: bool, base_url: str,
                 orion_token_user_name: str,
                 orion_token_password: str,
                 orion_token_url: str,
                 enable_auth_token: bool = True):
        logger.info('OrionSink: inicia el constructor')

        fail_param_list = []

        # - host_name
        if host_name is None or host_name == "":
            fail_param_list.append("host_name")
        # - port
        if port is None:
            fail_param_list.append("port")
        # - service
        if service is None or service == "":
            fail_param_list.append("service")
        # - service_path
        if service_path is None or service_path == "":
            fail_param_list.append("service_path")
        # - base_url
        if base_url is None or base_url == "":
            fail_param_list.append("base_url")
        # - secure
        if secure is None:
            fail_param_list.append("secure")
        # - orion_token_user_name
        if orion_token_user_name is None or orion_token_user_name == "":
            fail_param_list.append("orion_token_user_name")
        # - orion_token_password
        if orion_token_password is None or orion_token_password == "":
            fail_param_list.append("orion_token_password")
        # - orion_token_url
        if orion_token_url is None or orion_token_url == "":
            fail_param_list.append("orion_token_url")

        if len(fail_param_list) > 0:
            raise ValueError('Parametro None o Vacio: {}'.format(fail_param_list))

        self.host_name = host_name
        self.port = port
        self.service = service
        self.service_path = service_path
        self.secure = secure
        self.orion_token_user_name = orion_token_user_name
        self.orion_token_password = orion_token_password
        self.orion_token_url = orion_token_url
        self.enable_auth_token = enable_auth_token
        self.base_url = base_url
        return

    def _get_access_token(self):
        logger.info('OrionSink::_get_access_token')

        payload='username={}&password={}&grant_type=password&client_id=fiware-login'.format(self.orion_token_user_name, self.orion_token_password)
        headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
        }

        try:
            print("orion_token_url: ", self.orion_token_url)
            print("payload: ", payload)
            response = requests.request("POST",
                                        self.orion_token_url,
                                        headers=headers,
                                        data=payload,
                                        verify=False)

            data = json.loads(response.text)
            print("data: ", data)
            access_token = data['access_token']

            if access_token:
                logger.info('Nuevo token de Orion obtenido!')

            return access_token

        except Exception as e:
            logger.exception('Fallo consulta de TOKEN-ORION: excepción: %s', e)
            raise Exception('Fallo consulta de TOKEN-ORION')



    def getSinkOrion(self) -> SinkOrion:
        logger.info('OrionSink::getSinkOrion')

        sink = SinkOrion(hostname=self.host_name,
                         port=self.port,
                         servicepath=self.service_path,
                         baseurl=self.base_url,
                         post_query=None,
                         post_endpoint="/v2/op/update",
                         secure=self.secure
                         )

        headers = {
            'fiware-service': self.service,
            'fiware-servicepath': self.service_path,
            'Content-Type': 'application/json',
            #'Authorization': 'Bearer ' + token
        }

        logger.info('Autenticación por Token en Orion (enable_auth_token) = {}'.format(str(self.enable_auth_token)))
        if self.enable_auth_token:
            token = self._get_access_token()
            headers['Authorization'] = 'Bearer ' + token

        sink.headers = headers
        print("sink: ", sink)
        print("token: ", token)
        logging.basicConfig(level=logging.DEBUG)
        logging.debug(environ)

        #return environ
        return sink


def main(parameters=None):
    """ 
    ===========================================================================
    Main function
    ===========================================================================     
    """
    try:
        sink_orin_constructor = SinkOrinConstructor(
                host_name=parameters["host_name"],
                port=parameters["port"],
                service=parameters["service"],
                service_path=parameters["service_path"],
                secure=parameters["secure"])

        sink = sink_orin_constructor.getSinkOrion()
        return {'success': True}
    except:
        errorDetail = sm.getExceptionDetail(sys.exc_info())
        logger.exception("Exception in main:"+errorDetail) 
        return {'error' : errorDetail}


#%%
#******************************************************************************
# Module Main Code
# Run if script call directoy
#******************************************************************************
if __name__ == '__main__':
    """ 
    ===========================================================================
    Configure logger, utilities and call main function
    ===========================================================================     
    """   
    import smcommon.logging_util as logutil
    logutil.configureLoggerBasic()
    #logutil.configureLogger(cfg.LOG_BASEPATH+os.path.basename(__file__)+'.log', logging.DEBUG)
    logger.info('Start module execution')
    
    parameters = {
            'host_name': '',
            'port': 0,
            'service': '',
            'service_path': '',
            'secure': False
        }
    response = main(parameters)
    logger.info("response="+str(response))
    
    logger.info('End module execution')