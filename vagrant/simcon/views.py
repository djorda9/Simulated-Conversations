from django.shortcuts import render, render_to_response, redirect
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.template import RequestContext
from django.http import HttpResponse
from django.contrib.auth.models import User
from models import StudentAccess
from forms import StudentAccessForm
from forms import LoginForm
from models import Researcher
from models import Template
from django.views.generic import View
#import logging

#logger = logging.getLogger(__name__)

def Submission(request):
    return render(request, 'Student_Submission.html')

def Login(request):
    return render(request, 'Student_Login.html')
    
@permission_required('simcon.authLevel1')
def TemplateWizard(request):
    if request.POST:
        if request.POST.get('addVideoToPool'): # and request.POST['sbutton'] == "Add Video":  
            '''
            User has demanded to add a video to the pool in the left pane
            '''
            request.session['videos'].append(request.POST['new_video']) #TODO grab code from long youtube url
            request.session.modified = True
        elif request.POST.get('removeVideoFromPool'):
            '''
            User has demanded to delete a video from the pool in the left pane
            '''
            request.session['videos'].remove(request.POST['removeVideoFromPool'])
            request.session.modified = True
        elif request.POST.get('submit'):
            '''
            User has selected a video from the pool to use for a conversation
            '''
            # TODO should we catalog the first video selected?
            # TODO need to save existing options, video chains somehow
            selectedVideo = request.POST.get('submit')
            request.session['selectedVideo'] = selectedVideo # add to selected video TODO may need to confirm?
            # init options releated to this video, not sure if videos will be singular for sure in a conversation?
            request.session['responseOptions'] = ['Enter your option'] 
            request.session.modified = True
        elif request.POST.get('removeVideoResponse'):
            '''
            User has requested that the active video be removed
            '''
            #TODO clean up session of all things related to this video
            del request.session['selectedVideo']
            del request.session['responseOptions']
            request.session.modified = True
        elif request.POST.get('addoption'):
            '''
            User has requested to add a new option to the conversation
            '''
            #load responseOptions
            i = 1
            while request.POST.get('response%d' % i):  # cycle through existing options and load them into responseOptions
                request.session['responseOptions'][i-1] = request.POST.get('response%d' % i)
                i += 1
            request.session.modified = True
            request.session['responseOptions'].append('Enter your option') #add an option
            request.session.modified = True
        elif request.POST.get('removeResponse'):
            '''
            User has requested a response option be removed
            '''
            #load responseOptions
            i = 1
            while request.POST.get('response%d' % i):  # cycle through existing options and load them into responseOptions
                request.session['responseOptions'][i-1] = request.POST.get('response%d' % i)
                i += 1
            request.session.modified = True
            #TODO if response size < 2, don't do this
            res = request.POST.get('removeResponse')
            res = res.split(' ')
            res = int(res[-1])-1 # should be number of response to remove
            request.session['responseOptions'].pop(res) # remove this instance
            request.session.modified = True
        elif request.POST.get('addVideoToResponse'):
            '''
            User has requested that a video be added to this response option, involves redirecting the either video click
            '''
            #load responseOptions
            i = 1
            while request.POST.get('response%d' % i):  # cycle through existing options and load them into responseOptions
                request.session['responseOptions'][i-1] = request.POST.get('response%d' % i)
                i += 1
            request.session.modified = True
            res = request.POST.get('addVideoToResponse')
            res = res.split(' ')
            res = int(res[-1])-1 # should be number of response to remove
            return HttpResponse('add %d' % res)
        else:
            return HttpResponse("ill formed request")
    else:
        request.session['videos'] = [] # creating an empty list to hold our videos
        request.session['videos'].append('zJ8Vfx4721M')  # sample video
        request.session['videos'].append('IAISUDbjXj0')  #sample video
        request.session.modified = True
        
    return render(request, 'admin/template-wizard.html')

# This view is used to generate the url for the researcher to give to a student to allow the student to take
# the simulated conversation.  Note the Student Login page requires the validation key to be part of the url.  To
# generate the url there is a function in StudentAccess model that you pass the validation key and it returns
# the url with the validation key as part of the url.  You can pass the templateID to the view in the url and it.
# will auto select the passed templateID as the templateID.  To pass the templateID,
# add ?user_templateID=(insert templateID) to the end of the url for this view.
#The researcher has to select a template and set an expiration date for the link before the system will generate
# the link and store the templateID, researcherID, validationKey,and expirationDate for the link.
@permission_required('simcon.authLevel1')
def GenerateLink(request):
    link_url = None
    validation_key = None
    user_templateID = request.GET.get('user_templateID', -1)
    template = None
    current_user = get_researcher(request.user)
    if request.method == 'POST':
        form = StudentAccessForm(request.POST)
        if form.is_valid():
            template =form.cleaned_data['templateID']
            validation_key = User.objects.make_random_password(length=10)
            link = StudentAccess(templateID=template, researcherID = current_user,
                                validationKey = validation_key, expirationDate=form.cleaned_data['expirationDate'])
            link.save()
            link_url = link.get_link(validation_key)
            form = StudentAccessForm(initial = {'templateID':template}, researcher=current_user)

    else:
        if(user_templateID > -1):
            template = Template.objects.get(pk=user_templateID)
            form = StudentAccessForm(initial = {'templateID':template}, researcher=current_user)
        else:
            form = StudentAccessForm(researcher=current_user)
    return render_to_response('generate_link.html', {'link':link_url, 'key':validation_key, 'form':form},
                              context_instance = RequestContext(request))

# Returns the user object for the passed user
def get_researcher(current_user):
    researcher = Researcher.objects.get(user=current_user)
    return researcher


#  This view is used to display all the links generated by a researcher.
@permission_required('simcon.authLevel1')
def Links(request):
    researcher_links = StudentAccess.objects.filter(researcherID=get_researcher(request.user)).order_by('-studentAccessID')
    return render_to_response('links.html', {'researcher_links':researcher_links}, context_instance=RequestContext(request))

# Temporary Login Page
def login_page(request):
    message = None
    page = request.GET.get('next', None)
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username = username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    if page is not None:
                        return redirect(page)
                    else:
                        return render_to_response('login.html', context_instance=RequestContext(request))
                else:
                    message = "Your user is inactive"
            else:
                message = "Invalid username and/or password"
    else:
        form = LoginForm()
    return render_to_response('login.html',{'message':message, 'form':form},context_instance=RequestContext(request))

'''    
class TemplateView(View):
    def get(self, request, *args, **kwargs):
        return HttpResponse('This is GET request')

    def post(self, request, *args, **kwargs):
        return HttpResponse('This is POST request')
        

 from django.conf.urls import patterns, url

from myapp.views import MyView

urlpatterns = patterns('',
    url(r'^mine/$', MyView.as_view(), name='my-view'),
) # in urls
 
'''
#@permission_required('simcon.authLevel1')
#def UpdateVideos(request):
