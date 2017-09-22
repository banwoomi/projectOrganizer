from __builtin__ import Exception

import json
import logging
import os
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse
from django.core import serializers
from django.http import HttpResponse
from django.http.response import HttpResponseRedirect
from django.shortcuts import render

from pjo.dao.SourceDao import SourceDao
from pjo.dao.ProjectDao import ProjectDao
from pjo.dao.CommonDao import CommonDao
from pjo.dao.MemberDao import MemberDao
from pjo.dao.EdDao import EdDao 
from pjo.form import SourceForm
from pjo.module.CheckScan import CheckScan
from pjo.module.Brk2nii import Brk2nii
from pjo.util.PjoUtil import CommonUtil


logger = logging.getLogger("devLog")
dbLogger = logging.getLogger("dba")
errLogger = logging.getLogger("errLog")




#==============================================================================
#  index page
#==============================================================================
def pjoInit(request):

    template_name = 'pjo_main.html'

    context = {
        'title' : 'Main',
    }

    return render(request, template_name, context)




'''
##########################################################################################################
#  JOIN PJO MEMBER
##########################################################################################################
'''

#==============================================================================
#  Join Form page
#==============================================================================
def joinInit(request):

    template_name = 'member/joinMember.html'

    context = {
        'title' : 'Join Project Organizer Members',
    }
    
    return render(request, template_name, context)




#==============================================================================
#  register Pjo member : [INSERT RESEARCHER]
#==============================================================================
def joinMember(request):

    template_name = 'pjo_main.html'
    context = {
        'title' : 'Main',
    }

    # values
    joinId = request.POST['txtId']
    logger.debug("joinID [" + joinId + "]")

    # Dao
    mDao = MemberDao()

    # Set Dictionary
    dicResearcher = {}

    dicResearcher['id'] = request.POST['txtId']
    dicResearcher['firstName'] = request.POST['txtFirstName']
    dicResearcher['lastName'] = request.POST['txtLastName']
    dicResearcher['initial'] = request.POST['txtInitial']
    dicResearcher['password'] = request.POST['txtPassword']
    dicResearcher['regDate'] = CommonUtil().f_getDateTime()

    # Insert
    result = mDao.insertResearcher(dicResearcher)

    if result:
        context['errMsg'] = "Join Success!! Please Sign in!!"
    else:
        context['errMsg'] = "[joinMember] Already exist."

    return render(request, template_name, context)




#==============================================================================
#  check duplication before join
#==============================================================================
def joinCheck(request):

    # Dao
    mDao = MemberDao()
    
    if 'flag' in request.POST:
        flag = request.POST['flag']
        logger.debug("flag : [" + flag + "]")

        # Check Initial
        if(flag == 'Initial'):
            strValue = request.POST['initial']
            logger.debug("initial : [" + strValue + "]")

        # Check ID
        elif(flag == 'ID'):
            strValue = request.POST['userId']
            logger.debug("ID=" + strValue)

        else:
            return HttpResponse("Wrong flag")


        researcher = mDao.selectResearcherForCheck(flag, strValue)
        rCount = researcher.count()

        json_str = json.dumps(rCount)
        return HttpResponse (json_str, content_type='application/json')
    
    else:
        return HttpResponse("No flag")




'''
##########################################################################################################
#  SIGN IN/OUT
##########################################################################################################
'''

#==============================================================================
#  Sign in Form page
#==============================================================================
def signInit(request):

    template_name = 'member/signIn.html'

    context = {
        'title' : 'Sign In Project Organizer',
    }
    return render(request, template_name, context)



#==============================================================================
#  Sign in
#==============================================================================
def signinPjo(request):

    template_name = 'pjo_main.html'
    context = {
        'title' : 'Main',
    }

    # values
    strId = request.POST['txtId']
    strPassword = request.POST['txtPassword']
    logger.debug("ID : [" + strId + "]")

    errMsg = ""

    # Dao
    mDao = MemberDao()
    
    # check ID
    researcher = mDao.selectResearcherForCheck("ID", strId) 

    if(researcher.count() == 0):
        errMsg = "[signinPjo] Incorrect ID. Please try again."
    else:

        # check ID & Password
        if(researcher[0].password == strPassword):
            obj_researcher = researcher[0]
        else:
            errMsg = "[signinPjo] Incorrect Password. Please try again."


    if errMsg == "":
        # session setting
        CommonUtil().setSession(request, obj_researcher)

    else:
        # delete session
        CommonUtil().delSession(request)

        logger.debug("errMsg: [" + errMsg + "]")
        context['errMsg'] = errMsg

    return render(request, template_name, context)




#==============================================================================
#  Sign out
#==============================================================================
def signoutPjo(request):

    template_name = 'pjo_main.html'
    context = {
        'title' : 'Main',
    }

    # session delete
    CommonUtil().delSession(request)

    return render(request, template_name, context)





'''
##########################################################################################################
#  PROFILE
##########################################################################################################
'''

#==============================================================================
#  Profile Form
#==============================================================================
def profileInit(request):

    template_name = 'member/profile.html'
    context = {
        'title' : 'My Profile',
    }

    # values
    signId = request.session['member_id']
    logger.debug("signId [" + signId + "]")

    # Dao
    mDao = MemberDao()
    researcher = mDao.selectResearcherObject(signId)
        
    # setting context
    context['id'] = researcher.id
    context['firstName'] = researcher.first_nm
    context['lastName'] = researcher.last_nm
    context['initialName'] = researcher.initial_nm
        
    return render(request, template_name, context)



#==============================================================================
#  Profile Update [UPDATE RESEARCHER]
#==============================================================================
def profileUpdate(request):

    template_name = 'pjo_main.html'
    context = {
        'title' : 'Main',
    }

    # Dictionary
    dicResearcher = {}
    
    dicResearcher['id'] = request.POST['txtId']
    dicResearcher['firstName'] = request.POST['txtFirstName']
    dicResearcher['lastName'] = request.POST['txtLastName']
    dicResearcher['password'] = request.POST['txtPassword']
    
    # Dao
    mDao = MemberDao()
    
    # Update
    result = mDao.updateResearcher(dicResearcher)

    if result:
        context['errMsg'] = "Your profile is changed!!"
    else:
        context['errMsg'] = "[profileUpdate] Fail"
        

    return render(request, template_name, context)




'''
##########################################################################################################
#  Navigation Bar
##########################################################################################################
'''
def setNavigation(request, context):

    initialName = ""
    if 'initial_nm' in request.session:
        initialName = request.session.get("initial_nm")
        logger.debug("NAVIGATION CHECK ===[" + initialName + "]")


    if initialName is None or initialName == "":
        logger.debug("initial name is none, sign in first.")
        context['signYn'] = "N"
        context['errMsg'] = "Sign In First!!"
    else:
        context['initialName'] = initialName


    # DAO
    pDao = ProjectDao()

    if 'txtProjectId' in context:
        
        projectId = context['txtProjectId']
        
        # get Project Information
        projectName = pDao.getProjectName(projectId)
        context['navProjectId'] = projectId
        context['txtProjectName'] = projectName

    if 'txtSubjectId' in context:
        
        subjectId = context['txtSubjectId']
        
        # get Subject Information
        subject = pDao.selectSubjectObject(subjectId)
        
        context['navSubjectId'] = subjectId
        context['txtSubjectNum']  = subject.subject_num
        context['txtSubjectName'] = subject.subject_nm

    if 'txtSessionId' in context:
        
        sessionId = context['txtSessionId']
        
        # get Session Information
        session = pDao.selectSessionObject(sessionId)
        
        context['navSessionId'] = sessionId
        context['txtSessionNum'] = session.session_num
        context['txtSessionName'] = session.session_nm
        
        if session.source_id is None or session.source_id == "" :
            context['txtMapYn'] = "N"
            context['navStage'] = 3
        else:
            context['txtMapYn'] = "Y"
            context['navStage'] = 4




