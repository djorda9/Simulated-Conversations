from django.shortcuts import render, render_to_response, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.template import RequestContext
from django.http import HttpResponse
from django.db import transaction, IntegrityError
from django.core.exceptions import ObjectDoesNotExist,PermissionDenied
from django.core.files.storage import default_storage
from django.template import loader, Context
from django.core.context_processors import csrf
from django import forms # for forms
from django.http import Http404
from forms import StudentAccessForm, ShareTemplateForm, LoginForm, ShareResponseForm
from models import StudentAccess, Response, Template, PageInstance, TemplateFlowRel, TemplateResponseRel, SharedResponses, Conversation, TemplateInProgress, TemplateInProgressRichText
from tinymce.widgets import TinyMCE
import re, logging, datetime, json

logger = logging.getLogger("simcon") #global logger handler

def StudentLogin(request,VKey = 123):

    try:
        access = StudentAccess.objects.get(validationKey = VKey)
    except Exception,e:
#fixme
        return render('Student_Expired.html')

    convo_Expiration = access.expirationDate
    currentdate = datetime.date.today()
    request.session['playbackAudio'] = access.playbackAudio
    request.session['playbackVideo'] = access.playbackVideo
    request.session['collectEmail']  = access.collectEmail
    #On other option that is cleaner is to pass the current time and expiration to the template, and have an if statement in the template
    #if(True):
    if(currentdate <= convo_Expiration):
#fixme
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

#student response function
# accepts an http request object, and loads a response page
def SResponse(request):
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
        responses = TemplateResponseRel.objects.filter(pageInstanceID = request.session.get('PIID')).order_by('optionNumber')
    except Exception,e:
#fixme
        return 0

    return responses

def SVideo(request):
    # Get the template ID(TID), Page Instance ID(PIID), and Validation Key(ValKey) as  variables from the url (see urls.py)
    # Check tID against template table. Check piID against piID of template, and valKey from StudentAccess table
    try:
        templ = Template.objects.get(templateID = request.session.get('TID'))
    except Exception,e:
#fixme
        return HttpResponse("bad template reference: %s" %e)

    try:
        page = PageInstance.objects.get(pageInstanceID = request.session.get('PIID'))
    except Exception,e:
#fixme
        return HttpResponse("missing page instance: %s" %e)

    try:
        valid = StudentAccess.objects.get(validationKey = request.session.get('ValKey'))
    except Exception,e:
#fixme
        return HttpResponse("invalid validation key reference: %s" %e)

    #try to find the next page, if it exists. Get it's PIID so we know where to go after this page.
    try:
        logger.info("current PIID value is a video page: ")
        logger.info(request.session.get('PIID'))
        
        nextpage = TemplateFlowRel.objects.get(pageInstanceID = request.session.get('PIID'))
        
        #logger.info('the template flow object:')
        #logger.info(nextpage)
        
        request.session['PIID'] = nextpage.nextPageInstanceID.pageInstanceID
        
        logger.info("new PIID value is a response page: ")
        logger.info(request.session.get('PIID'))
        
        request.session.modified = True
    except Exception,e:
#fixme
        request.session['PIID'] = -1
    return page

#when the student submits their name and optional email, this updates the database
def StudentInfo(request):
    if request.method == 'POST':
        #logger.info(request.POST)
        studentname = request.POST.get("SName")
        studentemail = request.POST.get("SEmail")
        if not studentemail:
            studentemail = ""
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

        T = Conversation.objects.create(templateID_id=templ.templateID, researcherID_id=rese.pk, studentName=studentname, studentEmail=studentemail)
        try:
            T.save()
            request.session['convo'] = T.pk
        except Exception,e:
            return HttpResponse("problems saving conversation object: %s" %e)
            
            
            
        if request.session.get('VoR') == "video":

            #validate session variables, return page info
            sPage = SVideo(request)
            
            #create context variables for video web page
            vidLink = sPage.videoLink
            text = sPage.richText
            playback = sPage.enablePlayback
        
            #the next page to load is a response page
            request.session['VoR'] = "response"
            request.session.modified = True
            
            #prepare the template context
            c = Context({
            'vidLink': vidLink,
            'text': text,
            'playback': playback,
            'message': 'I am the Student Video Response View.'
            })
            return render(request, 'Conversation_Parent.html', c)#'Student_Video_Response.html', c)

        elif request.session.get('VoR') == "response":

            #validate session variables, return queryset of responses
            responses = SResponse(request)

            #the next page is a video
            request.session['VoR'] = "video"
            request.session.modified = True
            
            c = Context({
            'responses': responses,
            #'conv': conv,
            'message': 'I am the Student Text Response View.'
            })
            return render(request, 'Student_Text_Response.html', c)
        else:
            request.session.flush()
            return render(request, 'Student_Submission.html')

