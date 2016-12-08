import logging

from django.db import connection
from django.db.models import Max
from django.shortcuts import get_object_or_404

from pjo.models import Project
from pjo.models import Subject
from pjo.models import Session

dbLogger = logging.getLogger("dba")
errLogger = logging.getLogger("errLog")


class ProjectDao(object):
    
    
    
    '''
    ==============================================================================
      Project
    ==============================================================================
    '''
    #==============================================================================
    #  Select Project Object
    #==============================================================================
    def selectProjectObject(self, projectId):
         
        project = get_object_or_404(Project, pk=projectId)
        
        return project


    #==============================================================================
    #  Select Project List with inquiry condition
    #==============================================================================
    def selectProjectList(self, context):

        # parameter list        
        paramList = []

        # make query
        queryList = []

        queryList.append("SELECT A.PROJECT_ID \n")
        queryList.append("     , A.INITIAL_NM, B.NAME \n")
        queryList.append("     , A.YEAR \n")
        queryList.append("     , A.ANIMAL_TYPE, (SELECT CODE_NM FROM PJO_CODE WHERE GROUP_ID_ID = '002' AND CODE_ID = A.ANIMAL_TYPE) AS ANIMAL_NM \n")
        queryList.append("     , A.METHOD_TYPE, (SELECT CODE_NM FROM PJO_CODE WHERE GROUP_ID_ID = '003' AND CODE_ID = A.METHOD_TYPE) AS METHOD_NM \n")
        queryList.append("     , A.SERIAL_NO, A.PROJECT_AIM, A.REG_DATE \n")
        queryList.append("     , (SELECT COUNT(*) FROM PJO_SUBJECT WHERE PROJECT_ID = A.PROJECT_ID) AS SUB_CNT \n")
        queryList.append("     , (SELECT COUNT(*) FROM PJO_SESSION WHERE PROJECT_ID = A.PROJECT_ID) AS SES_CNT \n")
        queryList.append("     , (SELECT COUNT(*) FROM PJO_SESSION WHERE PROJECT_ID = A.PROJECT_ID AND SOURCE_ID IS NOT NULL) AS MAP_CNT \n")
        queryList.append("     , IFNULL(DER.CNT, 0) AS DERIVE_CNT \n")
        queryList.append("  FROM PJO_PROJECT A \n")
        queryList.append("       LEFT OUTER JOIN (SELECT SES.PROJECT_ID, COUNT(SCAN.SOURCE_ID) AS CNT \n")
        queryList.append("                          FROM PJO_SESSION SES, PJO_SCAN SCAN  \n")
        queryList.append("                         WHERE SES.SOURCE_ID = SCAN.SOURCE_ID \n")
        queryList.append("                           AND SCAN.DERIVE_YN = 'Y'  \n")
        queryList.append("                         GROUP BY SES.PROJECT_ID) AS DER \n")
        queryList.append("       ON A.PROJECT_ID = DER.PROJECT_ID  \n")
        queryList.append("     , (SELECT INITIAL_NM, CONCAT(FIRST_NM, ' ', LAST_NM) AS NAME \n")
        queryList.append("          FROM PJO_RESEARCHER ) B \n")
        queryList.append(" WHERE A.INITIAL_NM = B.INITIAL_NM \n")
        queryList.append("   AND A.USE_YN = 'Y' \n")
    
        
        if 'selInitial' in context and context['selInitial'] != "":
            queryList.append("   AND A.INITIAL_NM = %s \n")
            paramList.append(context['selInitial'])
        if 'txtYear' in context and context['txtYear'] != "":
            queryList.append("   AND A.YEAR = %s \n")
            paramList.append(context['txtYear'])
        if 'selAnimalType' in context and context['selAnimalType'] != "":
            queryList.append("   AND A.ANIMAL_TYPE = %s \n")
            paramList.append(context['selAnimalType'])
        if 'selMethodType' in context and context['selMethodType'] != "":
            queryList.append("   AND A.METHOD_TYPE = %s \n")
            paramList.append(context['selMethodType'])
        if 'txtProjectAim' in context and context['txtProjectAim'] != "":
            queryList.append("   AND A.PROJECT_AIM LIKE %s \n")
            paramList.append("%" + context['txtProjectAim'] + "%")
        
        queryList.append(" ORDER BY A.PROJECT_ID DESC \n")
        
