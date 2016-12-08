'''
Created on 2016. 10. 5.

@author: Woomya
'''
import logging
import os
import shutil
from datetime import datetime
from django.utils import timezone
from django.utils import dateformat

from pjo.dao.ProjectDao import ProjectDao
from pjo.dao.CommonDao import CommonDao


logger = logging.getLogger("devLog")
errLogger = logging.getLogger("errLog")

class CommonUtil(object):


    #==============================================================================
    #  Constructor
    #==============================================================================
    def __init__(self):
        # do nothing
        pass
        
        

    #==============================================================================
    #  session setting
    #==============================================================================
    def setSession(self, request, researcherObj):
    
        request.session['member_id']  = researcherObj.id
        request.session['first_name'] = researcherObj.first_nm
        request.session['last_nm']    = researcherObj.last_nm
        request.session['initial_nm'] = researcherObj.initial_nm
        request.session['authority'] = researcherObj.authority
        request.session['last_touch'] = datetime.now()
    
    
    
    #==============================================================================
    #  session delete
    #==============================================================================
    def delSession(self, request):
    
        member_id = request.session.get("member_id")
        if member_id is not None:
            del request.session['member_id']
    
        first_name = request.session.get("first_name")
        if first_name is not None:
            del request.session['first_name']
    
        last_nm = request.session.get("last_nm")
        if last_nm is not None:
            del request.session['last_nm']
    
        initial_nm = request.session.get("initial_nm")
        if initial_nm is not None:
            del request.session['initial_nm']
    
        authority = request.session.get("authority")
        if authority is not None:
            del request.session['authority']

        last_touch = request.session.get("last_touch")
        if last_touch is not None:
            del request.session['last_touch']



    #==============================================================================
    #  Get Time Info
    #==============================================================================
    def f_getDateTime(self):
        return timezone.now()


    #==============================================================================
    #  Get Date Info 
    #     = Y:year
    #     = M:month
    #     = D:day
    #==============================================================================
    def f_getDate(self, dType):
        
        # result
        date = ""
        
        if dType == "Y":
            date = timezone.now().year
        elif dType == "M":
            date = timezone.now().month
        elif dType == "D":
            date = timezone.now().day

        return date


    
    #==============================================================================
    #  Get Time Using Format
    #  format : https://docs.djangoproject.com/en/1.10/ref/templates/builtins/#date
    #    ex) Y-m-d H:i ==> 2016-01-12 23:20
    #        y-M-D h:i ==> 16-Jan-Fri 11:20
    #==============================================================================
    def f_getDateTimeFormat(self, strFormat):
        return dateformat.format(timezone.localtime(CommonUtil().f_getDateTime()), strFormat)



    #==============================================================================
    #  Get Data Type Folder Name
    #==============================================================================
    def f_getDataTypeFolderName(self, dataType):
        
        if dataType == "F":
            dataTypeFolder = "func"
        elif dataType == "I":
            dataTypeFolder = "infusion"
        elif dataType == "D":
            dataTypeFolder = "dwi"
        elif dataType == "M":
            dataTypeFolder = "fmap"
        elif dataType == "A":
            dataTypeFolder = "anat"
        else:
            raise Exception('Can not find data type.')

            
        return dataTypeFolder


    #==============================================================================
    #  Get Code_group id
    #==============================================================================
    def f_getDataTypeGroupId(self, dataType):
        
        if dataType == "F":
            codeGroupId = "005"
        elif dataType == "D":
            codeGroupId = "006"
        elif dataType == "M":
            codeGroupId = "007"
        elif dataType == "A":
            codeGroupId = "008"
        elif dataType == "I":
            codeGroupId = "009"
        else:
            raise Exception('Can not find data type.')
        
        return codeGroupId



    #==============================================================================
    #  Get Root Path
    #==============================================================================
    def f_getPath(self, dataType):
        
        curPath = os.getcwd()
        logger.debug("curPath=[" + curPath + "]")
        
        rootPath = ""
        
        if curPath == "E:\workspace" :
            rootPath = "E:\pjoFiles"
#             rootPath2 = "G:\Dan\DA_2015_SNr-GPe-DBS"
            rootPath2 = "Z:\Woomi\M1_ChR2"
        else :
            ### TODO for linux
            rootPath = ""
        
        # source_path
        if dataType == "S":
#             returnPath = os.path.join(rootPath, "sourcedata")
            returnPath = rootPath2
        # derive_path
        elif dataType == "D":
            returnPath = os.path.join(rootPath, "derivatives")
        # temp Path
        elif dataType == "T":