#when the student chooses the text answer to their response, this updates the database with their choice
def StudentConvoStep(request):
    logger.info("method in studentconvo is %s" % request.method)
    if request.method == 'POST' or request.method == 'GET':
        logger.info("about to load a this type of page:")
        logger.info(request.session.get('VoR'))
        
        if request.session.get('VoR') == "video":
            piID = request.session.get('PIID')
            cID = request.session.get('convo')
            convoOrder = request.session.get('ConvoOrder')
            studentsChoice = request.session.get('choice')#request.POST.get('choice')
            logger.info("choice was %s" % studentsChoice)
            
            #fill a response object with the students audio and their choice
            responseRel = TemplateResponseRel.objects.get(templateResponseRelID = studentsChoice)
            
            T = Response.objects.create(pageInstanceID_id = piID, conversationID_id = cID, order = convoOrder, choice_id = studentsChoice, audioFile = request.session.get('path'))
#fixemefixeme
            T.save()
            #TODO if this fails, do cleanup for browser audio file copy/file system

            request.session['ConvoOrder'] += 1
            
            #the student has chosen a choice, figure out with the templateResponseRel table what the current PIID should be
            try:
                nextVideo = TemplateResponseRel.objects.get(pageInstanceID = request.session.get('PIID'), templateResponseRelID = studentsChoice)
                request.session['PIID'] = nextVideo.nextPageInstanceID.pageInstanceID
            except Exception,e:
#fixme
                #No next video page, go to submission page
                request.session.flush()
                return render(request, 'Student_Submission.html')
            
            #will get the variables for the current video page before changing PIID to point to this videos response page
            sPage = SVideo(request)
            
            #get the student access object to check for replayability of videos
            try:
                sAccess = StudentAccess.objects.get(validationKey = request.session.get('ValKey'))
            except Exception,e:
#fixme
                return HttpResponse("invalid validation key reference: %s" %e)

            #create context variables for video web page
            vidLink = sPage.videoLink
            text = sPage.richText
            playback = sPage.enablePlayback

            request.session['VoR'] = "response"
            request.session.modified = True
            
            if vidLink == "":
                request.session.flush()
                return render(request, 'Student_Submission.html')
            
            #Feed the current video PIID into SResponse to check for responses. If no responses to this video,
            #set a context variable. Make sure the user can't record audio, and end the conversation
            Rcheck = SResponse(request)
			
            if Rcheck == 0:
                End = True
            else:
                End = False
            
            # there are ways to compact this code, but this is the most explicit way to render a template
            c = Context({
            'vidLink': vidLink,
            'text': text,
            'playback': playback,
            'End': End,
            'message': 'I am the Student Video Response View.'
            })
            return render(request, 'Conversation_Video.html', c)#'Student_Video_Response.html', c)

        elif request.session.get('VoR') == "response":
        
            #validate session variables, get queryset of responses
            responses = SResponse(request)

            request.session['VoR'] = "response"
            request.session.modified = True
            
            if not responses:
                request.session.flush()
                return render(request, 'Student_Submission.html')

            c = Context({
            'responses': responses,
            #'conv': conv,
            'message': 'I am the Student Text Response View.'
            })
            return render(request, 'Conversation_Text.html', c)#'Student_Text_Response.html', c)
        elif request.session.get('VoR') == "endpoint":
            request.session.flush()
            return render(request, 'Student_Submission.html')
    else:
        #return HttpResponse("can't render next conversation step")
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

        c = Context({
        'responses': responses,
        #'conv': conv,
        'message': 'I am the Student Text Response View.'
        })
        return render(request, 'Student_Text_Response.html', c)

