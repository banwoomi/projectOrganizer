import collections
import logging
from django.shortcuts import get_object_or_404
from django.db import connection
from django.db.models import Max

from pjo.models import ExperimentalDesign
from pjo.models import EDDetail
from pjo.models import EDKeyword

dbLogger = logging.getLogger("dba")
errLogger = logging.getLogger("errLog")


class EdDao(object):

    '''
    ==============================================================================
      EDKeyword
    ==============================================================================
    '''

    #==============================================================================
    #  Select Keyword
    #==============================================================================
    def selectKeyList(self):
         
        keyList = EDKeyword.objects.filter(use_yn="Y").values().order_by('keyword_id')
        
        return keyList

    
    #==============================================================================
    #  Select Keyword
    #==============================================================================
    def selectKeyListWithComma(self):

        # make query
        queryList = []
        
        queryList.append("SELECT GROUP_CONCAT(KEYWORD_NAME) AS KEYWORD \n")
        queryList.append("  FROM PJO_EDKEYWORD \n")
        queryList.append(" WHERE USE_YN = 'Y'  \n")
        queryList.append(" ORDER BY KEYWORD_ID \n")    

        # get data
        with connection.cursor() as c:
            try:
                c.execute(''.join(queryList))
                key = c.fetchone()
            except Exception, e:
                errLogger.error(e)
            finally:
                c.close()
                    
        return key
    

    '''
    ==============================================================================
      ExperimentalDesign
    ==============================================================================
    '''

    #==============================================================================
    #  Select EDDetail Object
    #==============================================================================
    def selectExperimentalDesignObject(self, edId):
         
        edObj = get_object_or_404(ExperimentalDesign, pk=edId)
        
        return edObj
    
    

    #==============================================================================
    #  Select ExperimentalDesign
    #==============================================================================
    def selectExperimentalDesignList(self, context):
        
        # Select keyword list
        keyList = EdDao().selectKeyList()
        
        # from text
        if 'from' in context:
            strFrom = context['from']
        else:
            strFrom = ''
            
                
        # parameter list
        paramList = []

        # make query
        queryList = []
        
        queryList.append("SELECT A.ED_ID, A.ED_TITLE, CONCAT(C.FIRST_NM, ' ', C.LAST_NM) AS RESEARCHER_NAME \n")

        for key in keyList:
            
            if strFrom == 'edList':
                queryList.append("     , IFNULL(MAX(IF(B.KEYWORD_ID = '" + key['keyword_id'] + "', B.ED_VALUE, NULL)),'') AS 'Z_" + key['keyword_id'] + "' \n")
            else:
                if(key['keyword_id'] <= "06"):
                    queryList.append("     , IFNULL(MAX(IF(B.KEYWORD_ID = '" + key['keyword_id'] + "', B.ED_VALUE, NULL)),'') AS 'Z_" + key['keyword_id'] + "' \n")
        
        queryList.append("  FROM PJO_EXPERIMENTALDESIGN A \n")
        queryList.append("   , PJO_EDDETAIL B             \n")
        queryList.append("   , PJO_RESEARCHER C    \n")
        queryList.append(" WHERE A.ED_ID = B.ED_ID \n")
        queryList.append("   AND A.REG_ID = C.ID   \n")

        if 'txtEdId' in context and context['txtEdId'] != "":
            queryList.append("   AND A.ED_ID = %s \n")
            paramList.append(context['txtEdId'])
        
        if 'txtEdTitle' in context and context['txtEdTitle'] != "":
            queryList.append("   AND A.ED_TITLE LIKE %s \n")
            paramList.append("%" + context['txtEdTitle'] + "%")

        if 'txtResearcherName' in context and context['txtResearcherName'] != "":
            queryList.append("   AND (C.FIRST_NM LIKE %s \n")
            queryList.append("    OR C.LAST_NM LIKE %s ) \n")
            paramList.append("%" + context['txtResearcherName'] + "%")
            paramList.append("%" + context['txtResearcherName'] + "%")
                    
        queryList.append(" GROUP BY A.ED_ID \n") 
        queryList.append(" ORDER BY A.ED_ID DESC \n") 
        
