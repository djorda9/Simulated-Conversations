from django.conf.urls import patterns, include, url
#from django.conf import settings
from django.contrib import admin

from django.views.generic import TemplateView
admin.autodiscover()
   # Examples:
   # url(r'^$', 'simcon.views.home', name='home'),
   # url(r'^blog/', include('blog.urls')),
urlpatterns = patterns('simcon.views',
    url(r'^login/$', 'login_page', name="login"),
    url(r'^admin/template-wizard/$', 'TemplateWizard'),
    url(r'^generatelink/$', 'GenerateLink', name="GenerateLink"),
    url(r'^sharetemplate/$', 'ShareTemplate', name="ShareTemplate"),
    url(r'^shareresponse/$', 'ShareResponse', name="ShareResponse"),
    url(r'^links/$', 'Links', name="Links"),
    url(r'^responses/(\d+)$','Responses'),
    url(r'^studenttextchoice/$', 'StudentTextChoice', name = 'StudentTextChoice'),
    url(r'^studentinfo/$', 'StudentInfo', name = 'StudentInfo'),
    url(r'^student/(?P<VKey>\d{10})/$', 'StudentLogin', name = "StudentLogin"),
    url(r'^student/video/$', 'StudentVideoInstance', name = "StudentVideoInstance"),
    url(r'^student/response/$', 'StudentResponseInstance', name = "StudentResponseInstance"),
    url(r'^student/submission/$', 'Submission', name = "Submission"),
    url(r'^admin/template-delete/(\d+)$', 'TemplateDelete'),
    url(r'^admin/template-wizard/(\d+)$', 'TemplateWizardEdit'),
    url(r'^admin/template-wizard$', 'TemplateWizard'),
    url(r'^admin/template-wizard-save/$', 'TemplateWizardSave'),
    url(r'^admin/template-wizard-update', 'TemplateWizardUpdate'),
    url(r'^admin/template-wizard-left-pane', 'TemplateWizardLeftPane'),
    url(r'^admin/template-wizard-right-pane', 'TemplateWizardRightPane'),
    url(r'^admin/simcon/template/add/$', 'TemplateWizard'),
    url(r'^tinymce/', include('tinymce.urls')),
    url(r'^admin/superuser', include(admin.site.urls)),
    url(r'^admin/$', 'ResearcherView'),
    url(r'^admin/simcon/conversation/(\d+)', 'Responses'),
    url(r'^audio/save$', 'saveAudio'),
    url(r'^test_recorder$', TemplateView.as_view(template_name='test_recorder.html')),
)

# password recovery URLs
urlpatterns += patterns('',
    url(r'^user/password/reset/$', 
        'django.contrib.auth.views.password_reset', 
        {'post_reset_redirect' : '/user/password/reset/done/'},
        name="admin_password_reset"),
    (r'^user/password/reset/done/$',
        'django.contrib.auth.views.password_reset_done'),
    (r'^user/password/reset/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$', 
        'django.contrib.auth.views.password_reset_confirm', 
        {'post_reset_redirect' : '/user/password/done/'}),
    (r'^user/password/done/$', 
        'django.contrib.auth.views.password_reset_complete'),
)

#if settings.DEBUG:
#    import debug_toolbar
#    urlpatterns += patterns('',
#        url(r'^__debug__/', include(debug_toolbar.urls)),
#    )