'''
##########################################################################################################
#  MANAGE PROJECT
##########################################################################################################
'''

#==============================================================================
#  Project Form page
#==============================================================================
def projectInit(request):

    template_name = 'project/project.html'

    context = {
        'navStage' : 0,
        'subTitle' : 'Register Project Info',
    }

    # setting navigation
    setNavigation(request, context)


    if 'signYn' in context:
        template_name = 'member/signIn.html'
    else:

        # this year
        strYear = CommonUtil().f_getDate("Y")

        # Dao
        dao = CommonDao()

        # get common code
        code002 = dao.selectCodeList("002")
        code003 = dao.selectCodeList("003")

        # setting context
        context['scrType']     = "REGISTER"
        context['initialName'] = context['initialName']
        context['year']        = strYear
        context['code002']     = code002
        context['code003']     = code003

    return render(request, template_name, context)




#==============================================================================
#  Project Register
#==============================================================================
def projectRegister(request):

    template_name = 'project/projectList.html'
    context = {
        'navStage' : 0,
    }

    # setting navigation
    setNavigation(request, context)

    if 'signYn' in context:
        template_name = 'member/signIn.html'
    else:

        # DAO
        pDao = ProjectDao()

        # Set Dictionary
        dicProject = {}

        dicProject['initialName'] = request.POST['txtInitial']
        dicProject['year'] = request.POST['txtYear']
        dicProject['animalType'] = request.POST['selAnimalType']
        dicProject['methodType'] = request.POST['selMethodType']
        dicProject['projectAim'] = request.POST['txtProjectAim']
        dicProject['memberId'] = request.session.get("member_id")
        dicProject['regDate'] = CommonUtil().f_getDateTime()

        # Insert
        result = pDao.insertProjectInfo(dicProject)

        if result:
            context['errMsg'] = "Register Success!!"
        else:
            context['errMsg'] = "Register Fail!!"

    return render(request, template_name, context)





#==============================================================================
#  Project Detail
#==============================================================================
def projectDetail(request, project_id):

    template_name = 'project/project.html'

    context = {
        'navStage' : 0,
        'subTitle' : 'Modify Project Info',
    }

    # setting navigation
    setNavigation(request, context)

    if 'signYn' in context:
        template_name = 'member/signIn.html'

    else:

        # DAO
        pDao = ProjectDao()
        cDao = CommonDao()

        # get choosing data
        project = pDao.selectProjectObject(project_id)

        # get common code
        code002 = cDao.selectCodeList("002")
        code003 = cDao.selectCodeList("003")


        # setting context
        context['scrType']     = "MODIFY"
        context['code002']     = code002
        context['code003']     = code003
        context['sessionInitialName'] = context['initialName']

        context['projectId']   = project.project_id
        context['initialName'] = project.initial_nm
        context['year']        = project.year
        context['animalType']  = project.animal_type
        context['methodType']  = project.method_type
        context['serialNo']    = project.serial_no
        context['projectAim']  = project.project_aim
        context['useYn']       = project.use_yn


    return render(request, template_name, context)





#==============================================================================
#  Project Modify
#==============================================================================
def projectModify(request):

    template_name = 'project/projectList.html'
    context = {
        'navStage' : 0,
    }

    # setting navigation
    setNavigation(request, context)

    if 'signYn' in context:
        template_name = 'member/signIn.html'
    else:

        strInitial  = request.POST['txtInitial']

        if strInitial == context['initialName']:

            # DAO
            pDao = ProjectDao()

            # values
            projectId = request.POST['projectId']
            strProjectAim  = request.POST['txtProjectAim']


            # get choosing data
            project = pDao.selectProjectObject(projectId)

            if project.use_yn != 'Y':
                context['errMsg'] = "Modify Fail. [Check Use Y/N]"

            else:

                ### UPDATE
                result = pDao.updateProjectProjectAim(project, strProjectAim)

                if result:
                    context['errMsg'] = "Modify Success!!"
                else:
                    context['errMsg'] = "Modify Fail!!"

        else:
            context['errMsg'] = "Modify Fail. [Check Registrant]"

    return render(request, template_name, context)
    

    
    
    

#==============================================================================
#  Project List Search Form
#==============================================================================
def projectList(request):

    template_name = 'project/projectList.html'

    context = {
        'navStage' : 0,
    }


    #---------------------------------------------------------------------
    #  get default items
    #---------------------------------------------------------------------
    # Dao
    cDao = CommonDao()

    # get common code
    code002 = cDao.selectCodeList("002")
    code003 = cDao.selectCodeList("003")


    # get researcher's initial list
    initialList = cDao.selectResearcherInitialList()

    # setting context
    context['code002']     = code002
    context['code003']     = code003
    context['initialList'] = initialList


    #---------------------------------------------------------------------
    #  get project list
    #---------------------------------------------------------------------
    #  get parameters
    if 'selInitial' in request.POST:
        strInitialName = request.POST['selInitial']
        context['selInitial'] = strInitialName
    else:
        strInitialName = ""

    if 'txtYear' in request.POST:
        strYear = request.POST['txtYear']
        context['txtYear'] = strYear
    else:
        strYear = ""

    if 'selAnimalType' in request.POST:
        strAnimalType = request.POST['selAnimalType']
        context['selAnimalType'] = strAnimalType
    else:
        strAnimalType = ""

    if 'selMethodType' in request.POST:
        strMethodType = request.POST['selMethodType']
        context['selMethodType'] = strMethodType
    else:
        strMethodType = ""

    if 'txtProjectAim' in request.POST:
        strProjectAim = request.POST['txtProjectAim']
        context['txtProjectAim'] = strProjectAim
    else:
        strProjectAim = ""

    if 'txtPage' in request.POST:
        strPage = request.POST['txtPage']
    else:
        strPage = 1
    

    # Dao
    pDao = ProjectDao()

    # Get Project List
    resultList = pDao.selectProjectList(context)
    
    # Paginator
    paginator = Paginator(resultList, 20)


    try:
        resultList = paginator.page(strPage)
    except PageNotAnInteger:
        resultList = paginator.page(1)
    except EmptyPage:
        resultList = paginator.page(paginator.num_pages)
        
    # context setting
    context['resultList'] = resultList

    return render(request, template_name, context)





#==============================================================================
#  Experimental Design Download
#==============================================================================
def edDownLoad(request):
    
    # get JSON data
    jData = json.loads(request.body)

    # values
    strProjectId = jData['txtProjectId']
    logger.debug("strProjectId==" + strProjectId)

    # DAO
    pDao = ProjectDao()
    eDao = EdDao()
    
    # get Experimental List
    edList = pDao.selectExperimentalDesignList(strProjectId)
    print edList


