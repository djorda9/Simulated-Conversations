from django.shortcuts import render
#from simcom.templates import Templates
import datetime

def StudentVideoInstance(request):
    #Somehow get the template ID(TID), Page Instance ID(PIID), and Validation Key(ValKey).
    #check tID against template table. Check piID against piID of template, and valKey from StudentAccess table
    #upload to Responses table which PageInstanceID we're at with the current datetime. If all values already exist but the timedate is different,
    # then the page was refreshed, display an error, and after a few seconds go to beginning of conversation
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
        return render(request, 'Student_Login.html', {'TID':template}, {'PIID':pageinstance}, {'ValKey':VKey})
    else
        print "Conversation link has expired"