#         dbLogger.debug(queryList)
    
        # get data
        with connection.cursor() as c:
            try:
                c.execute(''.join(queryList), paramList)
                resultLIst = ProjectDao().f_dictfetchall(c)
            finally:
                c.close()
        return resultLIst
    
    
    
    #==============================================================================
    #  Make list to dictionary
    #==============================================================================
    def f_dictfetchall(self, cursor):
        columns = [col[0] for col in cursor.description]
        return [
            dict(zip(columns, row))
            for row in cursor.fetchall()
        ]
        
        

    #==============================================================================
    #  Get Project Name
    #==============================================================================
    def getProjectName(self, projectId):

        project = ProjectDao.selectProjectObject(self, projectId)
    
        projectName = project.initial_nm + "_" + project.year + "_" + project.animal_type + "_" + project.method_type + "_" + project.serial_no
        
        return projectName
    

    
    #==============================================================================
    #  Insert Project
    #==============================================================================
    def insertProjectInfo(self, dicProject):
    
        try:
            ### project_id
            projectId = Project.objects.all().aggregate(Max("project_id"))
            strProjectId = projectId['project_id__max']
        
            if(strProjectId is None):
                strProjectId = "1"
                strProjectId = strProjectId.zfill(5)
            else:
                strProjectId = str(int(strProjectId) + 1)
                strProjectId = strProjectId.zfill(5)
        
            dbLogger.debug("strProjectId====" + strProjectId)
        
        
            ### serial_no
            serialNo = Project.objects.filter(initial_nm=dicProject['initialName']
                                             , year=dicProject['year']
                                             , animal_type=dicProject['animalType']
                                             , method_type=dicProject['methodType']
                                    ).aggregate(Max("serial_no"))
            strSerialNo = serialNo['serial_no__max']
        
            if(strSerialNo is None):
                strSerialNo = "1"
                strSerialNo = strSerialNo.zfill(3)
            else:
                strSerialNo = str(int(strSerialNo) + 1)
                strSerialNo = strSerialNo.zfill(3)
        
            dbLogger.debug("strSerialNo====" + strSerialNo)
        
        
            ### INSERT
            project = Project (project_id = strProjectId
                             , initial_nm = dicProject['initialName']
                             , year = dicProject['year']
                             , animal_type = dicProject['animalType']
                             , method_type = dicProject['methodType']
                             , serial_no = strSerialNo
                             , project_aim = dicProject['projectAim']
                             , reg_id = dicProject['memberId']
                             , reg_date = dicProject['regDate'])
            project.save()
        
            return True
        
        except Exception, e:
            errLogger.error(e)
            return False
    


    #==============================================================================
    #  Update Project : project_aim
    #==============================================================================
    def updateProjectProjectAim(self, project, strProjectAim):
     
        try:
            project.project_aim = strProjectAim
            project.save()
                
            dbLogger.debug(connection.queries[-1])
            
            return True
        
        except Exception, e:
            errLogger.error(e)
            return False   
    
    
    
    
    
    '''
    ==============================================================================
      Subject
    ==============================================================================
    '''
    #==============================================================================
    #  Select Subject Object
    #==============================================================================
    def selectSubjectObject(self, subjectId):
         
        subject = get_object_or_404(Subject, pk=subjectId)
        
        return subject
        

    #==============================================================================
    #  Select Subject Object
    #==============================================================================
    def selectSubjectObjectWithNum(self, projectId, subjectNum):
         
        subject = get_object_or_404(Subject, project_id=projectId, subject_num=subjectNum)
        
        return subject
    
       
    #==============================================================================
    #  Select Subject List
    #==============================================================================
    def selectSubjectList(self, projectId):
        
#         subjectList = Subject.objects.filter(project_id=projectId, use_yn="Y").values()

        # parameter list
        paramList = []
        paramList.append(projectId)
        paramList.append(projectId)
        
        # make query
        queryList = []
        queryList.append("SELECT A.id, A.subject_num, A.subject_nm, A.subject_cmt, A.use_yn \n")
        queryList.append("     , (SELECT COUNT(SUBJECT_NUM)                      \n")
        queryList.append("          FROM PJO_SESSION                               \n")
        queryList.append("         WHERE PROJECT_ID = A.PROJECT_ID                 \n")
        queryList.append("            AND SUBJECT_NUM = A.SUBJECT_NUM ) AS ses_cnt   \n")
        queryList.append("     , IFNULL(DER.CNT, 0) AS derive_cnt \n")
        queryList.append("FROM PJO_SUBJECT A                                     \n")
        queryList.append("     LEFT OUTER JOIN (SELECT SES.ID, COUNT(SCAN.SOURCE_ID) AS CNT \n")
        queryList.append("                        FROM PJO_SESSION SES, PJO_SCAN SCAN \n")
        queryList.append("                       WHERE SES.SOURCE_ID = SCAN.SOURCE_ID \n")
        queryList.append("                         AND SCAN.DERIVE_YN = 'Y' \n")
        queryList.append("                         AND SES.PROJECT_ID = %s \n")
        queryList.append("                       GROUP BY SES.ID) AS DER \n")
        queryList.append("     ON A.ID = DER.ID \n")
        queryList.append(" WHERE A.PROJECT_ID = %s  \n")
        queryList.append("   AND A.USE_YN = 'Y' \n")


        # get data
        with connection.cursor() as c:
            try:
                c.execute(''.join(queryList), paramList)
                subjectList = ProjectDao().f_dictfetchall(c)