'''        
def StudentTextResponse(request):
    # Get the template ID(TID), Page Instance ID(PIID), and Validation Key(ValKey) as  variables from the url
    # Check tID against template table. Check piID against piID of template, and valKey from StudentAccess table
    try:
        templ = Template.objects.get(templateID = request.session.get('TID'))
    except Exception,e:
        return HttpResponse("missing template: %s" %e)

    try:
        pi = PageInstance.objects.get(pageInstanceID = request.session.get('PIID'), templateID = request.session.get('TID'))
    except Exception,e:
        return HttpResponse("missing page instance: %s" %e)

    try:
        valid = StudentAccess.objects.get(validationKey = request.session.get('ValKey'))
    except Exception,e:
        return HttpResponse("missing student access: %s" %e)

    #get the list of responses to display to the student
    try:
        responses = TemplateResponseRel.objects.filter(pageInstanceID = request.session.get('PIID')).order_by('optionNumber')
    except Exception,e:
        return HttpResponse("missing template response relation: %s" %e)

    request.session['VoR'] = "video"
    request.session.modified = True
    
    c = Context({
    'responses': responses,
    #'conv': conv,
    'message': 'I am the Student Text Response View.'
    })
    return render(request, 'Conversation_Text.html', c)#'Student_Text_Response.html', c)
    '''


#Reload the mode Pane in conversation
@login_required
def RenderVideo(request):
    c = {}
    c.update(csrf(request))
    return render(request, 'Conversation_Video.html')

def PostChoice(request):
    c = {}
    c.update(csrf(request))
    request.session['choice'] = request.POST.get('choice')
    logger.info("Posting choice %s" % request.session['choice'])
    request.session['VoR'] = "video"
    request.session.modified = True
    return HttpResponse("success")

    
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
    if request.method == "POST":
        if request.POST.get("saveInProg") == "saveInProg":
            request.session['conversationTitle'] = request.POST.get('conversationTitle')
            request.session.modified = True
            return TemplateSaveInProgress(request)
        else:
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
                    request.session['metaError'] = ""

                    if request.session['editTemplateID'] != False:
                        #you are editing an existing template, so delete the old one first.
                        deleteTemp = Template.objects.get(templateID = request.session['editTemplateID'])
                        deleteTemp.delete()

                    if request.POST.get('conversationTitle') == "":
                        request.session['conversationTitle'] = ""
                        request.session.modified = True
                        raise Exception("noTitle")
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
                    pageInstances[-1].save()
                    endpointPI = pageInstances[-1]
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
                        request.session['metaError'] = i # save current video being worked on
                        pageInstances.append(PageInstance(templateID = temp,
                                                           videoOrResponse = "video",
                                                           videoLink = vid,
                                                           richText = request.session['richText/%s' % vid],
                                                           enablePlayback = enabPlayback
                                                           ))
                        pageInstances[-1].save()
                        #thisVidsPI = pageInstances[-1]
                    #now all the videos have pageInstanceIDs

                    #next, for each video, 
                    for i, vid in enumerate(request.session['videos']):     
                        #the pageInstances should correspond to the session videos by id at this point.
                        #so only keep track of the responses that match this parent video (vid)
                        numberOfResponses = 0
                        request.session['metaError'] = i
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
                                    pageInstances[-1].save()
                                    responsesPageInstanceID = pageInstances[-1]
                                    #link the parents pageInstance entry to the one we just created
                                    for getapi in pageInstances:
                                        if getapi.videoLink == vid:
                                            thisVidsPI = getapi
                                            break
                                    pageInstanceMatchesVideo = thisVidsPI
                                    templateFlowRels.append(TemplateFlowRel(templateID = temp,
                                                                 pageInstanceID = pageInstanceMatchesVideo,
                                                                 nextPageInstanceID = responsesPageInstanceID
                                                                 ))
                                    templateFlowRels[-1].save()
                                #since a parent video references this child video, remove it from possible video heads
                                if res[2] != "endpoint" and res[2] in possibleVideoHeads:
                                    possibleVideoHeads.remove(res[2])
                                # find the ID of the pageInstance that matches responseChildVideo[j]
                                # unless its "endpoint", then just insert "endpoint"
                                if res[2] == "endpoint":
                                    insertNextPageInstanceID = endpointPI
                                else:
                                    for k,vid2 in enumerate(request.session['videos']):
                                        if vid2 == res[2]:
                                            for q in pageInstances:
                                                for p in PageInstance.objects.filter(videoLink = vid2, templateID = temp):
                                                    if q == p:
                                                        insertNextPageInstanceID = p
                                #begin adding the responses into the templateResponseRels 
                                templateResponseRels.append(TemplateResponseRel(templateID = temp,
                                                                 pageInstanceID = responsesPageInstanceID,
                                                                 responseText = res[0],
                                                                 optionNumber = numberOfResponses,
                                                                 nextPageInstanceID = insertNextPageInstanceID         
                                                                 ))
                                templateResponseRels[-1].save()
                        if numberOfResponses == 0:
                            raise Exception("noResponses")
                    pHeadLen = len(possibleVideoHeads)
                    request.session['metaError'] = "" # clear meta error
                    if pHeadLen == 0:
                        raise  Exception("The FirstVideo can not be linked as a response.")
                    #by now, there should be only one video head if the flow was built correctly.
                    if pHeadLen > 1:
                        #if not, produce an error message and go back to template editor.
                        raise Exception("noFirstVideo")
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
                        #now delete the in progress template if it exists.....
                        if "tempInProg" not in request.session:
                            request.session["tempInProg"] = -2
                            request.session.modified = True
                        if request.session['tempInProg'] != -2 and request.session['tempInProg'] != "":
                            deleteTIP = TemplateInProgress.objects.get(templateInProgressID = request.session['tempInProg'])
                            deleteTIP.delete()
                            request.session['tempInProg'] = ""
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
            except Exception as e:
                if not e.message:
                    request.session['error'] = "general"
                else:
                    request.session['error'] = e.message
                if request.session['metaError'] != "":
                    request.session['error'] += " in video: " + str(request.session['metaError'] + 1)
                request.session.modified = True
                #logger.info("error was %s" % request.session['error'])
                return TemplateWizardEdit(request, -1)
    else:
        return HttpResponse("Failure: no post data")

