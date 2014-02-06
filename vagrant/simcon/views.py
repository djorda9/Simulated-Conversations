from django.shortcuts import render, render_to_response
from django.contrib.auth.decorators import permission_required
from django.http import HttpResponse
from django.views.generic import View

#for template insertions
from simcon.models import Template, PageInstance, TemplateResponseRel, TemplateFlowRel, Researcher
from django.contrib.auth.models import User

from django.core.context_processors import csrf #csrf
#from django.shortcuts import render_to_response #csrf

#used in video link processessing: regular expressions
import re

import logging
logger = logging.getLogger("simcon")

def Submission(request):
    return render(request, 'Student_Submission.html')

def Login(request):
    return render(request, 'Student_Login.html')

#For researchers: edit conversation templates 
# or create a new one.
@permission_required('simcon.authLevel1')
def TemplateWizard(request):
    logger.info("in templatewizard")
    c = {}
    c.update(csrf(request))
    if request.POST:
        if request.POST.get('saveTemplateButton'):
            logger.info("Inserting conversation into database")
            #TODO check if values are valid
               #if not, send back to edit page and display errors
            #TODO check if conversation already existed
               #if yes, check if associated with responses/shared responses
               #if yes, save as new version
            #TODO store session variables into template tables
            '''
            Storing session variables into temporary data elements
            '''
            temp = Template(researcherID = Researcher.objects.get(user=request.user), 
                             shortDesc   = request.POST.get('conversationTitle')) # NOTE: need firstInstanceID (TemplateFlowRel), added retroactively
            
            temp.save() # need this to create id
            pageInstances = []
            
            templateResponseRels = []
            
            templateFlowRels = []
            
            
            # build up structure in models
            for i, vid in enumerate(request.session['videos']):
                enabPlayback = False
                if vid in request.session['enablePlayback']:
                    enabPlayback = True
                
                pageInstances.append(PageInstance(templateID = temp,
                                                   videoOrResponse = "video",
                                                   videoLink = vid,
                                                   richText = "",
                                                   enablePlayback = enabPlayback
                                                   ))
                pageInstances[-1].save()
                #TODO populate nextInstanceID in templateflowrels?
                templateFlowRels.append(TemplateFlowRel(templateID = temp,
                                                         pageInstanceID = pageInstances[-1]))
                templateFlowRels[-1].save()
            
            temp.firstInstanceID = templateFlowRels[0]
            temp.save()
            
            #TODO do we need an option that could just terminate without a video link?
            for i, res in enumerate(request.session['responseText']):
                parentVid = request.session['responseParentVideo'][i]
                childVid =  request.session['responseChildVideo'][i]
                # res = responseText
                #TODO add checks if these exist
                parentPageInstance = pageInstances[request.session['videos'].index(parentVid)] # find parent page instance
                parentPageInstance.save()
                
                childPageInstance  = pageInstances[request.session['videos'].index(childVid)]
                childPageInstance.save()
                
                #TODO perhaps grab optionNumber by indexing our pageInstanceID in templateResponseRel?
                
                templateResponseRels.append(TemplateResponseRel(templateID = temp,
                                                                pageInstanceID = parentPageInstance,
                                                                responseText = res,
                                                                optionNumber = 1,# TODO not sure how to grab this from session
                                                                nextPageInstanceID = childPageInstance))
                templateResponseRels[-1].save()
                   
            
            #TODO print success message
            #TODO provide link back to main page
            #TODO for now this renders the wizard page, but render a "success page" instead.
            return render(request, 'admin/template-wizard.html')
        elif request.POST.get('editExistingTemplate'):
            logger.info("loading existing template")
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
    
    logger.info("template wizard updating")
    c = {}
    c.update(csrf(request))
    if request.POST:
        if request.POST.get('new_video'):
            '''
            User has demanded to add a video to the pool in the left pane
            '''
            videoCode = re.match(r'.*?v=([^&]*)&?.*', request.POST['new_video'], 0)
            if videoCode:
              #first check if video exists in pool... dont add twice
               #NOTE: this doesnt work. it still adds it.
              addIt = True
              for check in request.session['videos']:
                if check == request.POST['new_video']:
                  addIt = False
              if addIt == True:
                request.session['videos'].append(videoCode.group(1))
                request.session['enablePlayback'].append(videoCode.group(1))
                request.session.modified = True
            else:
              print "Invalid video link."
        elif request.POST.get('removeVideoFromPool'):
            '''
            User has demanded to delete a video from the pool in the left pane
            '''
            if request.POST['removeVideoFromPool']:
                if request.POST['removeVideoFromPool'] == request.session['selectedVideo']:
                    request.session['selectedVideo'] = ""
                request.session['videos'].remove(request.POST['removeVideoFromPool'])
                #TODO delete all associated responses + rich text
                request.session.modified = True
        elif request.POST.get('editVideo'):
            '''
            User selected a video to edit. Populate the right pane.
            '''
            editVideo = request.POST.get('editVideo')
            request.session['selectedVideo'] = editVideo
            request.session.modified = True;
        elif request.POST.get('saveVideo'):
            '''
            Save the video page that is being edited
            '''
            #TODO save some video attributes.....
            logger.info("video saving")
            request.session.selectedVideo = ""
            request.session.modified = True;
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
            #NOTE: this doesn't work. need to find how to delete by index....
            index = request.POST["removeResponseId"]
            request.session["responseText"].remove(index)
            request.session["responseParentVideo"].remove(index)
            request.session["responseChildVideo"].remove(index)
            request.session.modified = True
        elif request.POST.get('saveVideoPage'):
            '''
            User requested to save a video page's richtext
            '''
            #TODO this doesnt do anything yet
            logger.info("issue richtext save")
        elif request.POST.get('enablePlayback'):
            '''
            User selected to Enable/disable playback on youtube video
            '''
            #NOTE this doesnt work. for some reason, the checkbox is sending "on" no matter if its on or not.
            logger.info("post in enablePlayback is %s, vid is %s" % (request.POST['enablePlayback'], request.POST["vid"]))
            if request.session['selectedVideo'] not in request.session['enablePlayback']:
              request.session["enablePlayback"].append(request.session['selectedVideo'])
            else:
              request.session["enablePlayback"].remove(request.session['selectedVideo'])
            request.session.modified = True               
    else:
        logger.error("No post data")
        return HttpResponse("no POST data")
    logger.info("return null httpresponse")
    return HttpResponse("null")

#Reload the template wizards left pane if requested
@permission_required('simcon.authLevel1')
def TemplateWizardLeftPane(request):
    logger.info("left pane reloading")
    c = {}
    c.update(csrf(request))
    return render(request, 'admin/template-wizard-left-pane.html')

#Reload the template wizards right pane if requested
@permission_required('simcon.authLevel1')
def TemplateWizardRightPane(request):
    logger.info("right pane reloading")
    c = {}
    c.update(csrf(request))
    return render(request, 'admin/template-wizard-right-pane.html')



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
