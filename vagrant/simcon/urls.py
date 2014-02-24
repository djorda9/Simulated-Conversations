from django.conf.urls import patterns, include, url
#from django.conf import settings

from django.contrib import admin
admin.autodiscover()
   # Examples:
   # url(r'^$', 'simcon.views.home', name='home'),
   # url(r'^blog/', include('blog.urls')),
urlpatterns = patterns('simcon.views',
<<<<<<< HEAD
    url(r'login/$', 'login_page', name="login"),
    url(r'^admin/template-wizard/$', 'TemplateWizard'),
    url(r'^generatelink/$', 'GenerateLink', name="GenerateLink"),
    url(r'^sharetemplate/$', 'ShareTemplate', name="ShareTemplate"),
    url(r'^shareresponse/$', 'ShareResponse', name="ShareResponse"),
    url(r'^links/$', 'Links', name="Links"),

    url(r'^student/(?P<VKey>\d{10})/$', student.views.StudentLogin),
    url(r'^student/video/(?P<ValKey>\d{10})&(?P<TID>\d{10})&(?P<PIID>\d{10})/$', student.views.StudentVideoInstance),
    url(r'^student/response/(?P<ValKey>\d{10})&(?P<TID>\d{10})&(?P<PIID>\d{10})/$', student.views.StudentResponseInstance),
    url(r'^student/submission/$', student.views.Submission),
=======
    url(r'^admin/template-wizard$', 'TemplateWizard'),
    url(r'^admin/template-wizard-update', 'TemplateWizardUpdate'),#used to do the behind-the-scenes stuff, update session variables
    url(r'^admin/template-wizard-left-pane', 'TemplateWizardLeftPane'), #used to do the behind-the-scenes stuff, reload the left pane
    url(r'^admin/template-wizard-right-pane', 'TemplateWizardRightPane'),#used to do the behind-the-scenes stuff, reload the right pane
    url(r'^admin/simcon/template/add/$', 'TemplateWizard'), # override url for navigation to template wizard from the admin template CRUD
>>>>>>> nate
    )
    
urlpatterns += patterns('',
    (r'^tinymce/', include('tinymce.urls')), # this is for rich text embeds
    url(r'^admin/', include(admin.site.urls)),  # for admin site
)
   

'''
Include a default page
urlpatterns += patterns('',
        url(r'^', include())
    )
'''

#if settings.DEBUG:
#    import debug_toolbar
#    urlpatterns += patterns('',
#        url(r'^__debug__/', include(debug_toolbar.urls)),
#    )