@login_required
def TemplateWizardEdit(request, tempID):
    request.session['edit'] = True;
    if tempID == -1 or tempID == -2:
        request.session['errorFlag'] = True
        if tempID == -2:
            tempInProg = TemplateInProgress.objects.get(templateInProgressID = request.session['tempInProg'])
            request.session['conversationTitle'] = tempInProg.conversationTitle
            logger.info(tempInProg.videoList)
            request.session['videos'] = []
            request.session['responseText'] = []
            request.session['responseParentVideo'] = []
            request.session['responseChildVideo'] = []
            jsonDec = json.decoder.JSONDecoder()
            request.session['videos'] = jsonDec.decode(tempInProg.videoList)
            request.session['responseText'] = jsonDec.decode(tempInProg.responseTextList)
            request.session['responseParentVideo'] = jsonDec.decode(tempInProg.responseParentVideoList)
            request.session['responseChildVideo'] = jsonDec.decode(tempInProg.responseChildVideoList)
            for vid in request.session['videos']:
                result = TemplateInProgressRichText.objects.get(templateInProgressID = request.session['tempInProg'], video = vid)
                request.session['richText/%s'%vid] = result.richText
            request.session.modified = True
        else:
            request.session['tempInProg'] = -2
    else:
        request.session['editTemplateID'] = tempID
        request.session['errorFlag'] = False
        request.session['error'] = ""
    request.session.modified = True
    return TemplateWizard(request)