#                 dbLogger.debug(''.join(queryList))
            finally:
                c.close()
                
        return subjectList
    
    
    

    #==============================================================================
    #  Select Subject List
    #==============================================================================
    def selectSubjectListForSessionCopy(self, projectId, subjectId):
        
        subjectList = Subject.objects.filter(project_id=projectId, use_yn="Y").exclude(id=subjectId).values().order_by('id')
        
        return subjectList
    
    

    #==============================================================================
    #  Insert Subject
    #==============================================================================
    def insertSubjectInfo(self, dicSubject):
    
        try:
            
            ### get subject_num
            subjectNum = Subject.objects.filter(project_id=dicSubject['projectId']).aggregate(Max("subject_num"))
    
            strSubjectNum = subjectNum['subject_num__max']
    
            if(strSubjectNum is None):
                strSubjectNum = "1"
                strSubjectNum = strSubjectNum.zfill(2)
            else:
                strSubjectNum = str(int(strSubjectNum) + 1)
                strSubjectNum = strSubjectNum.zfill(2)
    
            dbLogger.debug("strSubjectNum====" + strSubjectNum)
    
    
            ### INSERT
            subject = Subject (project_id = dicSubject['projectId']
                             , subject_num = strSubjectNum
                             , subject_nm = dicSubject['subjectName']
                             , subject_cmt = dicSubject['subjectComment']
                             , reg_id = dicSubject['memberId'] )
            subject.save()
            dbLogger.debug(connection.queries[-1])
        
            return True
        
        except Exception, e:
            errLogger.error(e)
            return False
    


    #==============================================================================
    #  Update Subject : subject_nm
    #==============================================================================
    def updateSubjectSubjectName(self, dicSubject):
        
        try:
            
            subject = ProjectDao.selectSubjectObject(self, dicSubject['subjectId'])


            # Derivative File Check
            deriveCnt = ProjectDao.selectDeriveCount(self, subject.project_id, subject.subject_num, "")

            if deriveCnt > 0 and subject.subject_nm != dicSubject['subjectName']:   
                dicSubject["error"] = "You can't modify subject's name, if it's already derived."
                return False
            
            else:
                
                subject.subject_nm = dicSubject['subjectName']
                subject.subject_cmt = dicSubject['subjectComment']
                subject.save()
                dbLogger.debug(connection.queries[-1])
            
                return True
        
        except Exception, e:
            errLogger.error(e)
            return False
        


    '''
    ==============================================================================
      Session
    ==============================================================================
    '''

    #==============================================================================
    #  Select Session Object
    #==============================================================================
    def selectSessionObject(self, sessionId):
         
        session = get_object_or_404(Session, pk=sessionId)
        
        return session
    
    
    
    #==============================================================================
    #  Select Session List With SubjectNum
    #==============================================================================
    def selectSessionList(self, projectId, subjectNum):
        
