from django.shortcuts import render, render_to_response, redirect
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.template import RequestContext
from django.http import HttpResponse
from django.db import transaction, IntegrityError
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.files.storage import default_storage
from django.core.urlresolvers import reverse
from django.conf import settings
from django.views.generic import View
from django.template import loader, Context
from django.core.context_processors import csrf
from django import forms # for forms
from forms import StudentAccessForm, ShareTemplateForm, LoginForm, ShareResponseForm
from models import StudentAccess, Response, Template, PageInstance, TemplateFlowRel, TemplateResponseRel, SharedResponses, Conversation
from tinymce.widgets import TinyMCE
from tinymce.models import HTMLField  # tinymce for rich text embeds
import re, logging, datetime

logger = logging.getLogger("simcon") #global logger handler

def StudentLogin(request,VKey = 123):

    try:
        access = StudentAccess.objects.get(validationKey = VKey)
    except Exception,e:
#fixme
        return HttpResponse("missing student access table entry: %s" %e)

    convo_Expiration = access.expirationDate
    currentdate = datetime.date.today()
    #On other option that is cleaner is to pass the current time and expiration to the template, and have an if statement in the template
    if(True):
    #if(currentdate < convo_Expiration):
        try:
            #logger.info(access.templateID.templateID)
            TID = access.templateID.templateID
            template = Template.objects.get(templateID = TID)
        except Exception,e:
#fixme
            return HttpResponse("missing template: %s" %e)

        pageInstance = template.firstInstanceID.pageInstanceID

        try:
            nextPage = PageInstance.objects.get(pageInstanceID = pageInstance)
        except Exception,e:
#fixme
            return HttpResponse("missing page instance: %s" %e)

        #reference variables ex: request.session.ValKey
        request.session['ValKey'] = VKey
        request.session['TID'] = template.templateID
        request.session['RID'] = template.researcherID.id
        request.session['PIID'] = pageInstance
        request.session['ConvoOrder'] = 1
        request.session['VoR'] = nextPage.videoOrResponse

        t = loader.get_template('Student_Login.html')
        c = Context({
        'message': 'I am the Student Login View.'
        })
        request.session.modified = True
        return render(request, 'Student_Login.html')
    else:
        print "Conversation link has expired"
#fixme
        return HttpResponse("Conversation link has expired")


#when the student submits their name and optional email, this updates the database
def StudentInfo(request):
    if request.method == 'POST':
        #logger.info(request.POST)
        studentname = request.POST.get("SName")
        studentemail = request.POST.get("SEmail")
        request.session['SName'] = studentname
        #Conversation wants a instances, not just the ids
        try:
            rID = request.session.get('RID')
            rese = User.objects.get(pk = rID)
        except Exception,e:
#fixme
            return HttpResponse("no researcher for conversation: %s" %e)
            
        try:
            tID = request.session.get('TID') #this doesn't equate to 2, this equates to "first working template"
            templ = Template.objects.get(templateID = tID)
        except Exception,e:
#fixme
            return HttpResponse("no researcher for conversation: %s" %e)

            
        #dt = datetime.datetime.today()
        T = Conversation(templateID_id=templ.templateID, researcherID_id=rese.pk, studentName=studentname, studentEmail=studentemail)#, dateTime = dt)
        
        try:
            T.save()
            #convo = Conversation.objects.get(dateTime = dt)
            request.session['convo'] = T.pk
        except Exception,e:
            return HttpResponse("problems saving conversation object: %s" %e)
            
        if request.session.get('VoR') == "video":
            # Get the template ID(TID), Page Instance ID(PIID), and Validation Key(ValKey) as  variables from the url (see urls.py)
            # Check tID against template table. Check piID against piID of template, and valKey from StudentAccess table
            try:
                templ = Template.objects.get(templateID = request.session.get('TID'))
            except Exception,e:
#fixme
                return HttpResponse("bad template reference: %s" %e)

            try:
                page = PageInstance.objects.get(pageInstanceID = request.session.get('PIID'), templateID = request.session.get('TID'))
            except Exception,e:
#fixme
                return HttpResponse("missing page instance: %s" %e)

            try:
                #possible case: someone changes validation key to a different validation key, would still succeed
                valid = StudentAccess.objects.get(validationKey = request.session.get('ValKey'))
            except Exception,e:
#fixme
                return HttpResponse("invalid validation key reference: %s" %e)

            #create context variables for video web page
            vidLink = page.videoLink
            text = page.richText
            playback = page.enablePlayback

            #try to find the next page, if it exists. Get it's PIID so we know where to go after this page.
            #otherwise, set PIID to 0. this will make this page end up at the Student Submission page.
            try:
                nextpage = TemplateFlowRel.objects.get(pageInstanceID = request.session.get('PIID'))
                request.session['PIID'] = nextpage.nextPageInstanceID.pageInstanceID
                request.session.modified = True
            except Exception,e:
#fixme
                return HttpResponse("missing template flow relation: %s" %e)

            request.session['VoR'] = "response"
            request.session.modified = True

            # there are ways to compact this code, but this is the most explicit way to render a template
            t = loader.get_template('Student_Video_Response.html')
            c = Context({
            'vidLink': vidLink,
            'text': text,
            'playback': playback,
            'message': 'I am the Student Video Response View.'
            })
            return render(request, 'Student_Video_Response.html', c)

        elif request.session.get('VoR') == "response":
            # Get the template ID(TID), Page Instance ID(PIID), and Validation Key(ValKey) as  variables from the url
            # Check tID against template table. Check piID against piID of template, and valKey from StudentAccess table
            try:
                templ = Template.objects.get(templateID = request.session.get('TID'))
            except Exception,e:
#fixme
                return HttpResponse("missing template: %s" %e)

            try:
                pi = PageInstance.objects.get(pageInstanceID = request.session.get('PIID'), templateID = request.session.get('TID'))
            except Exception,e:
#fixme
                return HttpResponse("missing page instance: %s" %e)

            try:
                valid = StudentAccess.objects.get(validationKey = request.session.get('ValKey'))
            except Exception,e:
#fixme
                return HttpResponse("missing student access: %s" %e)

            #get the list of responses to display to the student
            try:
                responses = TemplateResponseRel.objects.filter(pageInstanceID = request.session.get('PIID'))
            except Exception,e:
#fixme
                return HttpResponse("missing template response relation: %s" %e)

            # is this needed for anything?
            #try:
            #    conv = Conversation.objects.get(templateID = request.session.get('TID'), studentName = request.session.get('SName'))
            #except Exception,e:
#fixme
            #    return HttpResponse("missing conversation: %s" %e)

            request.session['VoR'] = "video"
            request.session.modified = True

            t = loader.get_template('Student_Text_Response.html')
            c = Context({
            'responses': responses,
            #'conv': conv,
            'message': 'I am the Student Text Response View.'
            })
            return render(request, 'Student_Text_Response.html', c)
        else:
            return render(request, 'Student_Submission.html')

#when the student chooses the text answer to their response, this updates the database with their choice
def StudentConvoStep(request):
    if request.method == 'POST':
        if request.session.get('VoR') == "video":
            piID = request.session.get('PIID')
            cID = request.session.get('convo')
            convoOrder = request.session.get('ConvoOrder')
            studentsChoice = request.POST.get("choice")
            
            #schoice = TemplateResponseRel.objects.filter(pageInstanceID_id = request.session.get('PIID'), optionNumber = request.POST.get("choice"))

            T = Response(pageInstanceID_id = piID, conversationID_id = cID, order = convoOrder, choice = studentsChoice, audioFile = "/media/audio/the_fox_say.mp3")
            T.save()
            #TODO if this fails, do cleanup for browser audio file copy/file system

            request.session['ConvoOrder'] += 1
            
            # Get the template ID(TID), Page Instance ID(PIID), and Validation Key(ValKey) as  variables from the url (see urls.py)
            # Check tID against template table. Check piID against piID of template, and valKey from StudentAccess table
            try:
                templ = Template.objects.get(templateID = request.session.get('TID'))
            except Exception,e:
#fixme
                return HttpResponse("bad template reference: %s" %e)

            try:
                page = PageInstance.objects.get(pageInstanceID = request.session.get('PIID'), templateID = request.session.get('TID'))
            except Exception,e:
#fixme
                return HttpResponse("missing page instance: %s" %e)

            try:
                #possible case: someone changes validation key to a different validation key, would still succeed
                valid = StudentAccess.objects.get(validationKey = request.session.get('ValKey'))
            except Exception,e:
#fixme
                return HttpResponse("invalid validation key reference: %s" %e)

            #create context variables for video web page
            vidLink = page.videoLink
            text = page.richText
            playback = page.enablePlayback

            #try to find the next page, if it exists. Get it's PIID so we know where to go after this page.
            #otherwise, set PIID to 0. this will make this page end up at the Student Submission page.
            try:
                nextpage = TemplateFlowRel.objects.get(pageInstanceID = request.session.get('PIID'))
                request.session['PIID'] = nextpage.nextPageInstanceID.pageInstanceID
                request.session.modified = True
            except Exception,e:
#fixme
                return HttpResponse("missing template flow relation: %s" %e)

            request.session['VoR'] = "response"
            request.session.modified = True

            # there are ways to compact this code, but this is the most explicit way to render a template
            t = loader.get_template('Student_Video_Response.html')
            c = Context({
            'vidLink': vidLink,
            'text': text,
            'playback': playback,
            'message': 'I am the Student Video Response View.'
            })
            return render(request, 'Student_Video_Response.html', c)

        elif request.session.get('VoR') == "response":
            # Get the template ID(TID), Page Instance ID(PIID), and Validation Key(ValKey) as  variables from the url
            # Check tID against template table. Check piID against piID of template, and valKey from StudentAccess table
            try:
                templ = Template.objects.get(templateID = request.session.get('TID'))
            except Exception,e:
#fixme
                return HttpResponse("missing template: %s" %e)

            try:
                pi = PageInstance.objects.get(pageInstanceID = request.session.get('PIID'), templateID = request.session.get('TID'))
            except Exception,e:
#fixme
                return HttpResponse("missing page instance: %s" %e)

            try:
                valid = StudentAccess.objects.get(validationKey = request.session.get('ValKey'))
            except Exception,e:
#fixme
                return HttpResponse("missing student access: %s" %e)

            #get the list of responses to display to the student
            try:
                responses = TemplateResponseRel.objects.filter(pageInstanceID = request.session.get('PIID'))
            except Exception,e:
#fixme
                return HttpResponse("missing template response relation: %s" %e)

            request.session['VoR'] = "video"
            request.session.modified = True

            t = loader.get_template('Student_Text_Response.html')
            c = Context({
            'responses': responses,
            #'conv': conv,
            'message': 'I am the Student Text Response View.'
            })
            return render(request, 'Student_Text_Response.html', c)
        else:
            return render(request, 'Student_Submission.html')
    else:
        return HttpResponse("can't render next conversation step")

def Submission(request):
    return render(request, 'Student_Submission.html')

# class for rich text field in a form
class RichTextForm(forms.Form):
    richText = forms.CharField(widget=TinyMCE(attrs={'cols': 80, 'rows': 10}))