@login_required
def TemplateDelete(request, tempID):
    templateObj = Template.objects.get(templateID=tempID)
    #Security check:
    if not request.user.is_superuser and templateObj.researcherID != request.user:
        raise Http404
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
    if "error" not in request.session:
        request.session["errorRightPane"] = ""
        request.session.modified = True
    if "edit" not in request.session:
        request.session["edit"] = False
        request.session.modified = True
    if "editTemplateID" not in request.session:
        request.session["editTemplateID"] = False
        request.session.modified = True
    if "errorFlag" not in request.session:
        request.session["errorFlag"] = False
        request.session.modified = True
    pastTempInProgs = TemplateInProgress.objects.filter(researcherID = request.user).order_by('-dateTimeSaved')
    context = RequestContext(request, {
            'pastTempInProgs': pastTempInProgs
        })
    if request.session["edit"] == True:
        request.session['edit'] = False
        request.session.modified = True
        request.session["selectedVideo"] = ""
        #if the session's template ID = -1, that just means there was an error trying to save. 
        #the session variables are still intact, so just regenerate the template wizard.
        #else, begin editing a template.
        if request.session['errorFlag'] != True:
            #ok, screw the 'version' idea. Heres a new idea. If responses to this template exist,
            #instead just produce an error message. The researcher cannot edit this template.
            #they can "copy to a new template", which actually does populate all the 
            #same session variables, but will not save over the old template.
            #also it will change the title to include "(copy)"
            temp = Template.objects.get(templateID = request.session['editTemplateID'])
            responses = Conversation.objects.filter(templateID = temp.templateID)
            if len(responses) > 0:
                request.session['error'] = "editButResponses"
                request.session['editTemplateID'] = False
                request.session['edit'] = False
                request.session["conversationTitle"] = temp.shortDesc + " (copy)"
                request.session.modified = True
            else:
                request.session["conversationTitle"] = temp.shortDesc
                request.session.modified = True
            tempFlow = TemplateFlowRel.objects.filter(templateID = temp)
            tempResponseFlow = TemplateResponseRel.objects.filter(templateID = temp)
            pages = PageInstance.objects.filter(templateID = temp)
            firstPage = temp.firstInstanceID
            request.session['tempInProg'] = ""
            request.session["error"] = ""
            request.session['selectedVideo'] = ""
            request.session['videos'] = []
            request.session['responseText'] = [] #create an empty list to hold responses text
            request.session['responseParentVideo'] = [] #create an empty list to hold responses video (like a foreign key)
            request.session['responseChildVideo'] = []
            request.session['enablePlayback'] = [] #this now does nothing. ignore.
            for p in tempFlow:
                if p.pageInstanceID.videoOrResponse == 'video':
                    request.session['videos'].append(p.pageInstanceID.videoLink)
                    if p.pageInstanceID.enablePlayback == True:
                        request.session['enablePlayback'].append(p.pageInstanceID.videoLink)
                    request.session['richText/%s' % p.pageInstanceID.videoLink] = p.pageInstanceID.richText
                if p.nextPageInstanceID.videoOrResponse == 'response':
                    for t in tempResponseFlow:
                        if t.pageInstanceID.pageInstanceID == p.nextPageInstanceID.pageInstanceID:
                            request.session['responseText'].append(t.responseText)
                            for q in tempFlow:
                                if q.nextPageInstanceID.pageInstanceID == t.pageInstanceID.pageInstanceID:
                                    request.session['responseParentVideo'].append(q.pageInstanceID.videoLink)
                            if t.nextPageInstanceID.videoOrResponse == 'endpoint':
                                request.session['responseChildVideo'].append("endpoint")
                            else:
                                request.session['responseChildVideo'].append(t.nextPageInstanceID.videoLink)
            request.session.modified = True
        return render(request, 'template-wizard.html', context)
    else:
        # DATA MODEL:
        request.session["error"] = ""
        request.session["errorRightPane"] = ""
        request.session["errorFlag"] = False
        request.session["editTemplateID"] = False
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
        request.session['enablePlayback'] = [] #apparently this is now useless.... look in "generate link"
        #request.session['videos'].append('zJ8Vfx4721M')  # sample video
        #request.session['videos'].append('DewJHJlYOIU') #sample 
        request.session.modified = True
        return render(request, 'template-wizard.html', context)

