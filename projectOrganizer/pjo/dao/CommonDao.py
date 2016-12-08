import logging
from django.shortcuts import get_object_or_404
from django.db.models import Count
from pjo.models import Code
from pjo.models import Researcher

dbLogger = logging.getLogger("dba")
errLogger = logging.getLogger("errLog")



class CommonDao(object):

    #==============================================================================
    #  Select Common Code
    #==============================================================================
    def selectCodeList(self, groupId):
         
        codeList = Code.objects.filter(group_id=groupId).values().order_by('order_no')
        
        return codeList

    
    #==============================================================================
    #  Select Common Code for Json
    #==============================================================================
    def selectCodeListForJson(self, groupId):
         
        codeList = Code.objects.filter(group_id=groupId).only('code_id', 'code_nm').order_by('order_no')
        
        return codeList   


    #==============================================================================
    #  Select Common Code Value
    #==============================================================================
    def selectCodeObject(self, groupId, codeId):

        code = get_object_or_404(Code, group_id=groupId, code_id=codeId)
        
        return code




    '''
    ==============================================================================
      Researcher
    ==============================================================================
    '''
    #==============================================================================
    #  Select Researcher initial_nm
    #==============================================================================
    def selectResearcherInitialList(self):
        
        initialList = Researcher.objects.values('initial_nm').annotate(dcount=Count('initial_nm')).order_by('initial_nm')
        
        return initialList






