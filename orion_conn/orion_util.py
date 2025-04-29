# -*- coding: utf-8 -*-
'''
Created 2023/09/01
'''

# ******************************************************************************
# Add root or main directory to python path for module execution
# ******************************************************************************
if __name__ == '__main__':
    import os, sys

    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# ******************************************************************************

import logging
import pandas as pd
import re
import geojson
from pyngsi.ngsi import DataModel

#******************************************************************************
# globals
#******************************************************************************
logger = logging.getLogger(__name__)


#******************************************************************************
# Excepciones
#******************************************************************************

class SmException(Exception):
    """
    Excepcion controlada por la libre SM
    """
    pass

#%%
#******************************************************************************
# functions
#******************************************************************************

LIST_SPECIAL_CHARACTERS_ORION = ["<",">",'"',"'","=",";","(",")", "\u2013"]
PATRON_SPECIAL_CHARACTERS_ORION = "|".join(re.escape(caracter) for caracter in LIST_SPECIAL_CHARACTERS_ORION)

def clean_characters_to_orion (value):
    for char in LIST_SPECIAL_CHARACTERS_ORION:
        value = value.replace(char,"")
    return value


def add_to_dm(fail_list: list, data_model: DataModel, name: str, value, type: str = None):
    '''
    Agrega el atributo al Data Model.
    Valida el valor a agregar:
        si es None o NaN:
        1) Y tiene Type, lo agrega al modelo solo con tipo, es decir el valor NULL en Orion
        2) Y NO tiene Type, no lo agrega al modelo. pues esto no es soportado por NGSI -Orion, debido a que requiere un tipo de dato.
    Si es el valor es instancia de STR:
        1) Ejecuta encode y decode en utf-8
        2) Si contiene caracteres especiales:
            Limpia todos los caracteres especales contenidos en: LIST_SPECIAL_CHARACTERS_ORION

    type (dominio de valores):
        "DateTime"
        "URL"
        "STRING_URL_ENCODED"
        "Text"
        "Boolean"
        "Number"
        "Number"
        # the value datetime MUST be UTC
        "DateTime".strftime("%Y-%m-%dT%H:%M:%SZ")
        "geo:json"
        "geo:json"
        "Array"
        "Property"
    '''
    if _is_None(value):
        if type:
            # se agrega el atributo solo con el tipo, esto permite insertar Nulos en orion
            data_model[name] = {"type": type}
        else:
            fail_list.append('{}: None|NaN'.format(name))

        return

    if isinstance(value, str):
        # Codificar el texto a bytes en UTF-8
        bytes_utf8 = value.encode('utf-8', 'replace')

        # Decodificar nuevamente a UTF-8, reemplazando caracteres no soportados
        value = bytes_utf8.decode('utf-8', 'replace')

        if _contains_special_characters(value):
            value = clean_characters_to_orion(value)
            logger.debug('Se limpiaron caracteres no soportados por orion: {}'.format(value))

    data_model.add(name, value)
    return

def add_geojson_to_dm(fail_list: list, data_model: DataModel, name: str, longitud: float, latitud: float):
    '''
    Agrega al Data Model y valida si el valor a agregar es una coordenada, en tal caso lo descarta, es decir no lo agrega al modelo,
    pues esto no es soportado por NGSI -Orion, debido a que requiere un tipo de dato.
    '''
    if _is_gps_coordinate(longitud, latitud):
        data_model.add(name, geojson.Point((float(latitud), float(longitud))))
    else:
        fail_list.append('{}: sin formato de coordenada'.format(name))

    return

def _contains_special_characters(cadena):
    '''
    # Define una expresión regular que busca caracteres no alfanuméricos
    patron = re.compile(r'[^\w\s]', re.UNICODE)
    # Busca si la cadena contiene caracteres especiales
    return bool(patron.search(cadena))
    '''
    # Busca si la cadena contiene caracteres especiales
    return bool(re.search(PATRON_SPECIAL_CHARACTERS_ORION, cadena))

def _is_gps_coordinate(longitud, latitud):

    if ( _is_None(longitud)  or _is_None(latitud)):
        return False

    if not isinstance(longitud, float) and not isinstance(latitud, float):
        return False

    if -90 <= latitud <= 90 and -180 <= longitud <= 180:
        return True
    else:
        return False

def _is_None(value):
    if (value is None or pd.isna(value)):
        return True

    return False