from django.conf.urls import patterns, include, url
#from django.conf import settings
from django.contrib import admin

admin.autodiscover()
   # Examples:
   # url(r'^$', 'simcon.views.home', name='home'),
   # url(r'^blog/', include('blog.urls')),
urlpatterns = patterns('simcon.views',
    url(r'^admin/template-wizard/$', 'TemplateWizard'),
    url(r'^generatelink/$', 'GenerateLink', name="GenerateLink"),
    url(r'^sharetemplate/$', 'ShareTemplate', name="ShareTemplate"),
    url(r'^shareresponse/$', 'ShareResponse', name="ShareResponse"),
    url(r'^links/$', 'Links', name="Links"),
    url(r'^responses/(\d+)$','Responses'),
    url(r'^studenttextchoice/$', 'StudentTextChoice', name = 'StudentTextChoice'),
    url(r'^studentinfo/$', 'StudentInfo', name = 'StudentInfo'),
    url(r'^student/(?P<VKey>\d{10})/$', 'StudentLogin', name = "StudentLogin"),  #, student.views.StudentLogin),
    url(r'^student/video/$', 'StudentVideoInstance', name = "StudentVideoInstance"),  #, student.views.StudentVideoInstance),
    url(r'^student/response/$', 'StudentResponseInstance', name = "StudentResponseInstance"),  #, student.views.StudentResponseInstance),
    url(r'^student/submission/$', 'Submission', name = "Submission"),  #, student.views.Submission),
    url(r'^admin/template-wizard$', 'TemplateWizard'),
    url(r'^admin/template-wizard-update', 'TemplateWizardUpdate'),#used to do the behind-the-scenes stuff, update session variables
    url(r'^admin/template-wizard-left-pane', 'TemplateWizardLeftPane'), #used to do the behind-the-scenes stuff, reload the left pane
    url(r'^admin/template-wizard-right-pane', 'TemplateWizardRightPane'),#used to do the behind-the-scenes stuff, reload the right pane

    url(r'^accounts/', include('django.contrib.auth.urls')),
    
	url(r'^admin/simcon/response/(\d+)/audio/', 'RetrieveAudio'),
	
	url(r'^admin/simcon/conversation/(\d+)', 'Responses'),
	

# overriding to build templates from admin page
#    url(r'^admin/simcon/template/add/$', 'TemplateWizard'),
# override url for navigation to template wizard from the admin template CRUD

    

#urlpatterns+=patterns('', url(r'^tinymce/', include('tinymce.urls')), 
	# this is for rich text embeds,
    

#urlpatterns += patterns('',
        url(r'^admin/', include(admin.site.urls))
                       
#if settings.DEBUG:
#    import debug_toolbar
#    urlpatterns += patterns('',
#        url(r'^__debug__/', include(debug_toolbar.urls)),
#    )
	)