#This allows a researcher to save a template in progress
@login_required
def TemplateSaveInProgress(request):
    if "tempInProg" not in request.session:
        pass
    elif request.session['tempInProg'] != -2 and request.session['tempInProg'] != "":
        deleteOld = TemplateInProgress.objects.get(templateInProgressID = request.session['tempInProg'])
        deleteOld.delete()
    tempInProg = TemplateInProgress()
    tempInProg.researcherID = request.user
    tempInProg.save()
    for vid in request.session['videos']:
        tempIPRT = TemplateInProgressRichText()
        tempIPRT.templateInProgressID = tempInProg
        tempIPRT.video = vid
        tempIPRT.richText = request.session['richText/%s'%vid]
        tempIPRT.save()
    tempInProg.conversationTitle = request.POST.get("conversationTitle")
    tempInProg.videoList = json.dumps(list(request.session['videos']))
    tempInProg.responseTextList = json.dumps(list(request.session['responseText']))
    tempInProg.responseParentVideoList = json.dumps(list(request.session['responseParentVideo']))
    tempInProg.responseChildVideoList = json.dumps(list(request.session['responseChildVideo']))
    tempInProg.save()
    request.session['tempInProg'] = tempInProg.templateInProgressID
    request.session.modified = True
    return TemplateWizardEdit(request, -2)

@login_required
def TemplateLoadInProgress(request, tempIPID):
    request.session['tempInProg'] = tempIPID
    request.session.modified = True
    return TemplateWizardEdit(request, -2)


#This is the "behind the scenes" stuff for the template wizard above
@login_required
def TemplateWizardUpdate(request):
    c = {}
    c.update(csrf(request))
    if request.method == "POST":
        request.session["errorRightPane"] = ""
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
        elif request.POST.get('oldVideo'):
            oldVideo = request.POST.get('oldVideo')
            videoCode = re.match(r'.*?v=([^&]*)&?.*', request.POST['newURL'], 0)
            videoCode = videoCode.group(1) # just pertinent code
            try:
                if videoCode and videoCode not in request.session['videos']:
                    for idx, item in enumerate(request.session['videos']):
                        if oldVideo == item:
                            request.session['videos'][idx] = videoCode
                            request.session.modified = True
                            request.session['selectedVideo'] = videoCode
                            request.session['richText/%s' % videoCode] = request.session['richText/%s' % oldVideo]
                            del request.session['richText/%s' % oldVideo]
                            removeIndex = []
                            loopRestart = True
                            while loopRestart:
                                loopRestart = False
                                for idxRes, response in enumerate(request.session['responseParentVideo']):
                                    if(oldVideo == response):
                                        removeIndex.append(idxRes)
                                        request.session["responseText"].append(request.session["responseText"][idxRes])
                                        request.session["responseParentVideo"].append(videoCode)
                                        request.session["responseChildVideo"].append(request.session["responseChildVideo"][idxRes])
                                        request.session["responseParentVideo"].pop(idxRes)
                                        request.session["responseText"].pop(idxRes)
                                        request.session["responseChildVideo"].pop(idxRes)
                                        loopRestart = True
                                        break
                                    if loopRestart:
                                        break

                            for idxChild, child in enumerate(request.session['responseChildVideo']):
                                if(oldVideo == child):
                                    request.session['responseChildVideo'][idxChild] = videoCode
                            if oldVideo in request.session['enablePlayback']:
                              request.session["enablePlayback"].remove(oldVideo)
                              request.session["enablePlayback"].append(request.session['selectedVideo'])
                            request.session.modified = True
                else:
                    raise Exception('The video link is either invalid or it is already in the video pool.')
            except Exception as e:
                if not e.message:
                    request.session["errorRightPane"] = "general"
                else:
                    request.session["errorRightPane"] = e.message
                request.session.modified = True
                logger.info("error was %s" % request.session["errorRightPane"])
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
    link_user = None
    validation_key = None
    saved = False
    user_templateID = templateID
    exp_date = None
    success = None
    template = None
    playback_audio = None
    playback_video = None
    collect_email = None
    current_user = get_researcher(request.user)
    if request.method == 'POST':
        #logger.info("post for playback was %s" % request.POST['playbackAudio'])
        
        #if request.POST['playbackAudio'] == 'on':
        #    playback_audio = True
        #else:
        #    playback_audio = False
            
        form = StudentAccessForm(request.POST, researcher=current_user)
        #logger.info("is the form valid? %s" % form.is_valid())
        if form.is_valid():
            template =form.cleaned_data['templateID']
            while not saved:
                try:
                    validation_key = User.objects.make_random_password(length=10)
                    exp_date = form.cleaned_data['expirationDate']
                    playback_audio = form.cleaned_data['playbackAudio']
                    playback_video = form.cleaned_data['playbackVideo']
                    collect_email = form.cleaned_data['collectEmail']
                    #logger.info("playbackaudio is %s" % playback_audio)
                    link = StudentAccess(templateID=template, researcherID = current_user,
                                        validationKey = validation_key, expirationDate=exp_date, 
                                        playbackAudio = playback_audio, playbackVideo = playback_video,
                                        collectEmail = collect_email)
                    link.save()
                    saved = True
                    success = "You have successfully generated a link to " + template.__unicode__() + " template.\n"
                    success = success + "The Link expires on " + exp_date.strftime("%B %d, %Y")
                except IntegrityError as e:
                    saved = False
            link_url = link.get_link(validation_key)
            link_user = request.get_host() + link_url
            form = StudentAccessForm(initial = {'templateID':template}, researcher=current_user)

    else:
        if(user_templateID > -1):
            try:
                template = Template.objects.get(pk=user_templateID)
                form = StudentAccessForm(initial = {'templateID':template}, researcher=current_user)
                #logger.info("initial playback in form is %s" % form.data['playbackAudio'])
            except ObjectDoesNotExist as e:
                form = StudentAccessForm(researcher=current_user)
        else:
            form = StudentAccessForm(researcher=current_user)
    return render_to_response('generate_link.html', {'link':link_url, 'link_user':link_user, 'key':validation_key,
                                                     'success':success, 'form':form},
                              context_instance = RequestContext(request))