#     for txtEdId in edList:
#         edId = txtEdId['META_ACQ'][2:]
        
            
    edId = "000001"
    edValueList = eDao.selectEDValueList(edId)
    print edValueList

    jsonTuple = "" # [row['session_nm'] + " ::> " + row['session_cmt'] for row in sessionList]

    return HttpResponse(json.dumps(jsonTuple), content_type="application/json")



################################################################################
#  MANAGE Subject
################################################################################

#==============================================================================
#  Subject Form
#==============================================================================
def subjectList(request):

    template_name = 'project/subjectList.html'

    context = {
        'navStage' : 1,
    }

    # values
    strProjectId = request.POST['txtProjectId']
    context['txtProjectId'] = strProjectId

    # setting navigation
    setNavigation(request, context)

    if 'signYn' in context:
        template_name = 'member/signIn.html'

    else:

        if strProjectId is not None:

            # get Subject List
            inquirySubjectList(request, strProjectId, context)

    return render(request, template_name, context)




#==============================================================================
#  Inquiry Subject List
#==============================================================================
def inquirySubjectList(request, projectId, context):

    # DAO
    pDao = ProjectDao()

    # get subject list using Project_id
    subjectList = pDao.selectSubjectList(projectId)

    # setting context
    context['subjectList'] = subjectList

    return context




#==============================================================================
#  Add Subject
#==============================================================================
def subjectRegister(request):

    template_name = 'project/subjectList.html'
    context = {
        'navStage' : 1,
    }

    # values
    strProjectId = request.POST['txtProjectId']
    context['txtProjectId'] = strProjectId

    # setting navigation
    setNavigation(request, context)


    if 'signYn' in context:
        template_name = 'member/signIn.html'

    else:

        # check changeable
        checkResultMsg = check_Modify_Project(context)

        if checkResultMsg != "Y":
            context['errMsg'] = checkResultMsg

        else:

            # Dictionary
            dicSubject = {}

            dicSubject['projectId'] = strProjectId
            dicSubject['memberId'] = request.session.get("member_id")
            dicSubject['subjectName'] = request.POST['txtSubjectName']
            dicSubject['subjectComment'] = request.POST['txtSubjectComment']

            # DAO
            pDao = ProjectDao()

            ### INSERT
            result = pDao.insertSubjectInfo(dicSubject)

            if result:
            #    context['errMsg'] = "Register Success!!"
                pass
            else:
                context['errMsg'] = "Register Fail!!"

            # get Subject List
            inquirySubjectList(request, strProjectId, context)

    return render(request, template_name, context)



#==============================================================================
#  Modify Subject
#==============================================================================
def subjectModify(request):

    template_name = 'project/subjectList.html'
    context = {
        'navStage' : 1,
    }

    # values
    strProjectId = request.POST['txtProjectId']
    context['txtProjectId'] = strProjectId

    # setting navigation
    setNavigation(request, context)


    if 'signYn' in context:
        template_name = 'member/signIn.html'

    else:

        # check changeable
        checkResultMsg = check_Modify_Project(context)

        if checkResultMsg != "Y":
            context['errMsg'] = checkResultMsg

        else:

            # DAO
            pDao = ProjectDao()

            # Dictionary
            dicSubject = {}

            dicSubject['subjectId'] = request.POST['txtSubjectId']
            dicSubject['subjectName'] = request.POST['txtSubjectName']
            dicSubject['subjectComment'] = request.POST['txtSubjectComment']

            ### UPDATE
            result = pDao.updateSubjectSubjectName(dicSubject)

            if result:
            #    context['errMsg'] = "Modify Success!!"
                pass
            else:
                if "error" in dicSubject:
                    context['errMsg'] = dicSubject["error"]
                else:
                    context['errMsg'] = "Modify Fail!!"

        # get Subject List
        inquirySubjectList(request, strProjectId, context)

    return render(request, template_name, context)



#==============================================================================
#  Check available of changing :
#       - Same person who registered Project only can add/modify subject and session.
#       - Under [Use_yn = Y] condition, subject and session can be changed.
#==============================================================================
def check_Modify_Project(context):

    sessionInitialName = context["initialName"]

    # DAO
    pDao = ProjectDao()

    # get project data for check
    projectId = context["txtProjectId"]
    project = pDao.selectProjectObject(projectId)

    resultMsg = "Y"

    if project.use_yn != 'Y':
        resultMsg = "Save Fail. [Check Project Use Y/N]"

    elif project.initial_nm != sessionInitialName:
        resultMsg = "Save Fail. [Check Registrant]"
    
    elif "txtSubjectId" in context:

        subjectId = context["txtSubjectId"]
        
        # get session data for check
        subject = pDao.selectSubjectObject(subjectId)
        
        if subject.use_yn != "Y":
            resultMsg = "Save Fail. [Check Subject Use Y/N]"

    return resultMsg






################################################################################
#  Manage Session
################################################################################

#==============================================================================
#  Session Form
#==============================================================================
def sessionList(request):

    template_name = 'project/sessionList.html'

    context = {
        'navStage' : 2,
    }
    
    
    # values
    strProjectId = request.POST['txtProjectId']
    context['txtProjectId'] = strProjectId
    
    strSubjectId = request.POST['txtSubjectId']
    context['txtSubjectId'] = strSubjectId
    

    # setting navigation 
    setNavigation(request, context)   

    if 'signYn' in context:
        template_name = 'member/signIn.html'
        
    else:

        if strProjectId is not None:
            if strSubjectId is not None:

                # get Session List
                inquirySessionList(request, strProjectId, strSubjectId, context)

    return render(request, template_name, context)



#==============================================================================
#  Inquiry Session List
#==============================================================================
def inquirySessionList(request, projectId, subjectId, context):

    logger.debug("projectId=[" + projectId+ "]")
    logger.debug("subjectId=[" + subjectId+ "]")

    subjectNum = context['txtSubjectNum']
    logger.debug("subjectNum=[" + subjectNum+ "]")

    # DAO
    pDao = ProjectDao()

    # get session list using Project_id, subject_num
    sessionList = pDao.selectSessionList(projectId, subjectNum)

    # setting context
    context['sessionList'] = sessionList

    return context




#==============================================================================
#  Add Session
#==============================================================================
def sessionRegister(request):

    template_name = 'project/sessionList.html'
    context = {
        'navStage' : 2,
    }

    
    # values
    strProjectId = request.POST['txtProjectId']
    context['txtProjectId'] = strProjectId
    
    strSubjectId = request.POST['txtSubjectId']
    context['txtSubjectId'] = strSubjectId


    # setting navigation 
    setNavigation(request, context)   

    if 'signYn' in context:
        template_name = 'member/signIn.html'
        
    else:
    
        # check changeable
        checkResultMsg = check_Modify_Project(context)
    
        if checkResultMsg != "Y":
            context['errMsg'] = checkResultMsg
    
        else:
    
            # Dao
            pDao = ProjectDao()
            
            # Dictionary
            dicSession = {}
    
            dicSession['projectId'] = strProjectId
            dicSession['subjectNum'] = request.POST['txtSubjectNum']
            dicSession['sessionName'] = request.POST['txtSessionName']
            dicSession['sessionComment'] = request.POST['txtSessionComment']
            dicSession['memberId'] = request.session.get("member_id")
        
            ### INSERT
            result = pDao.insertSessionInfo(dicSession)

            if result:
