from django.conf.urls import url
from . import views


app_name = "pjo"

urlpatterns = [

    # main
    url(r'^$', views.pjoInit, name='index'),


    # about JOIN
    url(r'^join/form$', views.joinInit, name='joinForm'),
    url(r'^join/check$', views.joinCheck, name='joinCheck'),
    url(r'^join/$', views.joinMember, name='join'),

    # about SIGN IN
    url(r'^signin/form$', views.signInit, name='signinForm'),
    url(r'^signin/$', views.signinPjo, name='signin'),
    url(r'^signout/$', views.signoutPjo, name='signout'),

    # about Profile
    url(r'^profile/$', views.profileInit, name='profileForm'),
    url(r'^profile/update$', views.profileUpdate, name='profile'),
    

    #-----------------------------------------------------------------------------------
    # about Project
    url(r'^project/$', views.projectInit, name='projectForm'),
    url(r'^prjList/$', views.projectList, name='projectList'),
    url(r'^pjtDetail/(?P<project_id>[0-9]+)$', views.projectDetail, name='projectDetail'),
    url(r'^prjRegi/$', views.projectRegister, name='projectRegister'),
    url(r'^pjtModi/$', views.projectModify, name='projectModify'),

    # about Subject
    url(r'^subList/$', views.subjectList, name='subjectList'),
    url(r'^subRegi/$', views.subjectRegister, name='subjectRegister'),
    url(r'^subModi/$', views.subjectModify, name='subjectModify'),

    # about Session
    url(r'^ssnList/$', views.sessionList, name='sessionList'),
    url(r'^ssnRegi/$', views.sessionRegister, name='sessionRegister'),
    url(r'^ssnModi/$', views.sessionModify, name='sessionModify'),

    url(r'^ssnCopy/(?P<project_id>[0-9]+)/(?P<subject_id>[0-9]+)$', views.sessionCopyForm, name='sessionCopyForm'),
    url(r'^chgGrp/$', views.changeSubject, name='changeSubject'),
    url(r'^ssnSave/$', views.sessionCopySave, name='sessionCopySave'),
    
    #-----------------------------------------------------------------------------------
    # about Source
    url(r'^srcInit/$', views.sourceInit, name='sourceInit'),
    url(r'^srcList/$', views.sourceList, name='sourceList'),
    url(r'^addSrc/$', views.addNewSource, name='addNewSource'),
    
    # about Scan
    url(r'^scanList/$', views.scanList, name='scanList'),

    #-----------------------------------------------------------------------------------
    # about Mapping
    url(r'^mapInit/$', views.mapInit, name='mapInit'),
    url(r'^mapSrcList/$', views.mapSourceList, name='mapSourceList'),
    url(r'^mapScList/$', views.mapAjaxScanList, name='mapAjaxScanList'),
    url(r'^mapMapping/$', views.mapMapping, name='mapMapping'),
    url(r'^metaInit/$', views.metaInit, name='metaInit'),
    url(r'^metaCode/$', views.metaCode, name='metaCode'),
    url(r'^metaSave/$', views.metaSave, name='metaSave'),

    url(r'^downFile/$', views.downloadSingleFile, name='downloadSingleFile'),
    url(r'^downJson/$', views.downloadJsonFile, name='downloadJsonFile'),

    #-----------------------------------------------------------------------------------
    # other module
    # checkscan
    url(r'^checkScan/$', views.checkScan, name='checkScan'),
    # brk2nii
    url(r'^derive/$', views.derive, name='derive'),
    
    #-----------------------------------------------------------------------------------
    # about Experimental Design
    url(r'^edInit/$', views.edInit, name='edInit'),
    url(r'^edKChs/$', views.edKeyChoose, name='edKeyChoose'),
    url(r'^edKModi/$', views.edKeyValueModify, name='edKeyValueModify'),

    url(r'^edList/$', views.edList, name='edList'),
    url(r'^edListJ/$', views.edListForJson, name='edListForJson'),
    url(r'^edKListJ/$', views.edKeyListForJson, name='edKeyListForJson'),

    url(r'^edMdInit/$', views.edModiInit, name='edModiInit'),


]