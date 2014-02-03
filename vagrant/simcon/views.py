from django.shortcuts import render, render_to_response
from django.contrib.auth.decorators import permission_required
from django.http import HttpResponse
from django.views.generic import View

#used in video link processessing: regular expressions
import re

#import logging
#logger = logging.getLogger(__name__)

def Submission(request):
    return render(request, 'Student_Submission.html')

def Login(request):
    return render(request, 'Student_Login.html')

#For researchers: edit conversation templates 
# or create a new one.
@permission_required('simcon.authLevel1')
def TemplateWizard(request):
    if request.POST:
        if request.POST.get('submitTemplate'):
            print "submit the conversation"
            #check if values are valid
               #if not, send back to edit page and display errors
            #check if conversation already existed
               #if yes, check if associated with responses/shared responses
               #if yes, save as new version
            #store session variables into template tables
            #print success message
            #provide link back to main page
        elif request.POST.get('editExistingTemplate'):
            #prepopulate session variables and then reload page
            print "existing temp"
        else:
            return HttpResponse("ill formed request")
        
    return render(request, 'admin/template-wizard.html')

    
@permission_required('simcon.authLevel1')
def TemplateWizardIncludeLeft(request):
    if request.POST:
        if request.POST.get('addVideoToPool'):
            '''
            User has demanded to add a video to the pool in the left pane
            '''
            videoCode = re.match(r'.*?v=([^&]*)&?.*', request.POST['new_video'], 0)
            if videoCode:
              request.session['videos'].append(videoCode.group(1))
              request.session.modified = True
            else:
              print "Invalid video link."
        elif request.POST.get('removeVideoFromPool'):
            '''
            User has demanded to delete a video from the pool in the left pane
            '''
            request.session['videos'].remove(request.POST['removeVideoFromPool'])
            request.session.modified = True
        else:
            return HttpResponse("ill formed request")
    else:
        request.session['videos'] = [] # creating an empty list to hold our videos
        request.session['videos'].append('zJ8Vfx4721M')  # sample video
        request.session['videos'].append('IAISUDbjXj0')  #sample video
        request.session.modified = True

        
    return render(request, 'admin/template-wizard-include-left.html')

    
@permission_required('simcon.authLevel1')
def TemplateWizardIncludeRight(request):
    if request.POST:
        if request.POST.get('beginEditingVideo'):
            print"ok edit video stuff here"  
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
#        elif request.POST.get('removeVideoResponse'):
#            '''
#            User has requested that the active video be removed
#            '''
#            #TODO clean up session of all things related to this video
#            del request.session['selectedVideo']
#            del request.session['responseOptions']
#            request.session.modified = True
#        elif request.POST.get('addoption'):
#            '''
#            User has requested to add a new option to the conversation
#            '''
#            #load responseOptions
#            i = 1
#            while request.POST.get('response%d' % i):  # cycle through existing options and load them into responseOptions
#                request.session['responseOptions'][i-1] = request.POST.get('response%d' % i)
#                i += 1
#            request.session.modified = True
#            request.session['responseOptions'].append('Enter your option') #add an option
#            request.session.modified = True
#        elif request.POST.get('removeResponse'):
#            '''
#            User has requested a response option be removed
#            '''
#            #load responseOptions
#            i = 1
#            while request.POST.get('response%d' % i):  # cycle through existing options and load them into responseOptions
#                request.session['responseOptions'][i-1] = request.POST.get('response%d' % i)
#                i += 1
#            request.session.modified = True
            #TODO if response size < 2, don't do this
#            res = request.POST.get('removeResponse')
#            res = res.split(' ')
#            res = int(res[-1])-1 # should be number of response to remove
#            request.session['responseOptions'].pop(res) # remove this instance
#            request.session.modified = True
#        elif request.POST.get('addVideoToResponse'):
#            '''
#            User has requested that a video be added to this response option, involves redirecting the either video click
#            '''
#            #load responseOptions
#            i = 1
#            while request.POST.get('response%d' % i):  # cycle through existing options and load them into responseOptions
#                request.session['responseOptions'][i-1] = request.POST.get('response%d' % i)
#                i += 1
#            request.session.modified = True
#            res = request.POST.get('addVideoToResponse')
#            res = res.split(' ')
#            res = int(res[-1])-1 # should be number of response to remove
#            return HttpResponse('add %d' % res)
        else:
            return HttpResponse("ill formed request")
    else:
        print "nothing was submitted. print default page load thing"
        
    return render(request, 'admin/template-wizard-include-right.html')


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