# Returns the user object for the passed user
def get_researcher(current_user):
    researcher = User.objects.get(id=current_user.id)
    return researcher


#  This view is used to display all the links generated by a researcher.
@login_required
def Links(request, tempID):
    today = datetime.datetime.today()
    researcher_links = StudentAccess.objects.filter(researcherID=get_researcher(request.user)).filter(templateID=tempID).filter(expirationDate__gte=today)
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
    researcher_name = None

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
                    researcher_name = researcher.get_full_name()
                    if(researcher_name==''):
                        researcher_name = researcher.get_username()

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
    return render_to_response('share_template.html', {'success':researcher_name,
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
                                                     dateTimeShared=datetime.datetime.now())
                            try:
                                shared.save()
                            except IntegrityError as e:
                                sharedWith = SharedResponses.objects.filter(responseID=user_conversationID).\
                                    order_by('researcherID')
                                failed = "The conversation has already been shared with " + researcher.get_full_name()
                                return render_to_response('share_response.html', {'success':success, 'failed':failed,
                                        'shared':sharedWith, 'form':form}, context_instance = RequestContext(request))

                            sharedWith = SharedResponses.objects.filter(responseID=user_conversationID).\
                                order_by('researcherID')
                            success = researcher.get_full_name()
                            if(success==''):
                                success = researcher.get_username()
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
def Responses(request):

    userID = get_researcher(request.user)


    conversations=Conversation.objects.filter(researcherID=userID)

    shared=[]




    sharedIDs=SharedResponses.objects.filter(researcherID=userID)
    for c in sharedIDs:
		temp=c.responseID
		shared.append(temp)

    page=render(request, 'Response_view.html',{'conversations':conversations, 'sharedConversations':shared})
#    assert False, locals()

    return page

@login_required
def SingleResponse(request, convoID):


	currentConvo=Conversation.objects.get(id=convoID)
	userID=get_researcher(request.user)

	if currentConvo.researcherID != userID:
		sharedCheck=SharedResponses.objects.filter(responseID=currentConvo)
		if sharedCheck.filter(researcherID=userID).exists() == False:
			raise PermissionDenied

	responses=Response.objects.filter(conversationID=convoID).order_by('order')

	page=render(request, 'Single_Response.html', {'responses':responses, 'conversation':currentConvo})
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

def logout_view(request):
    logout(request)
    return redirect('ResearcherView')
 
@login_required 
def DeleteResponse(request, responseNum=None):
    response = Conversation.objects.get(pk = responseNum)
    
    #Security check:
    if not request.user.is_superuser and response.researcherID != request.user:
        raise Http404
    
        
    response.delete()
    return redirect('ResearcherView')
            
            