from __future__ import unicode_literals
from django.db import models
from django.utils import timezone



YN_TYPE = (
     ('Y', 'YES')
     , ('N', 'NO')
)

USE_TYPE = (
     ('Y', 'USE')
     , ('N', 'NOT USE')
) 

AUTH_TYPE = (
     ('10', 'Common User')
     , ('99', 'Administrator')
)

DATA_TYPE = (
     ('C', 'Character')
     , ('I', 'Integer')
     , ('F', 'Float')
)

"""
==============================================
1. Common Table
==============================================
"""
class Code_Group(models.Model):
    group_id = models.CharField(max_length=3, primary_key=True)
    group_nm = models.CharField(max_length=30)

        
class Code(models.Model):
    group_id = models.ForeignKey(Code_Group, on_delete=models.CASCADE)
    code_id = models.CharField(max_length=2)
    code_nm = models.CharField(max_length=30)
    order_no = models.CharField(max_length=2)



"""
==============================================
2. Managing of Members
==============================================
"""
class Researcher(models.Model):
    
    id = models.CharField(max_length=20, primary_key=True)
    first_nm = models.CharField(max_length=50)
    last_nm = models.CharField(max_length=50)
    initial_nm = models.CharField(max_length=2)
    password = models.CharField(max_length=20)
    authority = models.CharField(max_length=2, default='10', choices=AUTH_TYPE)
    reg_date = models.DateTimeField()





"""
==============================================
3. Managing of Projects
==============================================
"""
class Project(models.Model):
 
    project_id = models.CharField(max_length=5, primary_key=True)
    initial_nm = models.CharField(max_length=2)
    year = models.CharField(max_length=4)
    animal_type = models.CharField(max_length=1)
    method_type = models.CharField(max_length=2)
    serial_no = models.CharField(max_length=3)
    project_aim = models.CharField(max_length=200)
    use_yn = models.CharField(max_length=1, default='Y', choices=USE_TYPE)
    reg_id = models.CharField(max_length=20, default='admin')
    reg_date = models.DateTimeField(default=timezone.now)


 
class Subject(models.Model):
 
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    subject_num = models.CharField(max_length=2)
    subject_nm = models.CharField(max_length=20)
    subject_cmt = models.CharField(max_length=100)
    use_yn = models.CharField(max_length=1, default='Y', choices=USE_TYPE)
    reg_id = models.CharField(max_length=20, default='admin')
    reg_date = models.DateTimeField(default=timezone.now)
    
    class Meta:
        unique_together = ('project', 'subject_num')



class Session(models.Model):
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    subject_num = models.CharField(max_length=2)
    session_num = models.CharField(max_length=2)
    session_nm = models.CharField(max_length=20, default='normal')
    session_cmt = models.CharField(max_length=100)
    source_id = models.CharField(max_length=8, blank=True, null=True)
    use_yn = models.CharField(max_length=1, default='Y', choices=USE_TYPE)
    reg_id = models.CharField(max_length=20, default='admin')
    reg_date = models.DateTimeField(default=timezone.now)
    
    class Meta:
        unique_together = ('project', 'subject_num', 'session_num')




"""
==============================================
4. Managing of Source
==============================================
"""
class Source(models.Model):

    source_id = models.CharField(max_length=8, primary_key=True)
    title = models.CharField(max_length=50)
    scan_yn = models.CharField(max_length=1, default='N', choices=YN_TYPE)
    scan_date = models.DateTimeField(blank=True, null=True)
    mapping_yn = models.CharField(max_length=1, default='N', choices=YN_TYPE)
    reg_id = models.CharField(max_length=20, default='admin')
    reg_date = models.DateTimeField(default=timezone.now)
    

class Scan(models.Model):

    source = models.ForeignKey(Source, on_delete=models.CASCADE)
    scan_num = models.CharField(max_length=2)
    pid_arr = models.CharField(max_length=20, blank=True, null=True)
    pid = models.CharField(max_length=2, blank=True, null=True)
    sch_slices = models.CharField(max_length=3, blank=True, null=True)
    sch_proto_nm = models.CharField(max_length=50, blank=True, null=True)
    sch_echo_time = models.CharField(max_length=10, blank=True, null=True)
    sch_repet_time = models.CharField(max_length=10, blank=True, null=True)
    sch_matrix = models.CharField(max_length=30, blank=True, null=True)
    sch_spat = models.CharField(max_length=3, blank=True, null=True)
    sch_n_repet = models.CharField(max_length=4, blank=True, null=True)
    meta_yn = models.CharField(max_length=1, default='N', choices=YN_TYPE)
    meta_data_type = models.CharField(max_length=1, blank=True, null=True)
    meta_acq = models.CharField(max_length=10, blank=True, null=True)
    meta_rec = models.CharField(max_length=10, blank=True, null=True)
    meta_task = models.CharField(max_length=10, blank=True, null=True)
    meta_run = models.CharField(max_length=2, blank=True, null=True)
    meta_suffix = models.CharField(max_length=2, blank=True, null=True)
    derive_yn = models.CharField(max_length=1, default='N', choices=YN_TYPE)
    reg_id = models.CharField(max_length=20, default='admin')
    reg_date = models.DateTimeField(default=timezone.now)
    
    class Meta:
        unique_together = ('source', 'scan_num')


"""
==============================================
5. Managing of Experimental Design
==============================================
"""

class ExperimentalDesign(models.Model):
    
    ed_id = models.CharField(max_length=6, primary_key=True)
    ed_title = models.CharField(max_length=30)
    reg_id = models.CharField(max_length=20, default='admin')
    reg_date = models.DateTimeField(default=timezone.now)


class EDDetail(models.Model):
    
    ed = models.ForeignKey(ExperimentalDesign, on_delete=models.CASCADE)
    detail_num = models.CharField(max_length=2)
    keyword_id = models.CharField(max_length=2, blank=True, null=True)
    ed_value = models.CharField(max_length=30, blank=True, null=True)
    use_yn = models.CharField(max_length=1, default='Y', choices=USE_TYPE)
    reg_id = models.CharField(max_length=20, default='admin')
    reg_date = models.DateTimeField(default=timezone.now)


class EDKeyword(models.Model):
    
    keyword_id = models.CharField(max_length=2, primary_key=True) 
    keyword_name = models.CharField(max_length=30)
    max_length = models.CharField(max_length=2)
    unit = models.CharField(max_length=3)
    data_type = models.CharField(max_length=1, default='C', choices=DATA_TYPE)
    sc_yn = models.CharField(max_length=1, default='N', choices=USE_TYPE)
    use_yn = models.CharField(max_length=1, default='Y', choices=USE_TYPE)

