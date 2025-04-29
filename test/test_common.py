#!/sm/scripts/python
# -*- coding: utf-8 -*-
"""
Pruebas unitarias

"""

#******************************************************************************
# Add root or main directory to python path for module execution
#******************************************************************************
if __name__ == '__main__':
    import os, sys
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..')))
#******************************************************************************


import unittest
import datetime
import config.smpy_config as cfg
import smcommon.smpy_util as sm
import argparse




class TestsSmcommon(unittest.TestCase):

    def test_logging(self):
        import logging
        import smcommon.logging_util as logutil
        logutil.configure_logger_basic()
        logutil.configure_logger('/tmp/test.log', logging.DEBUG)     

    def test_dates(self):
        date_arr = sm.date2array(datetime.date.today())
        self.assertEqual(len(date_arr), 3)      
        datetime_arr = sm.datetime2array(datetime.datetime.now())
        self.assertEqual(len(datetime_arr), 7)
        time_arr = sm.time2array(datetime.datetime.now())
        self.assertEqual(len(time_arr), 4)
        dt=sm.restvalue_to_datetime('2021-06-25T15:30:30')
        self.assertTrue(dt.month==6)
        d=sm.restvalue_to_date('2021-06-25')
        self.assertTrue(d.month==6)
        #Pruebas nulos
        r = sm.datetime2array(None)
        self.assertTrue(r==None)
        r = sm.date2array(None)
        self.assertTrue(r==None)
        r = sm.time2array(None)
        self.assertTrue(r==None)
        r = sm.restvalue_to_datetime(None)
        self.assertTrue(r==None)  
        r = sm.restvalue_to_date(None)
        self.assertTrue(r==None)   
        r = sm.get_exception_detail(None)
        self.assertTrue(r=="Error desconocido")                                         
           
    def test_files(self):
        s = "/tmp/pytest_s"
        t = "/tmp/pytest_t"
        
        sm.make_dir(s)
        sm.make_dir(t)
        sm.remove_files(s)
        sm.remove_files(t)
        
        success=True
        if cfg.OSTYPE == cfg.OsType.LINUX:
            f1="/source1.txt"
            f2="/source2.txt"
            f3="/source3.txt"
            f4="/source4.txt"
            f5="/source5.txt"
            sm.execute_shell("echo hola  > "+s+f1)
            sm.execute_shell("echo hola2 > "+s+f2)
            sm.copy_files(s, t)
            sm.execute_shell("echo hola3 > "+s+f3)
            sm.move_file(s+f3, t)
            sm.remove_file(t+f3)
            sm.execute_shell("echo hola4 > "+s+f4)
            sm.copy_file(s+f4, t)
            sm.move_rename_file(s+f1, t+f5)
            sm.remove_files(s)
            print(sm.list_files(t)) 
            sm.remove_dir(t)
            sm.remove_dir(s)
            
        self.assertTrue(success, "Modifica archivos OK")

        #pruebas envio excepcion
        fn="noexiste/test"
        try:
            sm.remove_dir(fn)
            self.assertFail("No genera Exp") 
        except:
            pass 
        try:
            sm.remove_file(fn)
            self.assertFail("No genera Exp") 
        except:
            pass           
        try:
            sm.execute_shell(fn)
            self.assertFail("No genera Exp") 
        except:
            pass 
        try:
            sm.copy_file,(fn, fn)
            self.assertFail("No genera Exp") 
        except:
            pass  
        try:
            sm.move_file,(fn, fn)
            self.assertFail("No genera Exp") 
        except:
            pass 
        try:
            sm.move_rename_file,(fn, fn)
            self.assertFail("No genera Exp") 
        except:
            pass                                             
        
    def test_taskutil(self):
        tstUtil = sm.SmTaskUtil(1)
        self.assertFalse(tstUtil==None, "SmTaskUtil no e snull")
        
    def test_argsparser(self):
        try:
            parser = argparse.ArgumentParser(prog="test")  
            sm.base_add_args(parser, "1.0")
        except:
            self.assertFail("base_add_args Exc")

    def test_getexception(self):
        r=sm.get_exception_detail("exc info")
        self.assertTrue(r!=None, "get_exception_detail OK")

    def test_config(self):
        import os
        os.environ["SMAPP_ENV"] = "development"
        import config.smpy_config as cfg
        cfg.print_config()
        os.environ["SMAPP_ENV"] = "preprod"
        import config.smpy_config as cfg
        cfg.print_config()           
           
     
class TestsPyserver(unittest.TestCase):

    def test_get_response(self):  
        import smpyserver.pyserver_common as pyserver_common
        r=pyserver_common.get_response(pyserver_common.RESULT_OK)
        self.assertTrue(r!=None, "get_response OK")
        r=pyserver_common.get_response(pyserver_common.RESULT_OK, "detalle", {"a": "b"})
        self.assertTrue(r!=None, "get_response OK")

"""     def test_pyserver(self):  
        import smpyserver.sm_pyserver as sm_pyserver
        data={'header': {'source':'origen'}}
    
        r=sm_pyserver.smhealth()
        self.assertFalse(r==None, "smhealth no es null")
        r=sm_pyserver.smhealth("d")
        self.assertFalse(r==None, "smhealth no es null")
        r=sm_pyserver.smhealth("detail")
        self.assertFalse(r==None, "smhealth no es null")  """ 

        #r=sm_pyserver.process_arguments()
        #self.assertFalse(r==None, "smhealth no es null")      


if __name__ == '__main__':
    unittest.main()
