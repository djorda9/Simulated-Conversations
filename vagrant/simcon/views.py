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
from django.template import loader, Context
from models import PageInstance
import datetime
#import logging
from django.core.context_processors import csrf #csrf
#from django.shortcuts import render_to_response #csrf

#used in video link processessing: regular expressions
import re

import logging
logger = logging.getLogger("simcon")

from django import forms # for forms
from django.core.urlresolvers import reverse
from tinymce.widgets import TinyMCE
from tinymce.models import HTMLField  # tinymce for rich text embeds

#for template insertions
from simcon.models import Template, PageInstance, TemplateResponseRel, TemplateFlowRel, Researcher
from django.contrib.auth.models import User


def StudentVideoInstance(request):
    # Get the template ID(TID), Page Instance ID(PIID), and Validation Key(ValKey) as  variables from the url (see urls.py)
    # Check tID against template table. Check piID against piID of template, and valKey from StudentAccess table
    try:
        templ = Template.objects.get(templateID = TID)
    except Template.Invalid:
        print "Template ID is invalid"

    try:
        page = PageInstance.objects.get(pageInstanceID = PIID, templateID = TID)
    except PageInstance.Invalid:
        print "Page Instance ID is invalid"

    try:
        #possible case: someone changes validation key to a different validation key, would still succeed
        valid = StudentAccess.objects.get(validationKey = VKey)
    except StudentAccess.Invalid:
        print "Validation Key is invalid"

    # if student name/email exist, then update the Conversation model
    try:
        # if we can get the conversation, then don't save a new instance of this conversation
        conv = Conversation.objects.get(templateID = TID, StudentName = SName)
    except Conversation.Invalid:
        print "conversation doesn't exist"
        #conv = Conversation.objects.get(templateID = TID, StudentName = SName)

    #create context variables for video web page
    vidLink = page.videoLink
    text = page.richText
    playback = page.enablePlayback
    #try to find the next page, if it exists. Get it's PIID so we know where to go after this page.
    #otherwise, set PIID to 0. this will make this page end up at the Student Submission page.
    try:
        nextpage = TemplateFlowRel.objects.get(pageInstanceID = PIID)
        newPID = nextpage.nextPageInstanceID
    except TemplateFlowRel.Invalid:
        print "could not find next page"

    # there are ways to compact this code, but this is the most explicit way to render a template
    t = loader.get_template('Student_Video_Response.html')
    c = Context({
    'vidLink': vidLink,
    'text': text,
    'playback': playback,
    'newPID': newPID,
    'ValKey': VKey,
    'TID': TID,
    'message': 'I am the Student Video Response View.'
    })
    return t.render(c)

def StudentResponseInstance(request):
    # Get the template ID(TID), Page Instance ID(PIID), and Validation Key(ValKey) as  variables from the url
    # Check tID against template table. Check piID against piID of template, and valKey from StudentAccess table
    try:
        templ = Template.objects.get(templateID = TID)
    except Template.Invalid:
        print "Template ID is invalid"

    try:
        pi = PageInstance.objects.get(pageInstanceID = PIID, templateID = TID)
    except PageInstance.Invalid:
        print "Page Instance ID is invalid"

    try:
        valid = StudentAccess.objects.get(validationKey = VKey)
    except StudentAccess.Invalid:
        print "Validation Key is invalid"

    #create a list for all of the possible response options
    responses = []

#we need to figure out what te responses are so that the student can choose one of them, prompting the rendering of the appropriate video page
    for i in range(1,10):
        try:
            tempObject = TemplateResponseRel.objects.get(templateID = TID, pageInstanceID = PIID, optionNumber = (i-1))
            responses.append(tempObject.responseText)
        except TemplateResponseRel.Invalid:
            responses.append("NA")

	#upload to Responses table which PageInstanceID we're at with the current datetime. If all values already exist but the timedate is different,
    # then the page was refreshed, display an error, and after a few seconds go to beginning of conversation
    try:
        conv = Conversation.objects.get(templateID = TID, studentName = SName)
    except TemplateResponseRel.Invalid:
        print "no conversation for this response"
    #something like this needs to be submitted in a form
	#T = Response(pageInstanceID=PIID, conversationID = conv.PK, order = ?, choice = ?, audioFile = ?)
    #T.save()

    t = loader.get_template('Student_Text_Response.html')
    c = Context({
    'responses': responses,
    'ValKey': VKey,
    'TID': TID,
    'conv': conv,
    'message': 'I am the Student Text Response View.'
    })
    return t.render(c)

