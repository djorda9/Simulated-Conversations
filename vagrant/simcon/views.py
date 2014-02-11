from django.shortcuts import render, render_to_response, redirect
from django.contrib.auth.decorators import permission_required
from django.contrib.auth import authenticate, login
from django.template import RequestContext
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.db import transaction, IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime
from models import StudentAccess
from forms import StudentAccessForm
from forms import ShareTemplateForm
from forms import LoginForm
from forms import ShareResponseForm
from models import Response
from models import Researcher
from models import Template
from models import PageInstance
from models import TemplateFlowRel
from models import SharedResponses
from models import Conversation
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
        form = StudentAccessForm(request.POST, researcher=current_user)
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
    researcher_links = StudentAccess.objects.filter(researcherID=get_researcher(request.user)).\
                        order_by('-studentAccessID')
    return render_to_response('links.html', {'researcher_links':researcher_links},
                              context_instance=RequestContext(request))

# This view is used to share a template with another researcher.
@permission_required('simcon.authLevel1')
def ShareTemplate(request):
    user_templateID = request.GET.get('user_templateID', -1)
    current_user = get_researcher(request.user)
    researcher_userId = None

    #A list of pageInstanceStruct for storing the old and new PageInstance used when coping the
    #TemplateFlowRel
    old_new_pages = []
    if request.method == 'POST':
        form = ShareTemplateForm(request.POST, researcher=current_user)
        if form.is_valid():
            researcher = form.cleaned_data['researcherID']
            template = form.cleaned_data['templateID']

            try:
                with transaction.atomic():
                    #Copy information in template table to the researcher selected.
                    copied_template = Template(researcherID=researcher, shortDesc=template.shortDesc, deleted=False,
                                               firstInstanceID=template.firstInstanceID)
                    copied_template.save()

                    #Copies each PageInstance associated with the selected template.
                    pages = PageInstance.objects.filter(templateID=template)
                    for page in pages:
                        temp = PageInstance(templateID=copied_template, videoOrResponse=page.videoOrResponse,
                                            videoLink=page.videoLink, richText=page.richText,
                                            enablePlayback=page.enablePlayback)
                        temp.save()
                        new_old = pageInstanceStruct(old=page, new=temp)
                        old_new_pages.append(new_old)

                    #Copies each TemplateFlowRel associated with the selected template.
                    flow = TemplateFlowRel.objects.filter(templateID=template)
                    for old in flow:
                        current_page = old.pageInstanceID
                        next_page = old.nextPageInstanceID

                        for i in old_new_pages:
                            oldId =  i.get_old()
                            if oldId.pageInstanceID==current_page.get_pageInstanceID():
                                current_page = i.newPageInstance
                            if next_page <> None:
                                if oldId.pageInstanceID==next_page.get_pageInstanceID():
                                    next_page = i.newPageInstance

                        temp = TemplateFlowRel(templateID=copied_template, pageInstanceID=current_page,
                                               nextPageInstanceID=next_page)
                        temp.save()

                        #Updates the copied template's firstInstance with the copied firstInstance
                        if old.templateFlowRelID==copied_template.firstInstanceID.templateFlowRelID:
                            copied_template.firstInstanceID = temp
                            copied_template.save()

                    form = ShareTemplateForm(researcher=current_user)
                    researcher_userId = researcher.user.get_full_name()

            except ValueError as e:
                failed = "Required data is missing in database in order to copy the template."
                return render_to_response('share_template.html',
                                          {'failed':failed, 'form':form}, context_instance = RequestContext(request))
    else:
        if(user_templateID > -1):
            template = Template.objects.get(pk=user_templateID)
            form = ShareTemplateForm(initial = {'templateID':template}, researcher=current_user)
        else:
            form = ShareTemplateForm(researcher=current_user)
    return render_to_response('share_template.html', {'success':researcher_userId,
                                                      'form':form}, context_instance = RequestContext(request))

# This view is used to share a response with another researcher.  To pass the responseID, add ?responseID=[responseID]
# to end of the url.
@permission_required('simcon.authLevel1')
def ShareResponse(request):
    user_responseID = request.GET.get('responseID', -1)
    current_user = get_researcher(request.user)
    form = None
    success = None
    failed = None
    sharedWith = None
    if(user_responseID < 0):
        failed = "The ResponseID was not provided."
    else:
        try:
            user_response = Response.objects.get(pk=user_responseID)
        except ObjectDoesNotExist as e:
            failed = "The ResponsedID was not found!"
        if failed is None:
            conversation = Conversation.objects.get(pk=user_response.conversationID.id)
            conversation_researcher = get_researcher(conversation.researcherID)
            if current_user.user==conversation_researcher.user:
                if request.method == 'POST':
                    form = ShareResponseForm(request.POST, researcher=current_user)
                    if form.is_valid():
                        researcher = form.cleaned_data['researcherID']
                        if user_response == None:
                            failed = "The ResponseID that was supplied is invalid."
                        else:
                            shared = SharedResponses(responseID=user_response, researcherID=researcher,
                                                     dateTimeShared=datetime.now())
                            try:
                                shared.save()
                            except IntegrityError as e:
                                sharedWith = SharedResponses.objects.filter(responseID=user_responseID).\
                                    order_by('researcherID')
                                failed = "The response has already been shared with " + researcher.user.get_full_name()
                                return render_to_response('share_response.html', {'success':success, 'failed':failed,
                                        'shared':sharedWith, 'form':form}, context_instance = RequestContext(request))

                            sharedWith = SharedResponses.objects.filter(responseID=user_responseID).\
                                order_by('researcherID')
                            success = researcher.user.get_full_name()
                else:
                    sharedWith = SharedResponses.objects.filter(responseID=user_responseID).order_by('researcherID')
                    form = ShareResponseForm(researcher=current_user)
            else:
                failed = "You do not have permission to share this response"

    return render_to_response('share_response.html', {'success':success, 'failed':failed, 'shared':sharedWith,
                                                      'form':form}, context_instance = RequestContext(request))

# Holds the PageInstance being copied and the PageInstance that was copied.
class pageInstanceStruct(object):
    oldPageInstance = None
    newPageInstance = None

    def __init__(self, *args, **kwargs):
        old = kwargs.pop('old',None)
        new = kwargs.pop('new',None)
        self.oldPageInstance = old
        self.newPageInstance = new

    def get_old(self):
        return self.oldPageInstance

    def get_new(self):
        return self.newPageInstance



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