#             returnPath = os.path.join(rootPath, "temp")
            returnPath = rootPath2
        else:
            returnPath = rootPath
            
        logger.debug("returnPath=[" + returnPath + "]")
        
        return returnPath        
        






    #==============================================================================
    #  Get Derive Info : return Dictionary
    #       fileDict['projectName'] : ex) WB_2016_M_VO_001
    #       fileDict['subjectName'] : ex) sub-normal
    #       fileDict['sessionName'] : ex) ses-test01
    #==============================================================================
    def f_getFileDict(self, sessionId):
    
        # DAO
        pDao = ProjectDao()
        
        # Dictionary
        fileDict = {}

        # Session Object
        sessionObj = pDao.selectSessionObject(sessionId)
        projectId = sessionObj.project_id
        subjectNum = sessionObj.subject_num
        logger.debug("projectId == [" + projectId + "]")

        # Subject Object
        subjectObj = pDao.selectSubjectObjectWithNum(projectId, subjectNum)
                
        # Project Name
        projectName = pDao.getProjectName(projectId)
        fileDict['projectName'] = projectName

        # Subject Name
        subjectName = subjectObj.subject_nm
        fileDict['subjectName'] = "sub-" + subjectName
        logger.debug("subjectName == [" + subjectName + "]")

        # Session Name
        sessionName = sessionObj.session_nm
        fileDict['sessionName'] = "ses-" + sessionName
        logger.debug("sessionName == [" + sessionName + "]")
        
        return fileDict
    


    #==============================================================================
    #  Get Derive Folder Name : ex) E:\pjoFiles\derivatives\WB_2016_M_VO_001\sub-normal\ses-test01\func
    #==============================================================================
    def f_getFolderName(self, fileDict, dataType):

        derive_path = CommonUtil().f_getPath("D")
        dataTypeFolder = CommonUtil().f_getDataTypeFolderName(dataType)
        logger.debug("dataTypeFolder ====== [" + dataTypeFolder + "]")
 
        dPath = os.path.join(derive_path, fileDict['projectName'], fileDict['subjectName'], fileDict['sessionName'], dataTypeFolder)
        logger.debug("folderName ====== [" + dPath + "]")
        
        return dPath



    #==============================================================================
    #  Get Derive File Name : ex) sub-normal_ses-test01_task-function_acq-hi_rec-hello_run-01_bold
    #==============================================================================
    def f_getFileName(self, fileDict, scanObj):

        try:
            dataType = scanObj.meta_data_type
            logger.debug("dataType=[%s]", dataType)
            
            codeGroupId = CommonUtil().f_getDataTypeGroupId(dataType)
            logger.debug("codeGroupId=[%s]", codeGroupId)
            
            # Meta Info
            task = scanObj.meta_task
            acq = scanObj.meta_acq
            rec = scanObj.meta_rec
            run = scanObj.meta_run
            suffix = scanObj.meta_suffix
            
            metaName = ""
            if task is not None and task != "":
                metaName = metaName + "task-" + task + "_"
            if acq is not None and acq != "":
                metaName = metaName + "acq-" + acq + "_"
            if rec is not None and rec != "":
                metaName = metaName + "rec-" + rec + "_"
    
            logger.debug("metaName=[%s]", metaName)
            
            # Get Suffix
            cDao = CommonDao()
            suffixCodeObj = cDao.selectCodeObject(codeGroupId, suffix)
    
            metaName = metaName + "run-" + run + "_" + suffixCodeObj.code_nm
            fileName = fileDict['subjectName'] + "_" + fileDict['sessionName'] + "_" + metaName
            logger.debug("fileName=[%s]", fileName)
        except Exception, e:
            errLogger.error(e)
        
        return fileName
         



    #==============================================================================
    #  Move Folder from source to target
    #==============================================================================
    def f_moveFolder(self, fromPath, toPath, sourceName):
        
        try:
            if os.path.isdir(os.path.join(fromPath, sourceName)):
                shutil.move(os.path.join(fromPath, sourceName) , os.path.join(toPath, sourceName))
                return True
            else:
                errLogger.error("This is not directory. name=[" + sourceName +"]")
                return False
        except Exception, e:
            errLogger.error(e)
            return False



    #==============================================================================
    #  Round
    #==============================================================================
    def f_round(self, orgNum, digit):
        
        try:
            num = float(orgNum)
            num = round(num, digit)
        except Exception, e:
            errLogger.error(e)
            num = 0
            
        return num



