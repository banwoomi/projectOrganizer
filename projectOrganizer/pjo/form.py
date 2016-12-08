from django import forms
from pjo.models import Source

YN_CHOICES = (('', '--CHOOSE--'), ('Y', 'YES'), ('N', 'NO'))


    
class SourceForm(forms.Form):
    
    txtTitle = forms.CharField(label="Folder Name", max_length=50)
    txtRegStart = forms.DateField(label="Registration Date", widget=forms.TextInput(attrs={'class':'datepicker'}))
    txtRegEnd = forms.DateField(widget=forms.TextInput(attrs={'class':'datepicker'}))
    selScanYn = forms.ChoiceField(label="Scan Y/N", choices=YN_CHOICES)
    txtScanStart = forms.DateField(label="Scan Date", widget=forms.TextInput(attrs={'class':'datepicker'}))
    txtScanEnd = forms.DateField(widget=forms.TextInput(attrs={'class':'datepicker'}))
   
    page = forms.CharField(widget=forms.HiddenInput())
    sourceId = forms.CharField(widget=forms.HiddenInput())
    init = forms.CharField(widget=forms.HiddenInput())

class SourceListForm(forms.Form):
    
    class Meta:
        model = Source
        fields = '__all__'
#         fields = ['a','b']
        
        
# required=True
# max_length=12
# min_length=12
# widget=forms.PasswordInput
# error_messages={'min_length':'minimum %(limit_value)d write please (now %(show_value)d letters'}