def Submission(request):
    return render(request, 'Student_Submission.html')

#when the student submits their name and optional email, this updates the database
def StudentInfo(request):
    if request.method == 'POST':
        form = StudentNameForm(request.POST)
        if form.is_valid():
            studentname = form.cleaned_data['SName']
            studentemail = form.cleaned_data['SEmail']

            T = Conversation(template=TID, researcherID = TID.researcherID, studentName = studentname, studentEmail = studentemail, dateTime = datetime.datetime.strptime(datetime.datetime.now(), "%Y-%m-%d %H:%M"))
            T.save()
#what is this line for?
            form = StudentInfoForm()

    return render_to_response('Student_Login.html', {'form':form},
                              context_instance = RequestContext(request))

#when the student chooses the text answer to their response, this updates the database with their choice
def StudentTextChoice(request):
    if request.method == 'POST':
        form = StudentTextChoiceForm(request.POST)
        if form.is_valid():
            studentchoice = form.cleaned_data['StudentChoice']
#what is this line for?
            form = StudentTextChoiceForm()

    #figure out newPID from the studentchoice
    #lookup template from TID, search through TemplateResponseRel for optionNum, return nextPageInstanceID as nextPID?
    return render_to_response('Student_Text_Response.html')

def StudentLogin(request):
    try:
        access = StudentAccess.objects.get(validationKey = VKey)
    except StudentAccess.Invalid:
        print "Validation Key is invalid"

    convo_Expiration = access.expirationDate
    currentdate = datetime.datetime.now()
    #On other option that is cleaner is to pass the current time and expiration to the template, and have an if statement in the template
    if(currentdate < convo_Expiration):
        try:
            template = Template.objects.get(TemplateID = access.templateID)
        except StudentAccess.Invalid:
            print "template doesn't exist"

        pageInstance = template.firstInstanceID

        try:
            nextPage = PageInstance.objects.get(pageInstanceID = pageInstance)
        except StudentAccess.Invalid:
            print "first page instance doesn't exist"

        t = loader.get_template('Student_Login.html')
        c = Context({
        'TID': template,
        'PIID': pageInstance,
        'ValKey': VKey,
        'VoR': nextPage.videoOrResponse,
        'message': 'I am the Student Login View.'
        })
        return t.render(c)
    else:
        print "Conversation link has expired"
   

# class for rich text field in a form
class RichTextForm(forms.Form):
    richText = forms.CharField(widget=TinyMCE(attrs={'cols': 80, 'rows': 10}))

#For researchers: edit conversation templates 
# or create a new one.

