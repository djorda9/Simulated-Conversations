from django.template import loader, Context
from django.shortcuts import render
from models import Template
from models import StudentAccess
from models import PageInstance
import datetime

def StudentVideoInstance(request):
    # Get the template ID(TID), Page Instance ID(PIID), and Validation Key(ValKey) as  variables from the url
    # Check tID against template table. Check piID against piID of template, and valKey from StudentAccess table
    try:
        templ = Template.objects.get(templateID = TID)
    except Template.Invalid:
        print "Template ID is invalid"

    try:
        pi = PageInstance.objects.get(pageInstanceID = PIID)
    except PageInstance,Invalid:
        print "Page Instance ID is invalid"

    try:
        valid = StudentAccess.objects.get(validationKey = VKey)
    except StudentAccess.Invalid:
        print "Validation Key is invalid"

    # if student name/email exist, then update the Conversation model
    if(SName && SEmail) {
        T = Conversation(template=TID, researcherID = TID.researcherID, studentName = SName, studentEmail = SEmail, dateTime = datetime.datetime.strptime(datetime.datetime.now(), "%Y-%m-%d %H:%M"))
        T.save()
    }

    #create context variables for video web page
    page = PageInstance.objects.get(pageInstanceID = PIID)
    vidLink = page.videoLink
    text = page.richText
    playback = page.enablePlayback
    try:
        nextpage = TemplateResponseRel,objects.get(pageInstanceID = PIID)
        newPID = nextPageInstanceID
    except TemplateResponseRel.Invalid:
        newPID = 0
    if(!new_PID)
        new_PID = 0
	#upload to Responses table which PageInstanceID we're at with the current datetime. If all values already exist but the timedate is different,
    # then the page was refreshed, display an error, and after a few seconds go to beginning of conversation
#class Response(models.Model):
#       pageInstanceID  = models.ForeignKey(PageInstance) 
#        conversationID  = models.ForeignKey(Conversation)
#        order           = models.SmallIntegerField()
#        choice          = models.CharField(max_length=1000)
#        audioFile       = models.FileField(upload_to='test')
#    S = Response(pageInstanceID=PIID, conversationID = T, studentEmail = SEmail, dateTime = datetime.datetime.strptime(testDate, "%Y-%m-%d %H:%M"))te
#    T.save()

    t = loader.get_template('Student_Video_Response.html')
    c = Context({
    'vidLink': vidLink,
    'text': text,
    'playback': playback,
    'newPID': newPID,
    'message': 'I am the Student Video Response View.',
    'ValKey': VKey,
    'TID': TID
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
        pi = PageInstance.objects.get(pageInstanceID = PIID)
    except PageInstance,Invalid:
        print "Page Instance ID is invalid"

    try:
        valid = StudentAccess.objects.get(validationKey = VKey)
    except StudentAccess.Invalid:
        print "Validation Key is invalid"

    try:
        theResponses = TemplateResponseRel.objects.get(pageInstanceID = PIID)
    except TemplateResponseRel.Invalid:
        print "no responses to this page is invalid"

    #create a dictionary for all of the possible response options
    responses = {'r1':0,'r2':0,'r3':0,'r4':0,'r5':0,'r6':0,'r7':0,'r8':0,'r9':0,'r10':0}

    for(i in 1:theResponses.optionNumber) {
        responses[i] = theResponses.responseText[i]
    }
    #upload to Responses table which PageInstanceID we're at with the current datetime. If all values already exist but the timedate is different,
    # then the page was refreshed, display an error, and after a few seconds go to beginning of conversation
    t = loader.get_template('Student_Text_Response.html')
    c = Context({
    'responses': responses,
    'newPID': theResponses.nextPageInstanceID,
    'message': 'I am the Student Text Response View.',
    'ValKey': VKey,
    'TID': TID
    })
    return t.render(c)

def Submission(request):
    return render(request, 'Student_Submission.html')

def StudentLogin(request):
    try:
        access = StudentAccess.objects.get(validationKey = VKey)
    except StudentAccess.Invalid:
        print "Validation Key is invalid"

    expiration = access.expirationDate
    currentdate = datetime.datetime.now()
    if(currentdate < expiration)
        template = access.templateID
        pageinstance = template.firstInstanceID

        t = loader.get_template('Student_Login.html')
        c = Context({
        'TID': template,
        'PIID': pageinstance,
        'ValKey': VKey,
        'message': 'I am the Student Login View.'
        })
        return t.render(c)
    }
    else
        print "Conversation link has expired"










