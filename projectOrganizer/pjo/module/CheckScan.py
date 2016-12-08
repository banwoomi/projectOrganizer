'''
Created on 2016. 10. 5.

@author: Sungho Lee
@version: 2015/09/16

'''

import os
import logging

from pjo.dao.SourceDao import SourceDao
from pjo.util.PjoUtil import CommonUtil


logger = logging.getLogger("devLog")
errLogger = logging.getLogger("errLog")

class CheckScan(object):

    #==============================================================================
    #  Constructor
    #==============================================================================
    def __init__(self):
        pass


    #==============================================================================
    #  Check Scan
    #==============================================================================
    def check_subject(self, source_id, title, member_id):

        logger.debug("source_id==[" + source_id + "] / title==[" + title + "] / member_id=[" + member_id + "]")


        '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
          1. Path
        '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
        cur_path = CommonUtil().f_getPath("S")
        subject_path = title

        path = os.path.join(cur_path, subject_path)
        logger.debug("Path==[" + path + "]")

        # folder list for scan
        scan_list = []
        
        # DAO
        dao = SourceDao()

        try:
            for comp in os.listdir(path):
    
                if os.path.isdir(os.path.join(path, comp)):
                    try:
                        comp = int(comp)
                        scan_list.append(comp)
                    except :
                        pass
                elif comp == 'subject':
                    with open(os.path.join(path, 'subject'), "r") as subj_file:
                        for line in subj_file:
                            if '##$SUBJECT_id' in line:
                                study_name = subj_file.next().strip()[1:-1]
                                logger.debug("Study Name==[" + study_name + "]")
    
                            elif '##$SUBJECT_location=' in line:
                                location = subj_file.next().strip()[1:-1]
                                logger.debug("Location==[" + location + "]")
    
    
    
    
            '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
              2. Scan Folder
            '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
            logger.debug("ScanList ==> %s", scan_list)
            for scan in sorted(scan_list):
    
                # Result
                scan_dic = {}
                
                scan_path = os.path.join(path, str(scan))
    
                # PID List
                pidArr = ""
                pdata_path = os.path.join(scan_path, "pdata")
                if os.path.isdir(pdata_path):
                    for pid in sorted(os.listdir(pdata_path)):
                        if os.path.isdir(os.path.join(pdata_path, pid)):
                            pidArr = pidArr + ":" + pid
                            scan_dic["pid_arr"] = pidArr
    
                    logger.debug("pidArr ==>" + pidArr)
                        
     
                if 'fid' in os.listdir(scan_path):
                    with open(os.path.join(scan_path, 'acqp')) as acqp_file:
                        
                        logger.debug("++++++++++++++++++ acqp start!!")
                        for line in acqp_file:
                            if "##$NSLICES=" in line:
                                scan_dic["n_slices"] = line[11:].strip()
                            elif "##$ACQ_protocol_name=" in line:
                                scan_dic["protocol_name"] = acqp_file.next()[1:-2]
                            elif "##$ACQ_echo_time=" in line:
                                strTe = acqp_file.next().strip()
                                scan_dic["te"] = CommonUtil().f_round(strTe, 2)
                            elif "##$ACQ_repetition_time" in line:
                                scan_dic["tr"] = acqp_file.next().strip()
     
                    with open(os.path.join(scan_path, 'method')) as mtd_file:
    
                        logger.debug("++++++++++++++++++ method start!!")
                        for line in mtd_file:
                             
                            scan_dic["scan"] = scan
                             
                            if "##$PVM_Matrix=" in line:
                                scan_dic["matrix"] = 'x'.join(mtd_file.next().strip().split())
                            elif "##$PVM_SpatDimEnum=" in line:
                                scan_dic["dim"] = line[19:].strip()
                                if scan_dic["dim"] == '3D':
                                    scan_dic["n_slices"] = ''
                            elif "##$PVM_NRepetitions=" in line:
                                scan_dic["frame"] = line[20:].strip()
     
                         
                        logger.debug("Scan Result ==> %s", scan_dic)
                         
                        # Insert Result
                        dao.insertScanInfo(source_id, scan_dic, member_id)

                else:
                    pass
        except Exception, e:
            errLogger.error(e)