@permission_required('simcon.authLevel1')
def TemplateWizard(request):
    c = {}
    c.update(csrf(request))
    if request.POST:
        if request.POST.get('saveTemplateButton'):
            #variables to translate into db:
              #request.session['videos']               <-- array of videos in the pools
              #request.session['responseText']                 <-- these 3 are all associated by id
              #request.session['responseChildVideo']           <--
              #request.session['responseParentVideo']          <--
              #request.POST.get('conversationTitle')
              #request.session['enablePlayback']       <-- True or False

            #logger.info("Inserting conversation into database")

            #TODO check if values are valid   --- note, the values should all be valid already, due to how we implemented the jQuery add functions. -nm
               #if not, send back to edit page and display errors

            #TODO check if conversation already existed  --- we should maybe have a "edittingTemplate" variable that is set when you open the edit page -nm
               #if yes, check if associated with responses/shared responses
               #if yes, save as new version
            '''
            Storing session variables into the database template mappings
            '''
            temp = Template(researcherID = Researcher.objects.get(user=request.user), 
                             shortDesc   = request.POST.get('conversationTitle')) # NOTE: need firstInstanceID (TemplateFlowRel), added retroactively
            
            temp.save() # need this to create id
            pageInstances = []
            templateResponseRels = []
            templateFlowRels = []
            errorMessages = []
           
            #this is how we will know which video comes first in the relationships
            possibleVideoHeads = []
            for vid in request.session['videos']:
               possibleVideoHeads.append(vid)
            
            # build up structure in models
            # first create page instance entries for all videos in pool
            for i, vid in enumerate(request.session['videos']):
                enabPlayback = False
                if vid in request.session['enablePlayback']:
                    enabPlayback = True
                
                #add the page instance for this video
                pageInstances.append(PageInstance(templateID = temp.templateID,
                                                   videoOrResponse = "video",
                                                   videoLink = vid,
                                                   richText = request.session['richText/%s' % vid],
                                                   enablePlayback = enabPlayback
                                                   ))
                pageInstances[-1].save()
            #now all the videos have pageInstanceIDs

            #next, for each video, 
            for i, vid in enumerate(request.session['videos']):     
                #the pageInstances should correspond to the session videos by id at this point.
                #so only keep track of the responses that match this parent video (vid)
                numberOfResponses = 0
                #loop through each of the responses....                         
                # note that the following three values can be accessed by res[0], res[1], res[2]
                for j, res in enumerate(zip(request.session['responseText'],request.session['responseParentVideo'],request.session['responseChildVideo'])):
                    # ...that match the video 
                    if res[1] == vid:
                        numberOfResponses += 1
                        #..and if this is the first one so far,
                        if numberOfResponses == 1:
                            #create a page instance for this group of responses.
                            pageInstances.append(PageInstance(templateID = temp.templateID,
                                                      videoOrResponse = "response",
                                                      videoLink = "",
                                                      richText = "",
                                                      enablePlayback = False
                                                      ))
                            responsesPageInstanceID = pageInstances[-1].pageInstanceID
                            pageInstances[-1].save()
                            #link the parents pageInstance entry to the one we just created
                            pageInstanceMatchesVideo = pageInstances[i].pageInstanceID
                            templateFlowRels.append(TemplateFlowRel(templateID = temp.templateID,
                                                         pageInstanceID = pageInstanceMatchesVideo,
                                                         nextPageInstanceID = responsesPageInstanceID
                                                         ))
                            templateFlowRels[-1].save()
                        #since a parent video references this child video, remove it from possible video heads
                        possibleVideoHeads.remove(res[2])
                        # find the ID of the pageInstance that matches responseChildVideo[j]
                        # unless its "endpoint", then just insert "endpoint"
                        if res[2] == "endpoint":
                            insertNextPageInstanceID = "endpoint"
                        else:
                            for k,vid2 in enumerate(request.session['videos']):
                                if vid2 == res[2]:
                                    insertNextPageInstanceID = pageInstances[k].pageInstanceID
                        #begin adding the responses into the templateResponseRels 
                        templateResponseRels.append(TemplateResponseRel(templateID = temp.templateID,
                                                         pageInstanceID = responsesPageInstanceID,
                                                         responseText = res[0],
                                                         optionNumber = numberOfResponses,
                                                         nextPageInstanceID = insertNextPageInstanceID         
                                                         ))
                        templateResponseRels[-1].save()
                
            #by now, there should be only one video head if the flow was built correctly.
            if len(possibleVideoHeads) > 1:
                #if not, produce an error message and go back to template editor.
                errorMessages.append("There was no video in the conversation flow that appeared to go first. Make sure the videos in the pool all link to something.")
            #if you want to insert more errors, do it here.
            else:
                #get the pageInstance that references this first video
                firstPageID = pageInstances[pageInstances.index(possibleVideoHeads[0])]
                #insert this video as the templates firstInstanceID
                temp.firstInstanceID = firstPageID
                temp.save()
                #TODO map these arrays to the actual db -- should already be done by save() -nm
                #TODO print success message
                #TODO provide link back to main page
                return HttpResponse("Success")#render(request, 'admin/template-wizard-submission.html')
        elif request.POST.get('editExistingTemplate'):
            #logger.info("loading existing template")
            #prepopulate session variables and then reload page
