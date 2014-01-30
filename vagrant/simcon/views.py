from django.shortcuts import render, render_to_response
from django.contrib.auth.decorators import permission_required
from django.http import HttpResponse
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
        if request.POST.get('addvideobutton') and request.POST['sbutton'] == "Add Video":
            request.session['videos'].append(request.POST['new_video']) #TODO grab code from long youtube url
            request.session.modified = True
        elif request.POST.get('remove_video'):
            request.session['videos'].remove(request.POST['remove_video'])
            request.session.modified = True
        elif request.POST.get('submit'):
            return HttpResponse("submitted via picture %s" % request.POST.get('submit'))
        else:
            return HttpResponse("uh oh")
    else:
        request.session['videos'] = [] # creating an empty list to hold our videos
        request.session['videos'].append('zJ8Vfx4721M')  # sample video
        request.session['videos'].append('IAISUDbjXj0')  #sample video
        request.session.modified = True
        
    return render(request, 'admin/template-wizard.html')

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
