import logging

import datetime
from django.db import connection
from django.db.models import Max, Count
from django.shortcuts import get_object_or_404
from django.utils import timezone

from pjo.models import Source
from pjo.models import Scan
from pjo.util.PjoUtil import CommonUtil
from pjo.util.CustomException import CustomException

dbLogger = logging.getLogger("dba")
errLogger = logging.getLogger("errLog")


class SourceDao(object):
    
    '''
    ==============================================================================
      SOURCE
    ==============================================================================
    '''

    #==============================================================================
    #  Select Source Object
    #==============================================================================
    def selectSourceObject(self, sourceId):
        
        source = get_object_or_404(Source, pk=sourceId)
        
        return source


    #==============================================================================
    #  Select Source List
    #==============================================================================
    def selectSourceList(self, dicSource):

        # SQL
        sourceQuery = Source.objects
        
        keyList = list(dicSource.keys())
        for key in keyList:
            if key == "source_id" :
                if dicSource["source_id"] != "":
                    sourceQuery = sourceQuery.filter(source_id=dicSource["source_id"])
            elif key == "title" :
                if dicSource["title"] != "":
                    sourceQuery = sourceQuery.filter(title__icontains=dicSource["title"])
            elif key == "scan_yn" :
                if dicSource["scan_yn"] != "":
                    sourceQuery = sourceQuery.filter(scan_yn=dicSource["scan_yn"])
            elif key == "mapping_yn" :
                if dicSource["mapping_yn"] != "":
                    sourceQuery = sourceQuery.filter(mapping_yn=dicSource["mapping_yn"])

        # Result
        sourceList = sourceQuery.values()
        
        return sourceList
    


    #==============================================================================
    #  Select Source List with inquiry condition
    #==============================================================================
    def selectSourceListForSourceForm(self, dicSource):
    
        # values
        strTitle = dicSource['title']
        strRegStart = dicSource['regStart']
        strRegEnd = dicSource['regEnd']
        strScanStart = dicSource['scanStart']
        strScanEnd = dicSource['scanEnd']
        strScanYn = dicSource['scanYn']
        
        #### SQL
        sourceQuery = Source.objects
    
        # Title
        if strTitle != "" :
            sourceQuery = sourceQuery.filter(title__icontains=strTitle)
    
        # Registration Date
        if(len(strRegStart) == 10):
    
            dateRegStart = datetime.datetime.strptime(strRegStart, '%m/%d/%Y')
            dateRegStart = timezone.make_aware(dateRegStart, timezone.get_current_timezone())
    
            if(len(strRegEnd) == 10):
                dateRegEnd = datetime.datetime.strptime(strRegEnd, '%m/%d/%Y')
                dateRegEnd = timezone.make_aware(dateRegEnd, timezone.get_current_timezone())
    
                sourceQuery = sourceQuery.filter(reg_date__range=[dateRegStart, dateRegEnd])
    
            else:
                pass
        else:
            pass
    
    
        # Scan Date
        if(len(strScanStart) == 10):
    
            dateScanStart = datetime.datetime.strptime(strScanStart, '%m/%d/%Y')
            dateScanStart = timezone.make_aware(dateScanStart, timezone.get_current_timezone())
    
            if(len(strScanEnd) == 10):
                dateScanEnd = datetime.datetime.strptime(strScanEnd, '%m/%d/%Y')
                dateScanEnd = timezone.make_aware(dateScanEnd, timezone.get_current_timezone())
    
                sourceQuery = sourceQuery.filter(scan_date__range=[dateScanStart, dateScanEnd])
    
            else:
                pass
        else:
            pass
    
        # Scan Yes/No
        if strScanYn != "":
            sourceQuery = sourceQuery.filter(scan_yn=strScanYn)
    
        ##### Result
        sourceList = sourceQuery.values()
        dbLogger.debug(sourceList.query)        
        
        return sourceList
        




    #==============================================================================
    #  Insert Scan Info
    #==============================================================================
    def insertSourceInfo(self, dicSource):
        
        try:            

            ### source_id
            sourceId = Source.objects.all().aggregate(Max("source_id"))
            strSourceId = sourceId['source_id__max']
        
            if(strSourceId is None):
                strSourceId = "1"
                strSourceId = strSourceId.zfill(8)
            else:
                strSourceId = str(int(strSourceId) + 1)
                strSourceId = strSourceId.zfill(8)
        
            dbLogger.debug("strSourceId====" + strSourceId)

            source = Source(source_id=strSourceId
                            , title=dicSource['title']
                            , reg_id=dicSource['memberId']
                            , reg_date=dicSource['regDate'])
            source.save()
            
            dbLogger.debug(connection.queries[-1])
            
        except Exception, e:
            errLogger.error(e)






    #==============================================================================
    #  Update Source SCAN_YN
    #==============================================================================
    def updateSourceScanYn(self, sourceId):

        # util
        commonUtil = CommonUtil()
    
        source = SourceDao.selectSourceObject(self, sourceId)
        
        # Update Source. scan_yn
        source.scan_yn = "Y"
        source.scan_date = commonUtil.f_getDateTime()
        source.save()
        dbLogger.debug(connection.queries[-1])
     
    
    #==============================================================================
    #  UPdate Source MAPPING_YN
    #==============================================================================
    def updateSourceForMapping(self, sourceId, mappingYn):
         
        source = SourceDao.selectSourceObject(self, sourceId)

        # Update Source. mapping_yn
        source.mapping_yn = mappingYn
        source.save()
        dbLogger.debug(connection.queries[-1])



    '''
    ==============================================================================
      SCAN
    ==============================================================================
    '''

    #==============================================================================
    #  Select Source Object
    #==============================================================================
    def selectScanObject(self, scanId):
        
        scan = get_object_or_404(Scan, pk=scanId)
        
        return scan
    
    
    
    #==============================================================================
    #  Select Source Object
    #==============================================================================
    def selectScanObjectForJson(self, scanId):
        
        scan = Scan.objects.filter(pk=scanId)
        
        return scan
    
    
    
    #==============================================================================
    #  Select Scan List
    #==============================================================================
    def selectScanList(self, sourceId):
        
        scanList = Scan.objects.filter(source_id=sourceId).values().order_by('id')
        
        return scanList



    #==============================================================================
    #  Select Run Index
    #==============================================================================
    def selectRunIndex(self, dicScan):
         
        strDataType = dicScan['strDataType']
        metaRunQuery = Scan.objects.filter(source_id=dicScan['sourceId'])
        metaRunQuery = metaRunQuery.filter(meta_data_type=strDataType)
                                      
        if 'strAcq' in dicScan:
            strAcq = dicScan['strAcq']
            metaRunQuery = metaRunQuery.filter(meta_acq=strAcq)

        if 'strRec' in dicScan:
            strRec = dicScan['strRec']
            metaRunQuery = metaRunQuery.filter(meta_rec=strRec)

        if 'strTask' in dicScan:
            strTask = dicScan['strTask']
            metaRunQuery = metaRunQuery.filter(meta_task=strTask)
     

        metaRun = metaRunQuery.aggregate(Max("meta_run"))
        strMetaRun = metaRun['meta_run__max']
     
    
        if(strMetaRun is None or strMetaRun == ""):
            strMetaRun = "1"
            strMetaRun = strMetaRun.zfill(2)
        else:
            strMetaRun = str(int(strMetaRun) + 1)
            strMetaRun = strMetaRun.zfill(2)
         
        return strMetaRun



    #==============================================================================
    #  Insert Scan Info
    #==============================================================================
    def insertScanInfo(self, sourceId, dicScan, memberId):
        
        try:            
            scan = Scan(source_id=sourceId
                        , scan_num=dicScan["scan"]
                        , pid_arr=dicScan["pid_arr"]
                        , sch_slices=dicScan["n_slices"]
                        , sch_proto_nm=dicScan["protocol_name"]
                        , sch_echo_time=dicScan["te"]
                        , sch_repet_time=dicScan["tr"]
                        , sch_matrix=dicScan["matrix"]
                        , sch_spat=dicScan["dim"]
                        , sch_n_repet=dicScan["frame"]
                        , reg_id=memberId)
            scan.save()
            
            dbLogger.debug(connection.queries[-1])
            
        except Exception, e:
            errLogger.error(e)
            ## TODO : roll back





    #==============================================================================
    #  Update Scan Info for Meta
    #==============================================================================
    def updateScanInfoForMeta(self, dicScan, scanObj):
        
        try:            
            
            scanObj.meta_yn = "Y"
            scanObj.pid = dicScan["strPid"]
            scanObj.meta_data_type = dicScan["strDataType"]
            scanObj.meta_suffix = dicScan["strSuffix"]
                
            if("strTask" in dicScan):
                scanObj.meta_task = dicScan["strTask"]
            else:
                scanObj.meta_task = ""

            if("strAcq" in dicScan):
                scanObj.meta_acq = dicScan["strAcq"]
            else: 
                scanObj.meta_acq = ""
                
            if("strRec" in dicScan):
                scanObj.meta_rec = dicScan["strRec"]
            else:
                scanObj.meta_rec = ""

            if("strRun" in dicScan):
                scanObj.meta_run = dicScan["strRun"]
            else:
                scanObj.meta_run = ""

            scanObj.save()
            
            dbLogger.debug(connection.queries[-1])
            
            return True
            
        except Exception, e:
            CustomException().exceptionHandler(e)
            errLogger.error(e)
            return False
            ## TODO : roll back



    #==============================================================================
    #  Update Scan DERIVE_YN
    #==============================================================================
    def updateScanDeriveYn(self, scanId):

        scan = SourceDao.selectScanObject(self, scanId)

        # Update Scan. derive_yn
        scan.derive_yn = "Y"
        scan.save()
        dbLogger.debug(connection.queries[-1])




    #==============================================================================
    #  Select Scan linked with ED
    #==============================================================================
    def selectScanEDCount(self, edId):

        strEdId = "ED" + edId
        dbLogger.debug("strEdId ==[" + strEdId + "]")
        
        # SQL
        scanCnt = Scan.objects.filter(meta_acq=strEdId).aggregate(Count("id"))
        strScanCnt = scanCnt['id__count']
        
        return strScanCnt
    
    
    
    
    