#         dbLogger.debug(''.join(queryList))
        
        # get data
        with connection.cursor() as c:
            try:
                c.execute(''.join(queryList), paramList)
                edList = EdDao().f_dictfetchall_sort(c)
            except Exception, e:
                errLogger.error(e)
            finally:
                c.close()
                    
        return edList
    
    
    
        
    #==============================================================================
    #  Insert ExperimentalDesign
    #==============================================================================
    def insertExperimentalDesign(self, dicEd):

        try:
            
            ### ed_id
            edId = ExperimentalDesign.objects.all().aggregate(Max("ed_id"))
            strEdId = edId['ed_id__max']
        
            if(strEdId is None):
                strEdId = "1"
                strEdId = strEdId.zfill(6)
            else:
                strEdId = str(int(strEdId) + 1)
                strEdId = strEdId.zfill(6)
        
            dicEd['edId'] = strEdId
            dbLogger.debug("strEdId====" + strEdId)
        

            ### INSERT
            ed = ExperimentalDesign (ed_id = strEdId
                             , ed_title = dicEd['edTitle']
                             , reg_id = dicEd['memberId']
                             , reg_date = dicEd['regDate'])
            ed.save()
        
            return True
        
        except Exception, e:
            errLogger.error(e)
            return False
    

    
    #==============================================================================
    #  Update ExperimentalDesign : ED_TITLE
    #==============================================================================
    def updateExperimentalDesignEdTitle(self, edId, edTitle):
    
        try:
            edObj = EdDao.selectExperimentalDesignObject(self, edId)
        
            edObj.ed_title = edTitle
            edObj.save()
            
            dbLogger.debug(connection.queries[-1])
            
            return True
        
        except Exception, e:
            errLogger.error(e)
            return False




    '''
    ==============================================================================
      EDDetail
    ==============================================================================
    '''
    #==============================================================================
    #  Select EDDetail Object
    #==============================================================================
    def selectEDDetailObject(self, detailId):
         
        edDetailObj = get_object_or_404(EDDetail, pk=detailId)
        
        return edDetailObj
    
    
    
    
    #==============================================================================
    #  select EDDetail list
    #==============================================================================
    def selectEDDetailList(self, edId):
           
        # parameter list
        paramList = []
        paramList.append(edId)
        
        # make query
        queryList = []
        queryList.append("SELECT A.ID, A.ED_VALUE, A.KEYWORD_ID  \n")
        queryList.append("     , B.KEYWORD_NAME, B.MAX_LENGTH, B.UNIT, B.DATA_TYPE, B.SC_YN, B.USE_YN \n")
        queryList.append("  FROM PJO_EDDetail A                 \n")
        queryList.append("     , PJO_EDKeyword B                \n")
        queryList.append(" WHERE A.KEYWORD_ID = B.KEYWORD_ID     \n")
        queryList.append("   AND A.ED_ID = %s                    \n")
        queryList.append(" ORDER BY A.KEYWORD_ID                 \n")


        # get data
        with connection.cursor() as c:
            try:
                c.execute(''.join(queryList), paramList)
                edDetailList = EdDao().f_dictfetchall(c)

#                 dbLogger.debug(''.join(queryList))
            finally:
                c.close()
                
        return edDetailList
    
    
    
    
    #==============================================================================
    #  select keyword_id list (return type List)
    #==============================================================================
    def selectEDDetailKeywordList(self, edId):
        
        keyList = EDDetail.objects.values_list('keyword_id', flat=True).filter(ed_id=edId).order_by('keyword_id')
        
        return keyList
        
    
       
    #==============================================================================
    #  Insert EDDetail [[[BULK]]]
    #==============================================================================
    def insertEDDetail_Bulk(self, dicEd):

        try:
        
            # keyword List
            selectedKeyList = dicEd['selectedKeyList']
            
            # detail_num
            detailNum = EDDetail.objects.filter(ed_id=dicEd['edId']).aggregate(Max("detail_num"))
            strDetailNum = detailNum['detail_num__max']
            intDetailNum = 0
            
            if(strDetailNum is None):
                intDetailNum = 1
            else:
                intDetailNum = int(strDetailNum) + 1
        
            dbLogger.debug("intDetailNum====%d", intDetailNum)
            
    
            objs = [
                EDDetail(
                    ed_id=dicEd['edId'],
                    detail_num=str(intDetailNum+i).zfill(2),
                    keyword_id=selectedKeyList[i],
                    reg_id=dicEd['memberId'],
                    reg_date=dicEd['regDate'],
                ) 
                for i in range(len(selectedKeyList))
            ]
    
                     
            EDDetail.objects.bulk_create(objs)
            
            return True
        
        except Exception, e:
            errLogger.error(e)
            return False
    


    #==============================================================================
    #  Update ed_value
    #==============================================================================
    def updateEDDetailEdValue(self, detailId, edValue):

        try:
            
            edDetailObj = EdDao.selectEDDetailObject(self, detailId)

            # TODO if table pjo_scan use this data, you can't update.
            regCnt = 0 # ProjectDao.selectDeriveCount(self, subject.project_id, subject.subject_num, "")

            if regCnt > 0:  
                ## err msg setting 
                return False
            
            else:
                
                edDetailObj.ed_value = edValue
                edDetailObj.save()
                dbLogger.debug(connection.queries[-1])
            
                return True
        
        except Exception, e:
            errLogger.error(e)
            return False
        






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
    #  Make list to dictionary (Sorted)
    #==============================================================================
    def f_dictfetchall_sort(self, cursor):
        columns = [col[0] for col in cursor.description]
        
        return [
            collections.OrderedDict(sorted(dict(zip(columns, row)).items()))
            for row in cursor.fetchall()
        ]
        
        