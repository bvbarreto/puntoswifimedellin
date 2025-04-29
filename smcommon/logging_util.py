#!/sm/scripts/python
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 17 08:16:42 2017

"""

#******************************************************************************
# Add root or main directory to python path for module execution
#******************************************************************************
if __name__ == '__main__':    
    import os, sys
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..'))) 
#******************************************************************************

import sys
import logging
from logging.handlers import RotatingFileHandler

#%%
#******************************************************************************
# functions
#******************************************************************************

def configure_logger_basic():
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%H:%M:%S')     


def configure_logger(loggerfilepath, level=logging.DEBUG):
    """
    Configuracion general del logger
    """
    print("logger: ", loggerfilepath)
    ch = logging.StreamHandler(sys.stdout)
    ch.set_name("logsm")
    ch.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        
    root = logging.getLogger()
    root.setLevel(level)
    for handler in root.handlers:
        root.removeHandler(handler)
    root.addHandler(ch) 
    
    rotate_handler = RotatingFileHandler(loggerfilepath, maxBytes=10000000, backupCount=5)
    rotate_handler.set_name('rotateHandler')
    rotate_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')) 
    rotate_handler.setLevel(level)
    root.addHandler(rotate_handler)    
    
    
#%%
#******************************************************************************
# Module Main Code
# This code run only if this script is called directly
# This code helps to developer to test and know the usage of the module
#******************************************************************************
if __name__ == '__main__':    
    print('Start module execution:')
    
#    configure_logger_basic()
    configure_logger('/tmp/log.log', logging.DEBUG)
    
    logger = logging.getLogger(__name__)
    
    logger.debug("debug message")
    logger.info("info message")
    logger.warning("warning message")
    logger.error("error message")
    logger.critical("critical message")
    
    try:
        2/0
    except Exception as exc:
        logger.exception("exception message")