#         sessionList = Session.objects.filter(project_id=projectId, subject_num=subjectNum, use_yn="Y").values().order_by('id')

        # parameter list
        paramList = []
        paramList.append(projectId)
        paramList.append(subjectNum)
        paramList.append(projectId)
        paramList.append(subjectNum)
        
        # make query
        queryList = []
        queryList.append("SELECT A.id, A.session_num, A.session_nm, A.session_cmt, A.use_yn, A.source_id, IFNULL(DER.cnt, 0) AS derive_cnt \n")
        queryList.append("  FROM PJO_SESSION A                                                                    \n")
        queryList.append("       LEFT OUTER JOIN (SELECT SES.ID, COUNT(SCAN.SOURCE_ID) AS CNT                     \n")
        queryList.append("                          FROM PJO_SESSION SES, PJO_SCAN SCAN                           \n")
        queryList.append("                         WHERE SES.SOURCE_ID   = SCAN.SOURCE_ID                         \n")
        queryList.append("                           AND SCAN.DERIVE_YN  = 'Y'                                    \n")
        queryList.append("                           AND SES.PROJECT_ID  = %s                                     \n")
        queryList.append("                           AND SES.SUBJECT_NUM = %s                                     \n")
        queryList.append("                         GROUP BY SES.ID) DER                                           \n")
        queryList.append("       ON A.ID = DER.ID                                                                 \n")
        queryList.append(" WHERE A.PROJECT_ID  = %s                                                               \n")
        queryList.append("   AND A.SUBJECT_NUM = %s                                                               \n")
        queryList.append("   AND A.USE_YN      = 'Y'                                                              \n")
        queryList.append(" ORDER BY A.ID                                                                          \n")


        # get data
        with connection.cursor() as c:
            try:
                c.execute(''.join(queryList), paramList)
                sessionList = ProjectDao().f_dictfetchall(c)

                dbLogger.debug(''.join(queryList))
            finally:
                c.close()
                
        return sessionList



    #==============================================================================
    #  Insert Session
    #==============================================================================
    def insertSessionInfo(self, dicSession):
    
        try:
            
            ### get session_num
            sessionNum = Session.objects.filter(project_id=dicSession['projectId'], subject_num=dicSession['subjectNum']).aggregate(Max("session_num"))
            strSessionNum = sessionNum['session_num__max']
    
            if(strSessionNum is None):
                strSessionNum = "1"
                strSessionNum = strSessionNum.zfill(2)
            else:
                strSessionNum = str(int(strSessionNum) + 1)
                strSessionNum = strSessionNum.zfill(2)
    
            dbLogger.debug("strSessionNum=[" + strSessionNum+ "]")
            
            ### INSERT
            session = Session (project_id = dicSession['projectId']
                             , subject_num = dicSession['subjectNum']
                             , session_num = strSessionNum
                             , session_nm = dicSession['sessionName']
                             , session_cmt = dicSession['sessionComment']
                             , reg_id = dicSession['memberId'] )
            session.save()
            dbLogger.debug(connection.queries[-1])
        
            return True
        
        except Exception, e:
            errLogger.error(e)
            return False
    



    #==============================================================================
    #  Update Session : session_nm
    #==============================================================================
    def updateSessionSessionName(self, dicSession):
        
        try:
            
            # Get Session Object
            session = ProjectDao.selectSessionObject(self, dicSession['sessionId'])
            
            # Derivative File Check
            deriveCnt = ProjectDao.selectDeriveCount(self, session.project_id, session.subject_num, session.id)
            
            if deriveCnt > 0 and session.session_nm != dicSession['sessionName']:   
                dicSession["error"] = "You can't modify session's name, if it's already derived."
                return False
            
            else:            
                session.session_nm = dicSession['sessionName']
                session.session_cmt = dicSession['sessionComment']
                session.save()
                dbLogger.debug(connection.queries[-1])
                
                return True
        
        except Exception, e:
            errLogger.error(e)
            return False
        


     
    #==============================================================================
    #  UPdate Session Object
    #==============================================================================
    def updateSessionForMapping(self, sessionId, sourceId):
         
        session = ProjectDao.selectSessionObject(self, sessionId)

        # Update Session. source_id
        session.source_id = sourceId
        session.save()
        dbLogger.debug(connection.queries[-1])




    '''
    ==============================================================================
      Join
    ==============================================================================
    '''
    def selectDeriveCount(self, projectId, subjectNum, sessionId):

        # parameter list
        paramList = []
        paramList.append(projectId)

        if subjectNum != "":
            paramList.append(subjectNum)
        if sessionId != "":
            paramList.append(sessionId)
        
        # make query
        queryList = []             
        queryList.append("SELECT COUNT(SCAN.ID)                  \n")
        queryList.append("  FROM PJO_SESSION SES, PJO_SCAN SCAN  \n")
        queryList.append(" WHERE SES.SOURCE_ID = SCAN.SOURCE_ID  \n")
        queryList.append("   AND SCAN.DERIVE_YN = 'Y'            \n")
        queryList.append("   AND SES.PROJECT_ID = %s             \n")
        if subjectNum != "":
            queryList.append("   AND SES.SUBJECT_NUM = %s            \n")
        if sessionId != "":
            queryList.append("   AND SES.ID = %s                     \n")
    
        # get data
        with connection.cursor() as c:
            try :
                c.execute(''.join(queryList), paramList)
                deriveTuple = c.fetchone()
    
                dbLogger.debug(''.join(queryList))
            finally:
                c.close()

        if deriveTuple is not None and len(deriveTuple) >= 0:
            deriveCnt = deriveTuple[0]
        else:
            deriveCnt = 0
        
        return deriveCnt
        
    
    