#            '''
#            User has selected a video from the pool to use for a conversation
#            '''
#            # TODO should we catalog the first video selected?
#            # TODO need to save existing options, video chains somehow
#            selectedVideo = request.POST.get('submit')
#            request.session['selectedVideo'] = selectedVideo # add to selected video TODO may need to confirm?
#            # init options releated to this video, not sure if videos will be singular for sure in a conversation?
#            request.session['responseOptions'] = ['Enter your option'] 
#            request.session.modified = True
            return render(request, 'admin/template-wizard.html')

        else:
            return HttpResponse("ill formed request")
    else:
        # set up the session variables:
         # if session variables exist, dont do anything
         # THIS IS ACTUALLY DONE ABOVE: if they are editing the template, pre-poopulate the session vars
           # save the old id in a var
         # if its new, do the following....
        
        # DATA MODEL:
        request.session["selectedVideo"] = "" # the currently selected video to edit
        request.session['videos'] = [] # creating an empty list to hold our videos in the pool
        # django doesn't appear to support multidimensional arrays in session variables.
        # so, the best way I could think to add correlating responses under each video,
        # is to add a responseText, and at the same time add the responseParentVideo that it 
        # corresponds to. The id's should match up, so to find all responses that link to a video,
        # loop though responseParentVideo until you find it, and reference that id in responseText. 
        # Same goes for all the responseChildVideo's it links to. -nate
        request.session['responseText'] = [] #create an empty list to hold responses text
        request.session['responseParentVideo'] = [] #create an empty list to hold responses video (like a foreign key)
        request.session['responseChildVideo'] = []
        request.session['enablePlayback'] = [] #if the video exists in this list, enable playback.
        request.session['videos'].append('zJ8Vfx4721M')  # sample video
        request.session['videos'].append('DewJHJlYOIU') #sample 
        request.session.modified = True

        return render(request, 'admin/template-wizard.html')

#This is the "behind the scenes" stuff for the template wizard above
@permission_required('simcon.authLevel1')
def TemplateWizardUpdate(request):
    c = {}
    c.update(csrf(request))
    if request.POST:
        if request.POST.get('new_video'):
            '''
            User has demanded to add a video to the pool in the left pane
            '''
            videoCode = re.match(r'.*?v=([^&]*)&?.*', request.POST['new_video'], 0)
            videoCode = videoCode.group(1) # just pertinent code
            if videoCode and videoCode not in request.session['videos']:
                request.session['videos'].append(videoCode)
                request.session['enablePlayback'].append(videoCode)
                request.session.modified = True
            else:
              print "Invalid video link." #TODO make this echo properly back to user
        elif request.POST.get('removeVideoFromPool'):
            '''
            User has demanded to delete a video from the pool in the left pane
            '''
            removeVideo = request.POST.get('removeVideoFromPool')
            if removeVideo:
                del request.session['richText/%s' % removeVideo] #TODO remove any rich text saved in session
                if removeVideo == request.session['selectedVideo']:
                    request.session['selectedVideo'] = ""
                request.session['videos'].remove(removeVideo)
                #TODO delete all associated responses
                request.session.modified = True
        elif request.POST.get('editVideo'):
            '''
            User selected a video to edit. Populate the right pane.
            '''
            #TODO check if we have unsaved right pane data
            editVideo = request.POST.get('editVideo')
            request.session['selectedVideo'] = editVideo
            richText = request.session.get('richText/%s' % editVideo)
            #if richText: # some data for the rich text exists
                #tinyMCE.activeEditor.setContent(richText) 
            request.session.modified = True;
        #elif request.POST.get('saveVideo'):
            #'''
            #Save the video page that is being edited
            #'''
            #TODO save some video attributes.....
            #logger.info("video saving")
            #request.session.selectedVideo = ""
            #request.session.modified = True;
        elif request.POST.get('addResponse'):
            '''
            Add a response to the right pane
            '''
            request.session["responseText"].append(request.POST["addResponseText"])
            request.session["responseParentVideo"].append(request.POST["addResponseParentVideo"])
            request.session["responseChildVideo"].append(request.POST["addResponseChildVideo"])
            request.session.modified = True
        elif request.POST.get('removeResponse'):
            '''
            Remove a response from the right pane
            '''
            index = int(request.POST["removeResponseId"])
            request.session["responseText"].pop(index)
            request.session["responseParentVideo"].pop(index)
            request.session["responseChildVideo"].pop(index)
            request.session.modified = True
        elif request.POST.get('saveVideoPage'):
            '''
            User requested to save a video page's richtext
            '''
            # TODO get this working
            #logger.info("content from richtext was %s" % request.POST.get('mce'))
            request.session['richText/%s' % request.session['selectedVideo']] = request.POST.get('mce') # push current tinymce into session
            request.session.modified = True
        elif request.POST.get('enablePlayback'):
            '''
            User selected to Enable/disable playback on youtube video
            '''
            #I think this now works -Nick
            if request.session['selectedVideo'] not in request.session['enablePlayback']:
              request.session["enablePlayback"].append(request.session['selectedVideo'])
            else:
              request.session["enablePlayback"].remove(request.session['selectedVideo'])
            request.session.modified = True               
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
        logger.error("No post data")
        return HttpResponse("no POST data")
    return HttpResponse("null")