#                 context['errMsg'] = "Register Success!!"
                pass
            else:
                context['errMsg'] = "Register Fail!!"

    
        # get Session List
        inquirySessionList(request, strProjectId, strSubjectId, context)

    return render(request, template_name, context)





#==============================================================================
#  Modify Session
#==============================================================================
def sessionModify(request):

    template_name = 'project/sessionList.html'
    context = {
        'navStage' : 2,
    }

    # values
    strProjectId = request.POST['txtProjectId']
    context['txtProjectId'] = strProjectId
    
    strSubjectId = request.POST['txtSubjectId']
    context['txtSubjectId'] = strSubjectId


    # setting navigation
    setNavigation(request, context)

    if 'signYn' in context:
        template_name = 'member/signIn.html'

    else:
        
        # check changeable
        checkResultMsg = check_Modify_Project(context)
    
        if checkResultMsg != "Y":
            context['errMsg'] = checkResultMsg
    
        else:

            # Dao
            pDao = ProjectDao()
            
            # Dictionary
            dicSession = {}
    
            dicSession['sessionId'] = request.POST['txtSessionId']
            dicSession['sessionName'] = request.POST['txtSessionName']
            dicSession['sessionComment'] = request.POST['txtSessionComment']

            ### UPDATE
            result = pDao.updateSessionSessionName(dicSession)            

            if result:
                context['errMsg'] = "Modify Success!!"
            else:
                if "error" in dicSession:
                    context['errMsg'] = dicSession["error"]
                else:
                    context['errMsg'] = "Modify Fail!!"

    
        # get Session List
        inquirySessionList(request, strProjectId, strSubjectId, context)

    return render(request, template_name, context)





#==============================================================================
#  Load session copy form
#==============================================================================
def sessionCopyForm(request, project_id, subject_id):
    
    template_name = 'project/sessionCopy.html'

    context = {
        'navStage' : 2,
    }
    
    # values
    context['txtProjectId'] = project_id
    context['txtSubjectId'] = subject_id

    # setting navigation
    setNavigation(request, context)

    if 'signYn' in context:
        template_name = 'member/signIn.html'
    else:

        if project_id is not None:
            if subject_id is not None:
                
                # get Session List
                inquirySessionList(request, project_id, subject_id, context)
    
                # get subject list
                pDao = ProjectDao()
                subjectList = pDao.selectSubjectListForSessionCopy(project_id, subject_id)
                context['subjectList'] = subjectList

    return render(request, template_name, context)





#==============================================================================
#  Change subject -> select session list
#==============================================================================
def changeSubject(request):

    # get JSON data
    jData = json.loads(request.body)

    # values
    strProjectId = jData['txtProjectId']
    strSubjectNum  = jData['selSubjectNum']

    # DAO
    pDao = ProjectDao()
    
    # get session list
    sessionList = pDao.selectSessionList(strProjectId, strSubjectNum)

    jsonTuple = [row['session_nm'] + " ::> " + row['session_cmt'] for row in sessionList]

    return HttpResponse(json.dumps(jsonTuple), content_type="application/json")




#==============================================================================
#  Change subject -> select session list
#==============================================================================
def sessionCopySave(request):

    template_name = 'project/sessionCopy.html'
    
    context = {
        'navStage' : 2,
    }

    # values
    strProjectId = request.POST['txtProjectId']
    context['txtProjectId'] = strProjectId

    strSubjectId = request.POST['txtSubjectId']
    context['txtSubjectId'] = strSubjectId


    # setting navigation
    setNavigation(request, context)
    
    # check changeable
    checkResultMsg = check_Modify_Project(context)

    if checkResultMsg != "Y":
        context['errMsg'] = checkResultMsg
    else:

        # DAO
        pDao = ProjectDao()

        # values
        strSubjectNum = request.POST['txtSubjectNum']
        strSessionText = request.POST['hidSessionText']

        # Dictionary
        dicSession = {}

        dicSession['projectId'] = strProjectId
        dicSession['subjectNum'] = strSubjectNum
        dicSession['memberId'] = request.session.get("member_id")
        

        # split session
        ssnList = strSessionText.split("||")
        strSessionName = ""
        strSessionComment = ""

        # reult
        result = True

        for regSsnText in ssnList:
            
            logger.debug("regSsnText=[" + regSsnText+ "]")

            # split session name & comment
            nm_cmt_list = regSsnText.split(" ::> ")

            if (len(nm_cmt_list) == 2):
                strSessionName = nm_cmt_list[0]
                strSessionComment = nm_cmt_list[1]
 
                logger.debug("strSessionName=[" + strSessionName+ "]")
                logger.debug("strSessionComment=[" + strSessionComment+ "]")
                
                dicSession['sessionName'] = strSessionName
                dicSession['sessionComment'] = strSessionComment
                
            
                ### INSERT
                result = pDao.insertSessionInfo(dicSession)
    
                if not result:
                    break

            else:
                result = False
                break
            

        if result:
            template_name = 'project/sessionList.html'
            context['errMsg'] = "Copy Session Success!!"

        else:
            template_name = 'project/sessionCopy.html'
            context['errMsg'] = "Copy Session Fail!!"

            # get subject list
            subjectList = pDao.selectSubjectListForSessionCopy(strProjectId, strSubjectId)
            context['subjectList'] = subjectList


    # get Session List
    inquirySessionList(request, strProjectId, strSubjectId, context)

    return render(request, template_name, context)





################################################################################
#  MANAGE SOURCE
################################################################################

#==============================================================================
#  Source Form page
#==============================================================================
def sourceInit(request):

    template_name = 'source/sourceList.html'

    context = {
        'title' : 'Source List',
        'sourceForm' : SourceForm()
    }

    return render(request, template_name, context)



#==============================================================================
#  Source List page
#==============================================================================
def sourceList(request):

    template_name = 'source/sourceList.html'

    context = {
        'title' : 'Source List'
    }


    # values
    strTitle = request.POST['txtTitle']
    strRegStart = request.POST['txtRegStart']
    strRegEnd = request.POST['txtRegEnd']
    strScanStart = request.POST['txtScanStart']
    strScanEnd = request.POST['txtScanEnd']
    strScanYn = request.POST['selScanYn']
    strPage = request.POST['page']

    # Dictionary
    dicSource = {}
    dicSource['title'] = strTitle
    dicSource['regStart'] = strRegStart
    dicSource['regEnd'] = strRegEnd
    dicSource['scanStart'] = strScanStart
    dicSource['scanEnd'] = strScanEnd
    dicSource['scanYn'] = strScanYn

    # DAO
    sDao = SourceDao()
    
    # Get Source List
    sourceList = sDao.selectSourceListForSourceForm(dicSource)

    # Paginator
    paginator = Paginator(sourceList, 25)

    try:
        resultList = paginator.page(strPage)
    except PageNotAnInteger:
        resultList = paginator.page(1)
    except EmptyPage:
        resultList = paginator.page(paginator.num_pages)


    #### FORM
    sourceForm = SourceForm(initial={'txtTitle' : strTitle
                                     , 'txtRegStart' : strRegStart
                                     , 'txtRegEnd' : strRegEnd
                                     , 'txtScanStart' : strScanStart
                                     , 'txtScanEnd' : strScanEnd
                                     , 'selScanYn' : strScanYn
                                     , 'init' : "N"
                                     })
    
    context['resultList'] = resultList
    context['sourceForm'] = sourceForm

    return render(request, template_name, context)




