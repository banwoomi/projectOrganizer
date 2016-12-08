import logging

from django.db import connection
from django.shortcuts import get_object_or_404

from pjo.models import Researcher

dbLogger = logging.getLogger("dba")
errLogger = logging.getLogger("errLog")


class MemberDao(object):
    
    
    
    '''
    ==============================================================================
      Researcher
    ==============================================================================
    '''
    #==============================================================================
    #  Select Researcher Object
    #==============================================================================
    def selectResearcherObject(self, joinId):
         
        researcher = get_object_or_404(Researcher, pk=joinId)
        
        return researcher


    #==============================================================================
    #  Select Researcher 
    #==============================================================================
    def selectResearcherForCheck(self, flag, strValue):
        
        # Check Initial
        if(flag == 'Initial'):
            researcher = Researcher.objects.filter(initial_nm=strValue)
        
        # Check ID
        elif(flag == 'ID'):
            researcher = Researcher.objects.filter(id=strValue)
        
        # Other
        else:
            pass
    
        return researcher
        
        

    #==============================================================================
    #  Insert Researcher
    #==============================================================================
    def insertResearcher(self, dicResearcher):
         
        try:
            
            # Duplicate check
            researcher = Researcher.objects.filter(pk=dicResearcher['id'])
        
            if(researcher.count() == 0):
                model = Researcher (id         = dicResearcher['id']
                                  , first_nm   = dicResearcher['firstName']
                                  , last_nm    = dicResearcher['lastName']
                                  , initial_nm = dicResearcher['initial']
                                  , password   = dicResearcher['password']
                                  , reg_date   = dicResearcher['regDate'] )
                model.save()
                dbLogger.debug(connection.queries[-1])
                return True
            else:
                errLogger.error("Already Exists. ID=[" + dicResearcher['id'] + "]")
                return False
        
        except Exception, e:
            errLogger.error(e)
            return False



    #==============================================================================
    #  Update Researcher
    #==============================================================================
    def updateResearcher(self, dicResearcher):
         
        try:
            
            # UPDATE
            researcher = MemberDao.selectResearcherObject(self, dicResearcher['id'])
            researcher.first_nm = dicResearcher['firstName']
            researcher.last_nm = dicResearcher['lastName']
            researcher.password = dicResearcher['password']
            researcher.save()
            dbLogger.debug(connection.queries[-1])
            
            return True
        
        except Exception, e:
            errLogger.error(e)
            return False








