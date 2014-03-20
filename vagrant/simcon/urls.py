from django.conf.urls import patterns, include, url
from django.conf import settings
from django.contrib import admin

from django.views.generic import TemplateView
admin.autodiscover()
   # Examples:
   # url(r'^$', 'simcon.views.home', name='home'),
   # url(r'^blog/', include('blog.urls')),
urlpatterns = patterns('simcon.views',
    url(r'^$', 'ResearcherView', name="Index"),
    url(r'^researcherview/$', 'ResearcherView', name="ResearcherView"),
    url(r'^login/$', 'login_page', name="login"),
    url(r'^template-wizard/$', 'TemplateWizard', name="TemplateWizard"),
    url(r'^generatelink/$', 'GenerateLink', name="GenerateLink"),
    url(r'^generatelink/(?P<templateID>\d*)/$', 'GenerateLink', name="GenerateLink_with_templateID"),
    url(r'^sharetemplate/$', 'ShareTemplate', name="ShareTemplate"),
    url(r'^sharetemplate/(?P<templateID>\d*)/$', 'ShareTemplate', name="ShareTemplate_with_templateID"),
    url(r'^shareresponse/$', 'ShareResponse', name="ShareResponse"),
    url(r'^shareresponse/(?P<conversationID>\d*)/$', 'ShareResponse', name="ShareResponse_with_responseID"),
    url(r'^deleteresponse/(?P<responseNum>\d*)/$', 'DeleteResponse', name="DeleteResponse_by_id"),
    url(r'^links/(?P<tempID>\d*)$', 'Links', name="Links"),
    url(r'^studentconvostep/$', 'StudentConvoStep', name = 'StudentConvoStep'),
    url(r'^studentinfo/$', 'StudentInfo', name = 'StudentInfo'),
    #url(r'^studentinfo/text_response$', 'StudentTextResponse', name='text_response'), #'getTextResponse'),
    url(r'^student/(?P<VKey>\w{10})/$', 'StudentLogin', name = "StudentLogin"),
    url(r'^conversationvideo/$', 'RenderVideo', name = "RenderVideo"),
    url(r'^postchoice/$', 'PostChoice', name = 'PostChoice'),
    #url(r'^studenttextpane/$', 'ConversationTextPane', name= 'ConversationTextPane'),
    #url(r'^   $', 'Con
    #url(r'^student/video/$', 'StudentVideoInstance', name = "StudentVideoInstance"),
    #url(r'^student/response/$', 'StudentResponseInstance', name = "StudentResponseInstance"),
    url(r'^student/submission/$', 'Submission', name = "Submission"),
    url(r'^template-delete/(\d+)$', 'TemplateDelete', name="TemplateDelete"),
    url(r'^template-wizard/(\d+)$', 'TemplateWizardEdit', name="TemplateWizardEdit"),
    url(r'^template-wizard-save/$', 'TemplateWizardSave', name="TemplateWizardSave"),
    url(r'^template-wizard-update', 'TemplateWizardUpdate', name="TemplateWizardUpdate"),
    url(r'^template-wizard-left-pane', 'TemplateWizardLeftPane', name="TemplateWizardLeftPane"),
    url(r'^template-wizard-right-pane', 'TemplateWizardRightPane', name="TemplateWizardRightPane"),
    url(r'^template-save-in-progress', 'TemplateSaveInProgress', name="TemplateSaveInProgress"),
    url(r'^template-load-in-progress/(\d+)$', 'TemplateLoadInProgress', name="TemplateLoadInProgress"),
    url(r'^tinymce/', include('tinymce.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^responses/$', 'Responses', name="Responses"),
	url(r'^responses/(\d+)$', 'SingleResponse', name="SingleResponse"),
    url(r'^audio/save$', 'saveAudio', name="SaveAudio"),
    url(r'logout/$', 'logout_view', name="logout"),
    #url(r'^test_recorder$', TemplateView.as_view(template_name='test_recorder.html')),
)

# password recovery URLs
urlpatterns += patterns('',
    url(r'^user/password/reset/$', 
        'django.contrib.auth.views.password_reset', 
        {'post_reset_redirect' : '/user/password/reset/done/', 'from_email': settings.SERVER_EMAIL},
        name="admin_password_reset"),
    (r'^user/password/reset/done/$',
        'django.contrib.auth.views.password_reset_done'),
    (r'^user/password/reset/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$', 
        'django.contrib.auth.views.password_reset_confirm', 
        {'post_reset_redirect' : '/user/password/done/'}),
    (r'^user/password/done/$', 
        'django.contrib.auth.views.password_reset_complete'),
)

## debug stuff to serve static media  TODO make sure this works in development
if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^' + settings.MEDIA_URL + r'(?P<path>.*)$', 'django.views.static.serve', 
            {'document_root': settings.MEDIA_ROOT}),
   )

#if settings.DEBUG:
#    import debug_toolbar
#    urlpatterns += patterns('',
#        url(r'^__debug__/', include(debug_toolbar.urls)),
#    )
