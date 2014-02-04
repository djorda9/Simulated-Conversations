from django import forms
from models import StudentAccess
from models import Template
from models import Researcher
from models import Response
from models import Conversation


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

class StudentAccessForm(forms.Form):

    templateID = forms.ModelChoiceField(queryset=Template.objects.all(), empty_label='Select a template')
    expirationDate = forms.DateField(widget=forms.TextInput(attrs={'id':'datepicker'}))

    def __init__(self, *args, **kwargs):
        self.researcher = kwargs.pop('researcher',None)
        self.user_template = kwargs.pop('templateID',None)
        super(StudentAccessForm, self).__init__(*args, **kwargs)
        if self.researcher > 0:
            self.fields['templateID'] = forms.ModelChoiceField(queryset=Template.objects.filter
                                        (researcherID=self.researcher), empty_label='Select a template')

class ShareResponseForm(forms.Form):
    researcherID = forms.ModelChoiceField(queryset=Researcher.objects.all(), empty_label='Select a researcher')

    def __init__(self, *args, **kwargs):
        self.researcher = kwargs.pop('researcher',None)
        super(ShareResponseForm, self).__init__(*args, **kwargs)
        if self.researcher > 0:
            self.fields['researcherID'] = forms.ModelChoiceField(queryset=Researcher.objects.exclude(user=self.researcher),empty_label='Select a researcher')

class ShareTemplateForm(forms.Form):
    researcherID = forms.ModelChoiceField(queryset=Researcher.objects.all(), empty_label='Select a researcher')
    templateID = forms.ModelChoiceField(queryset=Template.objects.all(), empty_label='Select a conversation template')

    def __init__(self, *args, **kwargs):
        self.researcher = kwargs.pop('researcher',None)
        super(ShareTemplateForm, self).__init__(*args, **kwargs)
        if self.researcher > 0:
            self.fields['researcherID'] = forms.ModelChoiceField(queryset=Researcher.objects.exclude(user=self.researcher),empty_label='Select a researcher')
            self.fields['templateID'] = forms.ModelChoiceField(queryset=Template.objects.filter
                                        (researcherID=self.researcher), empty_label='Select a conversation template')