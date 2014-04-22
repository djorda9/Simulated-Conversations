from django import forms
from django.contrib.auth.models import User
from models import Template
from django.utils.timezone import utc
import datetime, logging


logger = logging.getLogger("simcon") #global logger handler

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

class StudentAccessForm(forms.Form):

    templateID = forms.ModelChoiceField(queryset=Template.objects.all(), empty_label='Select a template',
                                        label="Template")
    expirationDate = forms.DateField(widget=forms.TextInput(attrs={'id':'datepicker'}), label="Expiration Date")
    
    playbackAudio  = forms.BooleanField(initial=True, required=False, label='Playback audio?') 
    
    playbackVideo  = forms.BooleanField(initial=True, required=False, label='Playback video?')
    
    collectEmail = forms.BooleanField(initial=True, required=False, label='Collect Email?')
    
    allowTypedResponse = forms.BooleanField(initial=False, required=False, label='Allow student to end conversation with a typed response?')

    def __init__(self, *args, **kwargs):
        self.researcher = kwargs.pop('researcher',None)
        self.user_template = kwargs.pop('templateID',None)
        #rawaudio = args[0]['playbackAudio']#kwargs.pop('playbackAudio', None)
        #logger.info("playback in form is %s" % rawaudio)
        super(StudentAccessForm, self).__init__(*args, **kwargs)
        #self.playbackAudio = False
        if self.researcher > 0:
            self.fields['templateID'] = forms.ModelChoiceField(queryset=Template.objects.filter
                                        (researcherID=self.researcher).filter(deleted=0),
                                            empty_label='Select a template', label="Template")
    def clean_expirationDate(self):
        date = self.cleaned_data['expirationDate']
        todayDate = datetime.date.today()
        if date < todayDate:
            raise forms.ValidationError("The date cannot be in the past!")
        return date

class ShareResponseForm(forms.Form):
    researcherID = forms.ModelChoiceField(queryset=User.objects.all(), empty_label='Select a researcher',
                                          label="Researcher")

    def __init__(self, *args, **kwargs):
        self.researcher = kwargs.pop('researcher',None)
        super(ShareResponseForm, self).__init__(*args, **kwargs)
        if self.researcher > 0:
            self.fields['researcherID'] = forms.ModelChoiceField(queryset=User.objects.exclude(id=self.researcher.id),
                                                                 empty_label='Select a researcher', label="Researcher")

class ShareTemplateForm(forms.Form):
    templateID = forms.ModelChoiceField(queryset=Template.objects.all(), empty_label='Select a conversation template',
                                        label="Template")
    researcherID = forms.ModelChoiceField(queryset=User.objects.all(), empty_label='Select a researcher',
                                          label="Researcher")


    def __init__(self, *args, **kwargs):
        self.researcher = kwargs.pop('researcher',None)
        super(ShareTemplateForm, self).__init__(*args, **kwargs)
        if self.researcher > 0:
            self.fields['researcherID'] = forms.ModelChoiceField(queryset=User.objects.exclude(id=self.researcher.id),
                                                                 empty_label='Select a researcher', label="Researcher")
            self.fields['templateID'] = forms.ModelChoiceField(queryset=Template.objects.filter
                                        (researcherID=self.researcher).filter(deleted=0),
                                            empty_label='Select a conversation template', label="Template")