#==============================================================================
#  Add source folder to sourcedata / insert db
#==============================================================================
def addNewSource(request):
    
    # Util
    cUtil = CommonUtil()

    # Dao
    sDao = SourceDao()

    # Dictionary
    dicSource = {}
    dicSource['memberId'] = request.session.get("member_id")
    dicSource['regDate'] = CommonUtil().f_getDateTime()

    
    # get Path
    tempPath = cUtil.f_getPath("T")
    sourcePath = cUtil.f_getPath("S")

    # Find source
    for sourceNm in sorted(os.listdir(tempPath)):
        result = cUtil.f_moveFolder(tempPath, sourcePath, sourceNm)

        if result:
            
            # Insert
            dicSource['title'] = sourceNm
            sDao.insertSourceInfo(dicSource)
        else:
            logger.error("Move File==>[" + sourceNm + "]")

    return HttpResponseRedirect(reverse("pjo:sourceInit"))




#==============================================================================
#  CheckScan for source
#==============================================================================
def checkScan(request):

    initialName = request.session.get("initial_nm")

    # result
    jsonTuple = []

    if initialName is None:

        jsonTuple = ['N', 'Sign In First.']

        return HttpResponse(json.dumps(jsonTuple), content_type="application/json")

    else:

        # get JSON data
        jData = json.loads(request.body)

        # values
        strSourceID = jData['txtSourceId']
        logger.debug("strSouceId===[" + strSourceID + "]")


        # DAO
        dao = SourceDao()

        # get choosing source's title
        source = dao.selectSourceObject(strSourceID)

        # member_id
        member_id = request.session.get("member_id")

        if source.scan_yn == "N" :

            # Read file / Insert header info to Scan
            try:
                checkscans = CheckScan()
                checkscans.check_subject(strSourceID, source.title, member_id)
            except Exception, e:
                jsonTuple = ['N', str(e) + "(CheckScan)[" + source.title + "]"]
                return HttpResponse(json.dumps(jsonTuple), content_type="application/json")

            # update source scan_yn->Y
            dao.updateSourceScanYn(strSourceID)

            jsonTuple = ['Y', str(CommonUtil().f_getDateTimeFormat('Y-m-d H:i'))]

        return HttpResponse(json.dumps(jsonTuple), content_type="application/json")




#==============================================================================
#  Scan List page
#==============================================================================
def scanList(request):

    template_name = 'source/scanList.html'

    context = {
        'title' : 'Scan List'
    }

    # values
    strSourceId = request.POST['sourceId']
    logger.debug("strSourceId===[" + strSourceId + "]")

    # DAO
    dao = SourceDao()

    # Source Object
    source = dao.selectSourceObject(strSourceId)

    # Scan List
    scanList = dao.selectScanList(strSourceId)

    # Set Context
    context['txtSourceId'] = strSourceId
    context['txtTitle'] = source.title
    context['resultList'] = scanList

    return render(request, template_name, context)




#==============================================================================
#  Mapping Init Page
#==============================================================================
def mapInit(request):

    context = {
        'navStage' : 3,
    }
 
    # values
    strProjectId = request.POST['txtProjectId']
    context['txtProjectId'] = strProjectId
    
    strSubjectId = request.POST['txtSubjectId']
    context['txtSubjectId'] = strSubjectId

    strSessionId = request.POST['txtSessionId']
    context['txtSessionId'] = strSessionId


    # setting navigation 
    setNavigation(request, context)   
    

    if 'signYn' in context:
        template_name = 'member/signIn.html'
        
    else:
    
        #--------------------------
        # 1) Before mapping :
        #--------------------------
        if "txtMapYn" not in context or context['txtMapYn'] == "N":
            template_name = 'mapping/mappingPre.html'
            
            context['initPreMap'] = 'N'
            context = mapInquiryPre(request, context)
    
        #--------------------------
        # 2) After mapping :
        #--------------------------
        else:
            template_name = 'mapping/mappingPost.html'
            context = mapInquiryPost(request, context)
    
    
    return render(request, template_name, context)





#==============================================================================
#  Mapping - Setting Project Info, unmapped Source List
#==============================================================================
def mapInquiryPre(request, context):

    #  get parameters
    if 'txtSourceTitle' in request.POST:
        strSourceTitle = request.POST['txtSourceTitle']
        context['txtSourceTitle'] = strSourceTitle
    else:
        strSourceTitle = ""

    if 'selMappingYn' in request.POST:
        strMappingYn = request.POST['selMappingYn']
        context['selMappingYn'] = strMappingYn
    elif 'initPreMap' in context:
        strMappingYn = context['initPreMap']
    else:
        strMappingYn = ""

    logger.debug("strSourceTitle=[" + strSourceTitle + "]")
    logger.debug("strMappingYn=[" + strMappingYn + "]")


    # inquiry dictionary
    dicSource = {}
    dicSource["title"] = strSourceTitle
    dicSource["mapping_yn"] = strMappingYn
    dicSource["scan_yn"] = "Y"

    # DAO
    sDao = SourceDao()

    # Inquiry source List
    sourceList = sDao.selectSourceList(dicSource)
    
    # Paginator
    paginator = Paginator(sourceList, 20)

    if 'page' in context:
        strPage = context['page']
    else:
        strPage = 1

    try:
        resultList = paginator.page(strPage)
    except PageNotAnInteger:
        resultList = paginator.page(1)
    except EmptyPage:
        resultList = paginator.page(paginator.num_pages)    
    
    context['resultList'] = resultList

    return context




#==============================================================================
#  Mapping - Setting Project Info, mapped Source Info, Scan List
#==============================================================================
def mapInquiryPost(request, context):

    # DAO
    sDao = SourceDao()
    pDao = ProjectDao()

    # Session Object
    sessionObj = pDao.selectSessionObject(context['txtSessionId'])
    strSourceId = sessionObj.source_id
    logger.debug("strSourceId==[" + strSourceId + "]")

    # Source Object
    sourceObj = sDao.selectSourceObject(strSourceId)

    # Inquiry Scan List
    scanList = sDao.selectScanList(strSourceId)


    context['txtSourceId'] = strSourceId
    context['txtTitle'] = sourceObj.title
    context['resultList'] = scanList

    return context





#==============================================================================
#  Mapping - Search Source
#==============================================================================
def mapSourceList(request):

    template_name = 'mapping/mappingPre.html'
    context = {
        'navStage' : 3,
    }
 
    # values
    strProjectId = request.POST['txtProjectId']
    context['txtProjectId'] = strProjectId
    
    strSubjectId = request.POST['txtSubjectId']
    context['txtSubjectId'] = strSubjectId

    strSessionId = request.POST['txtSessionId']
    context['txtSessionId'] = strSessionId

    strPage = request.POST['txtPage']
    context['page'] = strPage
    
    # setting navigation 
    setNavigation(request, context)   
    

    if 'signYn' in context:
        template_name = 'member/signIn.html'
    else:
        context = mapInquiryPre(request, context)
    
    return render(request, template_name, context)