#For researchers: edit conversation templates 
# or create a new one.
@login_required
def TemplateWizardSave(request):
    #c = {}
    #c.update(csrf(request))
    if request.POST:
        try:
            #do all of this atomically
            with transaction.atomic():        

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
                request.session['error'] = ""
                if request.POST.get('conversationTitle') == "":
                    request.session['conversationTitle'] = ""
                    request.session.modified = True
                    raise "noTitle"
                request.session['conversationTitle'] = request.POST.get('conversationTitle')
                request.session.modified = True
                temp = Template(researcherID = request.user, 
                                 shortDesc   = request.POST.get('conversationTitle')) # NOTE: need firstInstanceID (TemplateFlowRel), added retroactively

                temp.save() # need this to create id
                pageInstances = []
                pageInstances.append(PageInstance(templateID = temp,       #need this to use as endpoint in template flow
                                                  videoOrResponse = "endpoint",
                                                  videoLink = "",
                                                  richText = "",
                                                  enablePlayback = False))
                endpointPI = pageInstances[-1]
                pageInstances[-1].save()
                templateResponseRels = []
                templateFlowRels = []

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
                    pageInstances.append(PageInstance(templateID = temp,
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
                                pageInstances.append(PageInstance(templateID = temp,
                                                          videoOrResponse = "response",
                                                          videoLink = "",
                                                          richText = "",
                                                          enablePlayback = False
                                                          ))
                                responsesPageInstanceID = pageInstances[-1]
                                pageInstances[-1].save()
                                #link the parents pageInstance entry to the one we just created
                                pageInstanceMatchesVideo = pageInstances[i]
                                templateFlowRels.append(TemplateFlowRel(templateID = temp,
                                                             pageInstanceID = pageInstanceMatchesVideo,
                                                             nextPageInstanceID = responsesPageInstanceID
                                                             ))
                                templateFlowRels[-1].save()
                            #since a parent video references this child video, remove it from possible video heads
                            if res[2] != "endpoint":
                                possibleVideoHeads.remove(res[2])
                            # find the ID of the pageInstance that matches responseChildVideo[j]
                            # unless its "endpoint", then just insert "endpoint"
                            if res[2] == "endpoint":
                                insertNextPageInstanceID = endpointPI
                            else:
                                for k,vid2 in enumerate(request.session['videos']):
                                    if vid2 == res[2]:
                                        insertNextPageInstanceID = pageInstances[k]
                            #begin adding the responses into the templateResponseRels 
                            templateResponseRels.append(TemplateResponseRel(templateID = temp,
                                                             pageInstanceID = responsesPageInstanceID,
                                                             responseText = res[0],
                                                             optionNumber = numberOfResponses,
                                                             nextPageInstanceID = insertNextPageInstanceID         
                                                             ))
                            templateResponseRels[-1].save()
                    if numberOfResponses == 0:
                        raise "noResponses"
                #by now, there should be only one video head if the flow was built correctly.
                if len(possibleVideoHeads) > 1:
                    #if not, produce an error message and go back to template editor.
                    raise "noFirstVideo"
                #if you want to insert more errors, do it here.
                else:
                    #get the pageInstance that references this first video
                    for pi in pageInstances:
                        if pi.videoLink == possibleVideoHeads[0]:
                            firstPageID = pi
                    #firstPageID = pageInstances[pageInstances.index(possibleVideoHeads[0])]
                    #insert this video as the templates firstInstanceID
                    temp.firstInstanceID = firstPageID
                    temp.save()
                    #TODO map these arrays to the actual db -- should already be done by save() -nm
                    #TODO print success message
                    #TODO provide link back to main page
                    #return HttpResponse("Success")#render(request, 'admin/template-wizard-submission.html')
                    for vid in request.session['videos']:
                        request.session['richText/%s' % vid] = ""
                    request.session['videos'] = []
                    request.session['responseText'] = []
                    request.session['responseParentVideo'] = []
                    request.session['responseChildVideo'] = []
                    request.session['enablePlayback'] = []
                    request.session['conversationTitle'] = ""
                    request.session.modified = True
                    return render(request, 'template-wizard-save.html')
        except "noFirstVideo":
            request.session['error'] = "noFirstVideo"
            request.session.modified = True
            return TemplateWizardEdit(request, -1)
        except "noResponses":
            request.session['error'] = "noResponses"
            request.session.modified = True
            return TemplateWizardEdit(request, -1)
        except "noTitle":
            request.session['error'] = "noTitle"
            request.session.modified = True
            return TemplateWizardEdit(request, -1)
        except:
            request.session['error'] = "general"
            request.session.modified = True
            return TemplateWizardEdit(request, -1)
    else:
        return HttpResponse("Failure: no post data")

@login_required
def TemplateWizardEdit(request, tempID):
    request.session['edit'] = True;
    request.session['editTemplateID'] = tempID
    request.session.modified = True
    return TemplateWizard(request)

@login_required
def TemplateDelete(request, tempID):
    templateObj = Template.objects.get(templateID=tempID)
    context = RequestContext(request, {
        'templateObj': templateObj,
        })
    return render(request, 'template-delete.html', context)

@login_required
def TemplateWizard(request):
    c = {}
    c.update(csrf(request))
    if "error" not in request.session:
        request.session["error"] = ""
        request.session.modified = True
    if "edit" not in request.session:
        request.session["edit"] = False
        request.session.modified = True
    if "editTemplateID" not in request.session:
        request.session["editTemplateID"] = False
        request.session.modified = True
    if request.session["edit"] == True:
        request.session['edit'] = False
        request.session.modified = True
        request.session["selectedVideo"] = ""
        if request.session['editTemplateID'] != -1:
            #TODO... check if this needs to be a new version.
            temp = Template.objects.get(templateID = request.session['editTemplateID'])
            request.session["conversationTitle"] = temp.shortDesc
            request.session.modified = True
            fi = temp.firstInstanceID
            fitfl = TemplateFlowRel.objects.get(pageInstanceID = fi)
        return render(request, 'template-wizard.html')
    else:
        # DATA MODEL:
        request.session["error"] = ""
        request.session["conversationTitle"] = ""
        request.session["selectedVideo"] = "" # the currently selected video to edit
        request.session['videos'] = [] # creating an empty list to hold our videos in the pool
        # django doesn't appear to support multidimensional arrays in session variables.
        # so, the best way I could think to add correlating responses under each video,
        # is to add a responseText, and at the same time add the responseParentVideo that it 
        # loop though responseParentVideo until you find it, and reference that id in responseText. 
        # Same goes for all the responseChildVideo's it links to. -nate
        request.session['responseText'] = [] #create an empty list to hold responses text
        request.session['responseParentVideo'] = [] #create an empty list to hold responses video (like a foreign key)
        request.session['responseChildVideo'] = []
        request.session['enablePlayback'] = [] #if the video exists in this list, enable playback.
        #request.session['videos'].append('zJ8Vfx4721M')  # sample video
        #request.session['videos'].append('DewJHJlYOIU') #sample 
        request.session.modified = True

        return render(request, 'template-wizard.html')

#This is the "behind the scenes" stuff for the template wizard above
@login_required
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
                request.session['richText/%s' % videoCode] = "" # push current tinymce into session
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
                request.session['richText/%s' % request.session['selectedVideo']] = "" # push current tinymce into session
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
        elif request.POST.get('deleteTemplate'):
            #delete template where id=tempID
            #this should all just work!
            #django has default CASCADE which deletes all entries with foreign key ref. this id
            deleteTemp = Template.objects.get(templateID = request.POST.get('tempID'))
            deleteTemp.delete()

    return HttpResponse("Success")

@login_required
def ResearcherView(request):
    templateList = Template.objects.filter(researcherID=get_researcher(request.user)).order_by("-templateID")
    responseList = Conversation.objects.filter(researcherID=get_researcher(request.user)).order_by("-dateTime")[:10]
    sharedResponseList = SharedResponses.objects.filter(researcherID=get_researcher(request.user)).order_by("-dateTimeShared")[:10]
    context = RequestContext(request, {
        'templateList': templateList,
        'responseList': responseList,
        'sharedResponseList': sharedResponseList
    })
    return render(request, 'researcher-view.html', context)

# This view is used to generate the url for the researcher to give to a student to allow the student to take
# the simulated conversation.  Note the Student Login page requires the validation key to be part of the url.  To
# generate the url there is a function in StudentAccess model that you pass the validation key and it returns
# the url with the validation key as part of the url.  You can pass the templateID to the view in the url and it.
# will auto select the passed templateID as the templateID.  To pass the templateID,
# add the [templateID] (http://site.com/generatelink/[templateID]) to the end of the url for this view.
#The researcher has to select a template and set an expiration date for the link before the system will generate
# the link and store the templateID, researcherID, validationKey,and expirationDate for the link.
@login_required
def GenerateLink(request, templateID=None):
    link_url = None
    validation_key = None
    saved = False
    user_templateID = templateID
    template = None
    current_user = get_researcher(request.user)
    if request.method == 'POST':
        form = StudentAccessForm(request.POST, researcher=current_user)
        if form.is_valid():
            template =form.cleaned_data['templateID']
            while not saved:
                try:
                    validation_key = User.objects.make_random_password(length=10)
                    link = StudentAccess(templateID=template, researcherID = current_user,
                                        validationKey = validation_key, expirationDate=form.cleaned_data['expirationDate'])
                    link.save()
                    saved = True
                except IntegrityError as e:
                    saved = False
            link_url = link.get_link(validation_key)
            form = StudentAccessForm(initial = {'templateID':template}, researcher=current_user)

    else:
        if(user_templateID > -1):
            try:
                template = Template.objects.get(pk=user_templateID)
                form = StudentAccessForm(initial = {'templateID':template}, researcher=current_user)
            except ObjectDoesNotExist as e:
                form = StudentAccessForm(researcher=current_user)
        else:
            form = StudentAccessForm(researcher=current_user)
    return render_to_response('generate_link.html', {'link':link_url, 'key':validation_key, 'form':form},
                              context_instance = RequestContext(request))

# Returns the user object for the passed user
def get_researcher(current_user):
    researcher = User.objects.get(id=current_user.id)
    return researcher


#  This view is used to display all the links generated by a researcher.
@login_required
def Links(request):
    researcher_links = StudentAccess.objects.filter(researcherID=get_researcher(request.user)).\
                        order_by('-studentAccessID')
    return render_to_response('links.html', {'researcher_links':researcher_links},
                              context_instance=RequestContext(request))

# This view is used to share a template with another researcher.  It has a drop down box to allow the user to select the
# researcher they wish to share the template with and and a drop down box to select the template they wish to share.
# The template drop down box can be auto-selected by adding the [templatedID]
# (http://site.com/sharetemplate/[templateID]) to the end of the URL.  Once the user has selected a researcher and
# template, it makes a copy the selected template for the selected researcher.  It copies the data in the Template,
# PageInstance, TemplateFlowRel, & TemplateResponseRel for the specified template (replacing the researcherID with the
# selected researcher's researcherID).
# Note - The specification requires that we make a copy of the shared template for the researcher that it is being
# shared with.
@login_required
def ShareTemplate(request, templateID=None):
    user_templateID = templateID
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

                        #Updates the copied template's firstInstance with the copied firstInstance
                        if page.pageInstanceID==copied_template.firstInstanceID.pageInstanceID:
                            copied_template.firstInstanceID = temp
                            copied_template.save()

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

                    #Copies each TemplateResponseRel associated with the selected template.
                    response = TemplateResponseRel.objects.filter(templateID=template)
                    for old in response:
                        current_page = old.pageInstanceID
                        next_page = old.nextPageInstanceID
                        response_text = old.responseText
                        option_number = old.optionNumber

                        for i in old_new_pages:
                            oldId =  i.get_old()
                            if oldId.pageInstanceID==current_page.get_pageInstanceID():
                                current_page = i.newPageInstance
                            if next_page <> None:
                                if oldId.pageInstanceID==next_page.get_pageInstanceID():
                                    next_page = i.newPageInstance

                        temp = TemplateResponseRel(templateID=copied_template, pageInstanceID=current_page,
                                               responseText=response_text, optionNumber=option_number,
                                               nextPageInstanceID=next_page)
                        temp.save()

                    form = ShareTemplateForm(researcher=current_user)
                    researcher_userId = researcher.user.get_full_name()

            except ValueError as e:
                failed = "Required data is missing in database in order to copy the template."
                return render_to_response('share_template.html',
                                          {'failed':failed, 'form':form}, context_instance = RequestContext(request))
    else:
        if(user_templateID > -1):
            try:
                template = Template.objects.get(pk=user_templateID)
                form = ShareTemplateForm(initial = {'templateID':template}, researcher=current_user)
            except ObjectDoesNotExist as e:
                form = ShareTemplateForm(researcher=current_user)
        else:
            form = ShareTemplateForm(researcher=current_user)
    return render_to_response('share_template.html', {'success':researcher_userId,
                                                      'form':form}, context_instance = RequestContext(request))

# This view is used to share a response with another researcher.  It is required to pass the conversationID to the view
# by adding the [responseID] (http://site.com/shareresponse/[responseID])to the end of the URL.  If no conversationID is
# passed, it will display an error to the user.  If the conversation can not be located, it will display an error to the
# user.  If the researcher that is logged in is not the owner of the conversation, it will display an error to the user.
# The user can select a researcher from the drop down box that they wish to share a conversation with.  Once the user
# submits the request to share the conversation, it will then store conversationID, researcherID, dateTimeShared in the
# SharedResponse model.  If the user has already shared the conversation with the researcher, it will display a message
# that the user had already shared the conversation with the researcher.
@login_required
def ShareResponse(request, conversationID=None):
    user_conversationID = conversationID
    current_user = get_researcher(request.user)
    form = None
    success = None
    failed = None
    sharedWith = None
    if(user_conversationID < 0):
        failed = "The ConversationID was not provided."
    else:
        try:
            user_conversation = Conversation.objects.get(pk=user_conversationID)
        except ObjectDoesNotExist as e:
            failed = "The ConversationID was not found!"
        if failed is None:
            conversation_researcher = get_researcher(user_conversation.researcherID)
            if current_user.id==conversation_researcher.id:
                if request.method == 'POST':
                    form = ShareResponseForm(request.POST, researcher=current_user)
                    if form.is_valid():
                        researcher = form.cleaned_data['researcherID']
                        if user_conversation == None:
                            failed = "The ConversationID that was supplied is invalid."
                        else:
                            shared = SharedResponses(responseID=user_conversation, researcherID=researcher,
                                                     dateTimeShared=datetime.now())
                            try:
                                shared.save()
                            except IntegrityError as e:
                                sharedWith = SharedResponses.objects.filter(responseID=user_conversationID).\
                                    order_by('researcherID')
                                failed = "The conversation has already been shared with " + researcher.user.get_full_name()
                                return render_to_response('share_response.html', {'success':success, 'failed':failed,
                                        'shared':sharedWith, 'form':form}, context_instance = RequestContext(request))

                            sharedWith = SharedResponses.objects.filter(responseID=user_conversationID).\
                                order_by('researcherID')
                            success = researcher.user.get_full_name()
                else:
                    sharedWith = SharedResponses.objects.filter(responseID=user_conversationID).order_by('researcherID')
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
@login_required
def TemplateWizardLeftPane(request):
    c = {}
    c.update(csrf(request))
    return render(request, 'template-wizard-left-pane.html')

#Reload the template wizards right pane if requested
@login_required
def TemplateWizardRightPane(request):
    c = {}
    c.update(csrf(request))
    
    selVideo = request.session.get('selectedVideo')
    if selVideo:
        key = 'richText/%s' % selVideo
        if request.session.get(key): # we have richText to populate
            widge = RichTextForm({'richText': request.session[key]}) # preload with the value
            return render(request, 'template-wizard-right-pane.html', {'widge':widge, 'videoRichText': request.session[key]})
            
    widge = RichTextForm()        
    return render(request, 'template-wizard-right-pane.html', {'widge': widge})
'''
urlpatterns = patterns('',
    url(r'^mine/$', MyView.as_view(), name='my-view'),
) # in urls
 '''

'''
#@login_required
#def UpdateVideos(request):
'''

@login_required
def RetrieveAudio(request, UserAudio):
    temp=Response.objects.get(id=UserAudio)
    answer=temp.audioFile
    answer.open()
    response = HttpResponse()
    response.write(answer.read())
    response['Content-Type'] = 'audio/mp3'
    return response

@login_required
def Responses(request, userIDstr):
    userID=int(userIDstr)
    convoNames=[]
    try:
        conversations=Conversation.objects.filter(researcherID=userID)
        for c in conversations:
            temp=c.templateID
            convoNames.append(temp.shortDesc)
    except:
       conversations=Conversation.objects.none()

    shared=[]
    try:
        sharedIDs=SharedResponses.objects.filter(researcherID=userID)
        for c in sharedIDs:
            shared.append(c.responseID)

    except:
        pass

    convoList=zip(convoNames,conversations)

    page=render(request, 'Response_view.html',{'conversations':convoList, 'sharedConversations':shared})
#    assert False, locals()

    return page

def getFileHandle(): # helper function to make a unique file handle
    return User.objects.make_random_password(length=5) # TODO check for collision?
    
def saveAudio(request):
    c = {}
    c.update(csrf(request))
    data = request.FILES.get('data')
    saveTo = datetime.datetime.now().strftime("%Y/%m/%d")
    saveTo = "audio/%s/%s.wav" % (saveTo, getFileHandle()) 
    
    path = default_storage.save(saveTo, data)
    request.session['path'] = path
    return HttpResponse("null") #render(request, "Student_Text_Response.html", {'data':data})
    
def getTextResponse(request):
    c = {}
    c.update(csrf(request))
    return render(request, "Student_Text_Response.html")
    
