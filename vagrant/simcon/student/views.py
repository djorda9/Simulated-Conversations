from django.template import loader, Context
from django.shortcuts import render
from models import Template
from models import StudentAccess
import datetime

def StudentVideoInstance(request):
    # Get the template ID(TID), Page Instance ID(PIID), and Validation Key(ValKey) as  variables from the url
    # Check tID against template table. Check piID against piID of template, and valKey from StudentAccess table
    try:
        templ = Template.objects.get(templateID = TID)
    except Template.Invalid:
        print "Template ID is invalid"

    if(PIID != templ.pageInstanceID)
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

    #check for existence of student response instance input. If so, upload to Responses table the response, the dateTime, and the studentName.
    return render(request, 'Student_Video_Response.html')

def StudentResponseInstance(request):
    #Somehow get the template ID(tID), Page Instance ID(piID), and Validation Key(ValKey).
    #check tID against template table. Check piID against piID of template, and valKey from StudentAccess table
    #upload to Responses table which PageInstanceID we're at with the current datetime. If all values already exist but the timedate is different,
    # then the page was refreshed, display an error, and after a few seconds go to beginning of conversation
    return render(request, 'Student_Text_Response.html')

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