#==============================================================================
#  Mapping - Get Scan List (Ajax)
#==============================================================================
def mapAjaxScanList(request):

    # get JSON data
    jData = json.loads(request.body)

    # values
    strSourceId = jData['txtSourceId']

    # DAO
    dao = SourceDao()

    # Scan List
    scanList = dao.selectScanList(strSourceId)


    jsonTuple = []
    for row in scanList :
        scanInfo = row['scan_num'] + "|" + row['sch_proto_nm'] + "|" + row['sch_echo_time'] + "|" + row['sch_repet_time'] + "|" + row['sch_matrix'] + "|" + row['sch_slices'] + "|" + row['sch_n_repet'] + "|" + row['sch_spat']
        jsonTuple.append(scanInfo)

    return HttpResponse(json.dumps(jsonTuple), content_type="application/json")




#==============================================================================
#  Mapping - Mapping Session and Source
#==============================================================================
def mapMapping(request):

    template_name = 'mapping/mappingPost.html'
    context = {
        'navStage' : 4,
    }
 
    # values
    strProjectId = request.POST['txtProjectId']
    context['txtProjectId'] = strProjectId
    
    strSubjectId = request.POST['txtSubjectId']
    context['txtSubjectId'] = strSubjectId

    strSessionId = request.POST['txtSessionId']
    context['txtSessionId'] = strSessionId


    # setting navigation 
    setNavigation(request, context)   
    

    if 'signYn' in context:
        template_name = 'member/signIn.html'
        
    else:
        
        # check changeable
        checkResultMsg = check_Modify_Project(context)

        if checkResultMsg != "Y":
            template_name = 'mapping/mappingPre.html'
            context['errMsg'] = checkResultMsg
    
        else:
    
            # values
            strSourceId = request.POST['txtSourceId']
            context['txtSourceId'] = strSourceId
        
            # DAO
            sDao = SourceDao()
            pDao = ProjectDao()
        
            # Session Object
            strSessionId = context['txtSessionId']
            sessionObj = pDao.selectSessionObject(strSessionId)
        
            # Source Object
            sourceObj = sDao.selectSourceObject(strSourceId)
        
        
            if sessionObj.use_yn == "N" :
                context['errMsg'] = "This Source can't use. [USE_YN=N]"
                template_name = 'mapping/mappingPre.html'
                context = mapInquiryPre(request, context)
            elif sessionObj.source_id is not None and sessionObj.source_id != "" :
                context['errMsg'] = "This Source has been mapped already.[SOURCE_ID]"
                template_name = 'mapping/mappingPre.html'
                context = mapInquiryPre(request, context)
            elif sourceObj.mapping_yn == "Y" :
                context['errMsg'] = "This Source has been mapped already.[MAPPING_YN=Y]"
                template_name = 'mapping/mappingPre.html'
                context = mapInquiryPre(request, context)
            else :
                # Mapping
                # 1. update Session : source_id setting
                pDao.updateSessionForMapping(strSessionId, strSourceId)
        
                # 2. update Source : mapping_yn = Y
                sDao.updateSourceForMapping(strSourceId, "Y")
        
                # 3. select Scan
                scanList = sDao.selectScanList(strSourceId)
        
                # context
                context['txtTitle']   = sourceObj.title
                context['resultList'] = scanList

    return render(request, template_name, context)







#==============================================================================
#  Mapping - Load Meta Init
#==============================================================================
def metaInit(request):

    # get JSON data
    jData = json.loads(request.body)

    # values
    txtScanId = jData['txtScanId']

    # Dao
    sDao = SourceDao()
    cDao = CommonDao()

    # list
    resultList = []

    # get Scan Object
    scanObj = sDao.selectScanObjectForJson(txtScanId)
    resultList.extend(list(scanObj))

    # get common code
    code004 = cDao.selectCodeListForJson("004")
    resultList.extend(code004)
    
    jsonResult = serializers.serialize("json", resultList)
    
    return HttpResponse(jsonResult, content_type="application/json")



#==============================================================================
#  Meta - Load Suffix Code
#==============================================================================
def metaCode(request):

    # get JSON data
    jData = json.loads(request.body)

    # values
    txtDataType = jData['txtDataType']

    groupId = CommonUtil().f_getDataTypeGroupId(txtDataType)

    # Dao
    dao = CommonDao()

    # get common code
    codeList = dao.selectCodeListForJson(groupId)

    jsonCodeList = serializers.serialize("json", codeList)

    return HttpResponse(jsonCodeList, content_type="application/json")





#==============================================================================
#  Meta - Save Meta Info
#==============================================================================
def metaSave(request):

    ## TODO check : can other member change meta info?
    
    # get JSON data
    jData = json.loads(request.body)

    # values
    strScanId = jData['txtScanId']
    strPid = jData['selPid']
    strDataType = jData['selDataType']
    strAcq = jData['txtAcq']
    strRec = jData['txtRec']
    strTask = jData['txtTask']
    strSuffix = jData['selSuffix']

    logger.debug("strDataType == [" + strDataType + "]")

    # Dao
    dao = SourceDao()

    # get Scan Obj
    scanObj = dao.selectScanObject(strScanId)
    
    if scanObj.derive_yn == "Y":
        jsonTuple = ['N', 'You could not edit Meta after derivation.']
    else:

        # Dictionary for Update
        dicScan = {}

        # functional MRI
        if(strDataType == "F"):
            dicScan["strTask"] = strTask
            dicScan["strAcq"] = strAcq
            dicScan["strRec"] = strRec
        # fMRI infusion
        elif(strDataType == "I"):
            dicScan["strTask"] = "infusion"
            dicScan["strAcq"] = strAcq
            dicScan["strRec"] = strRec
        # DWI
        elif(strDataType == "D"):
            dicScan["strAcq"] = strAcq
        # field Map
        elif(strDataType == "M"):
            dicScan["strAcq"] = strAcq
        # Structural Imaging
        elif(strDataType == "A"):
            dicScan["strAcq"] = strAcq
            dicScan["strRec"] = strRec

        dicScan["sourceId"] = scanObj.source_id
        dicScan["strPid"] = strPid
        dicScan["strDataType"] = strDataType
        dicScan["strSuffix"] = strSuffix


        # get Run Index
        if scanObj.meta_run is None or scanObj.meta_run == "":
            strMetaRun = dao.selectRunIndex(dicScan)
        else:
            strMetaRun = scanObj.meta_run
        dicScan["strRun"] = strMetaRun
        logger.debug("strMetaRun==[" + strMetaRun + "]")
            

        # Update
        result = dao.updateScanInfoForMeta(dicScan, scanObj)

        if result:
            jsonTuple = ['Y', 'Save Success.']
        else:
            jsonTuple = ['N', 'Save Fail.']            


    return HttpResponse(json.dumps(jsonTuple), content_type="application/json")