'''

#Reload the template wizards left pane if requested
@permission_required('simcon.authLevel1')
def TemplateWizardLeftPane(request):
    c = {}
    c.update(csrf(request))
    return render(request, 'admin/template-wizard-left-pane.html')

#Reload the template wizards right pane if requested
@permission_required('simcon.authLevel1')
def TemplateWizardRightPane(request):
    c = {}
    c.update(csrf(request))
    
    selVideo = request.session.get('selectedVideo')
    if selVideo:
        key = 'richText/%s' % selVideo
        if request.session.get(key): # we have richText to populate
            widge = RichTextForm({'richText': request.session[key]}) # preload with the value
            return render(request, 'admin/template-wizard-right-pane.html', {'widge':widge, 'videoRichText': request.session[key]})
            
    widge = RichTextForm()        
    return render(request, 'admin/template-wizard-right-pane.html', {'widge': widge})
'''
urlpatterns = patterns('',
    url(r'^mine/$', MyView.as_view(), name='my-view'),
) # in urls
 '''

'''
#@permission_required('simcon.authLevel1')
#def UpdateVideos(request):


@permission_required('simcon.authLevel1')
def Responses(request, RID):
	current_user = get_researcher(request.user)
	try:
		ConversationToGet=Conversation.objects.get(id=RID)
		if (ConversationToGet.ReasercherID != curren_user):
			ConversationToGet = None
		responsesToView=Responses.objects.filter(conversationID=ConversationToGet.id)
		
	except:
		responsesToView=None
	
	return render_to_response('Response_view.html', {'responses':responsesToView, 'currentUser':current_user}, context_instance=RequestContext(request))
'''

@permission_required('simcon.authLevel1')
def RetrieveAudio(request, UserAudio):
	temp=Response.objects.get(id=UserAudio)
	answer=temp.audioFile
	answer.open()
	response = HttpResponse()
	response.write(answer.read())
	response['Content-Type'] = 'audio/mp3'
	return response
	
def Responses(request, convIDstr):
	convID=int(convIDstr)
	responses=Response.objects.filter(conversationID=convID).order_by('order')
	try:
		conversation=Conversation.objects.get(id=convID)
	except:
		conversation=Conversation.objects.none()

	page=render(request, 'Response_view.html',{'conversation':conversation, 'responses':responses})
	return page
	