#==============================================================================
#  Derive : brk2nii, DB update
#==============================================================================
def derive(request):

    template_name = 'mapping/mappingPost.html'
    context = {
        'navStage' : 4,
    }
    
    # values
    strProjectId = request.POST['txtProjectId']
    context['txtProjectId'] = strProjectId
    
    strSubjectId = request.POST['txtSubjectId']
    context['txtSubjectId'] = strSubjectId
    
    strSessionId = request.POST['txtSessionId']
    context['txtSessionId'] = strSessionId


    # setting navigation 
    setNavigation(request, context)   

    if 'signYn' in context:
        template_name = 'member/signIn.html'
        
    else:
        
        # check changeable
        checkResultMsg = check_Modify_Project(context)

        # values
        strTitle = request.POST['txtTitle']
        strSourceId = request.POST['txtSourceId']
        strSelectedScan = request.POST['txtSelectedScan']
        logger.debug("strSelectedScan=[" + strSelectedScan + "]")
        
        # DAO
        sDao = SourceDao()
    
        # return 
        successCnt = 0
        
        if checkResultMsg != "Y":
            context['errMsg'] = checkResultMsg
    
        else:

            # BRK2NII
            brk = Brk2nii()
        
            # make folder & return file name dictionary
            fileDict = CommonUtil().f_getFileDict(strSessionId)
        
            # for loop : selected scan
            arrScan = strSelectedScan.split(":")
        
            for scanId in arrScan:
                if scanId is None or scanId == "":
                    pass
                else:
        
                    # scan object
                    scanObj = sDao.selectScanObject(scanId)
        
                    # Derive - brk2nii
                    try:
                        resultTF = brk.derive(strTitle, fileDict, scanObj);
                        if resultTF:
                            successCnt = successCnt + 1
                    except Exception, e:
                        context['errMsg'] = str(e) + "(derive)[" + scanObj.sch_proto_nm + "]"
        

            if successCnt > 0:      
                context['errMsg'] = "Create File : Success!! Total Derive Count : [" + str(successCnt) + "]"
            else:
                context['errMsg'] = "[Fail] Create File."
                
                
        
        # Inquiry Scan List
        scanList = sDao.selectScanList(strSourceId)
    
        context['txtSourceId'] = strSourceId
        context['txtTitle'] = strTitle
        context['resultList'] = scanList
        
    
    return render(request, template_name, context)





#==============================================================================
#  Derive : selected file download
#==============================================================================
def downloadSingleFile(request):
    
    template_name = 'mapping/mappingPost.html'
    context = {
        'navStage' : 4,
    }
    
    # values
    strProjectId = request.POST['txtProjectId']
    context['txtProjectId'] = strProjectId
    
    strSubjectId = request.POST['txtSubjectId']
    context['txtSubjectId'] = strSubjectId
    
    strSessionId = request.POST['txtSessionId']
    context['txtSessionId'] = strSessionId


    # setting navigation 
    setNavigation(request, context)   

    if 'signYn' in context:
        template_name = 'member/signIn.html'
    
    else:    
    
        # values
        strScanId = request.POST['txtDownScanId']
        logger.debug("strScanId=[" + strScanId + "]")
    
        # DAO
        sDao = SourceDao()

        # scan Object
        scanObj = sDao.selectScanObject(strScanId)
    
    
        # make folder & return file name dictionary
        fileDict = CommonUtil().f_getFileDict(strSessionId)

        # Get Folder Name    
        folderName = CommonUtil().f_getFolderName(fileDict, scanObj.meta_data_type)
        
        # Get File Name
        fileName = CommonUtil().f_getFileName(fileDict, scanObj) + ".nii"
        
        # Download
        if os.path.exists(folderName):
            response = HttpResponse(open(os.path.join(folderName, fileName), 'rb'), content_type="application/nii")
            response['Content-Disposition'] = 'attachment; filename=' + os.path.basename(fileName)
            return response
        else:
            context['errMsg'] = "Can't find .nii file."    
    

        return render(request, template_name, context)





#==============================================================================
#  Derive : selected json file info
#==============================================================================
def downloadJsonFile(request):
    
    # get JSON data
    jData = json.loads(request.body)

    # values
    strSessionId = jData['txtSessionId']
    strScanId = jData['txtScanId']

    # Dao
    sDao = SourceDao()

    # scan Object
    scanObj = sDao.selectScanObject(strScanId)

    # make folder & return file name dictionary
    fileDict = CommonUtil().f_getFileDict(strSessionId)

    # Get Folder Name    
    folderName = CommonUtil().f_getFolderName(fileDict, scanObj.meta_data_type)
    
    # Get File Name
    fileName = CommonUtil().f_getFileName(fileDict, scanObj) + ".json"

    # Get Json File Info
    brk = Brk2nii()
    dicJson = brk.getJsonFileInfo(folderName, fileName)
    
    dicJson['fileName'] = fileName

    return HttpResponse(json.dumps(dicJson), content_type="application/json")      
        




'''
##########################################################################################################
#  Experimental Design
##########################################################################################################
'''


#==============================================================================
#  Experimental Design Init
#==============================================================================
def edInit(request):
    
    template_name = 'experimentalDesign/ed.html'

    context = {
        'title' : 'Register Experimental Design',
        'subTitle1' : 'Register Keyword',
    }

    if 'initial_nm' not in request.session:
        template_name = 'member/signIn.html'
        context['errMsg'] = "Sign In First!!"
        
    else:

        # Dao
        eDao = EdDao()

        # get keyword list
        keyList = eDao.selectKeyList()
        context['keyList'] = keyList
    
    return render(request, template_name, context)



#==============================================================================
#  Experimental Design Key Choose
#==============================================================================
def edKeyChoose(request):

    template_name = 'experimentalDesign/ed.html'

    context = {
        'title' : 'Register Experimental Design',
        'subTitle1' : 'Register Keyword',
        'subTitle2' : 'Set Experimental Design Value',
    }

    if 'initial_nm' not in request.session:
        template_name = 'member/signIn.html'
        context['errMsg'] = "Sign In First!!"

    else:
        
        # Dao
        eDao = EdDao()

        # Set Dictionary
        dicEd = {}

        dicEd['edTitle'] = request.POST['txtEdTitle']
        dicEd['memberId'] = request.session.get("member_id")
        dicEd['regDate'] = CommonUtil().f_getDateTime()
        

        if 'txtEdId' in request.POST:
            strEdId = request.POST['txtEdId'].strip()
        
        if strEdId != "":
            dicEd['edId'] = request.POST['txtEdId']
            result = True
        else:
            # Insert [Experimental_Design]
            result = eDao.insertExperimentalDesign(dicEd)
        

        if result:
            
            # ED Title Change.
            chgTitle = request.POST['txtEdTitle']
            orgTitle = request.POST['txtEdTitleOrigin']
            logger.debug("@@ chgTitle:orgTitle ===" + chgTitle + ":" + orgTitle)
            
            if(chgTitle != orgTitle and orgTitle != ""):
                result = eDao.updateExperimentalDesignEdTitle(dicEd['edId'], chgTitle)
                if not result:
                    context['errMsg'] = "Change Title Error."
                
                
                
            
            # check: if ED is already linked with scan, you can't change ED.
            # Dao
            sDao = SourceDao()
            scanCnt = sDao.selectScanEDCount(dicEd['edId'])
            logger.debug("scanCnt ===[ %d ]", scanCnt)
            
            if scanCnt > 0:
                context['errMsg'] = "This ED is already linked, so you can't change."
            else:
                selectedKeyList = request.POST.getlist('chkKeyword')
                dicEd['selectedKeyList'] = selectedKeyList
            
                # Insert [Ed_Detail]
                result = eDao.insertEDDetail_Bulk(dicEd)

                if not result:
                    context['errMsg'] = "Register Fail. (BULK)"
        else:
            context['errMsg'] = "Register Fail!!"
        
        
        # get keyword list
        keyList = eDao.selectKeyList()
        context['keyList'] = keyList
        
        # get registered list
        regKeyList = eDao.selectEDDetailKeywordList(dicEd['edId'])
        context['regKeyList'] = regKeyList
        
        # get detail list
        detailList = eDao.selectEDDetailList(dicEd['edId'])
        context['detailList'] = detailList


        # setting context
        context['edId']    = dicEd['edId']
        context['edTitle'] = dicEd['edTitle']
    
    return render(request, template_name, context)




#==============================================================================
#  Experimental Design Key Value Modify
#==============================================================================
def edKeyValueModify(request):

    template_name = 'experimentalDesign/ed.html'

    context = {
        'title' : 'Register Experimental Design',
        'subTitle1' : 'Register Keyword',
        'subTitle2' : 'Set Experimental Design Value',
    }

    if 'initial_nm' not in request.session:
        template_name = 'member/signIn.html'
        context['errMsg'] = "Sign In First!!"

    else:
        
        # values
        strEdTitle = request.POST['txtEdTitle']
        strEdId = request.POST['txtEdId']


        # Dao
        eDao = EdDao()
        sDao = SourceDao()
        
        # check: if ED is already linked with scan, you can't change ED.
        scanCnt = sDao.selectScanEDCount(strEdId)
        logger.debug("scanCnt ===[ %d ]", scanCnt)
        
        if scanCnt > 0:
            context['errMsg'] = "This ED is already linked, so you can't change."
        else:

            # get detail list
            preDetailList = eDao.selectEDDetailList(strEdId)
            
            
            # set keyword name and value to Dictionary
            #    txtKey01 : txtKey + keyword_id
            failCnt = 0
            for detail in preDetailList:
                pk = detail['ID']
                inputKey = "txtKey_" + str(pk)
                 
                if inputKey in request.POST:
                    inputValue = request.POST[inputKey]
    
                    # update
                    result = eDao.updateEDDetailEdValue(pk, inputValue)
            
                    if not result:
                        failCnt = failCnt + 1
                        
            
            if failCnt > 0:
                context['errMsg'] = "Save Value fail." 

        
        # get keyword list
        keyList = eDao.selectKeyList()
        context['keyList'] = keyList
        
        # get registered list
        regKeyList = eDao.selectEDDetailKeywordList(strEdId)
        context['regKeyList'] = regKeyList

        # get detail list
        postDetailList = eDao.selectEDDetailList(strEdId)
        context['detailList'] = postDetailList
        
        # setting context
        context['edId'] = strEdId
        context['edTitle'] = strEdTitle
    
    return render(request, template_name, context)





#==============================================================================
#  Experimental Design List Search
#==============================================================================
def edList(request):

    template_name = 'experimentalDesign/edList.html'

    context = {
        'title' : 'Experimental Design',
    }



    if 'initial_nm' not in request.session:
        template_name = 'member/signIn.html'
        context['errMsg'] = "Sign In First!!"

    else:
 
        #---------------------------------------------------------------------
        #  get project list
        #---------------------------------------------------------------------
        #  get parameters
        if 'txtEdTitle' in request.POST:
            strEdTitle = request.POST['txtEdTitle']
            context['txtEdTitle'] = strEdTitle
        else:
            strEdTitle = ""
     
        if 'txtResearcherName' in request.POST:
            strResearcherName = request.POST['txtResearcherName']
            context['txtResearcherName'] = strResearcherName
        else:
            strResearcherName = ""
     
        if 'txtPage' in request.POST:
            strPage = request.POST['txtPage']
        else:
            strPage = 1


        logger.debug("## strEdTitle = [" + strEdTitle + "] strResearcherName = [" + strResearcherName + "]")
     
        # Dao
        eDao = EdDao()
    
        # get keyword list
        keyList = eDao.selectKeyList()
    
        
             
        # Get Project List
        context['from'] = 'edList'
        resultList = eDao.selectExperimentalDesignList(context)
         
        # Paginator
        paginator = Paginator(resultList, 20)
      
      
        try:
            resultList = paginator.page(strPage)
        except PageNotAnInteger:
            resultList = paginator.page(1)
        except EmptyPage:
            resultList = paginator.page(paginator.num_pages)
             
        # context setting
        context['keyList'] = keyList
        context['resultList'] = resultList

    return render(request, template_name, context)





#==============================================================================
#  Experimental Design List Search
#==============================================================================
def edListForJson(request):

    # get JSON data
    jData = json.loads(request.body)

    # values
    txtEdId = jData['txtEdId']
    txtEdTitle = jData['txtEdTitle']
    txtResearcherName = jData['txtResearcherName']

    # Dao
    eDao = EdDao()

    # context
    context = {}
    context['txtEdId'] = txtEdId
    context['txtEdTitle'] = txtEdTitle
    context['txtResearcherName'] = txtResearcherName

    # get ED list
    context['from'] = 'edListForJson'
    edList = eDao.selectExperimentalDesignList(context)
    
    return HttpResponse(json.dumps(edList), content_type="application/json")



 


#==============================================================================
#  Experimental Design Key List Search
#==============================================================================
def edKeyListForJson(request):

    # Dao
    eDao = EdDao()

    # get ED Key list
    key = eDao.selectKeyListWithComma()
    
    return HttpResponse(json.dumps(key), content_type="application/json")




#==============================================================================
#  Experimental Design Init (For modify)
#==============================================================================
def edModiInit(request):
    
    template_name = 'experimentalDesign/ed.html'

    context = {
        'title' : 'Register Experimental Design',
        'subTitle1' : 'Register Keyword',
        'subTitle2' : 'Set Experimental Design Value',
    }

    if 'initial_nm' not in request.session:
        template_name = 'member/signIn.html'
        context['errMsg'] = "Sign In First!!"
        
    else:

        # Dao
        eDao = EdDao()

        # get keyword list
        keyList = eDao.selectKeyList()
        context['keyList'] = keyList

        # get parameters
        strEdId  = request.POST['txtEdId']
        logger.debug("EdId ===[" + strEdId + "]")

        # get Experimental Design info
        edObj = eDao.selectExperimentalDesignObject(strEdId)
        context['edId']    = edObj.ed_id
        context['edTitle'] = edObj.ed_title     
        
        # get registered list
        regKeyList = eDao.selectEDDetailKeywordList(strEdId)
        context['regKeyList'] = regKeyList

        # get detail list
        postDetailList = eDao.selectEDDetailList(strEdId)
        context['detailList'] = postDetailList
        
    
    return render(request, template_name, context)




    
