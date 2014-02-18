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

    url(r'^student/(?P<VKey>\d{10})/$', 'StudentLogin', name = "StudentLogin"),  #, student.views.StudentLogin),
    url(r'^student/video/(?P<ValKey>\d{10})&(?P<TID>\d{10})&(?P<PIID>\d{10})/$', 'StudentVideoInstance', name = "StudentVideoInstance"),  #, student.views.StudentVideoInstance),
    url(r'^student/response/(?P<ValKey>\d{10})&(?P<TID>\d{10})&(?P<PIID>\d{10})/$', 'StudentResponseInstance', name = "StudentResponceInstance"),  #, student.views.StudentResponseInstance),
    url(r'^student/submission/$', 'Submission', name = "Submission"),  #, student.views.Submission),
    url(r'^accounts/', include('django.contrib.auth.urls')),
    )


urlpatterns+=patterns('',
        url(r'^admin/', include(admin.site.urls))
                       )

#if settings.DEBUG:
#    import debug_toolbar
#    urlpatterns += patterns('',
#        url(r'^__debug__/', include(debug_toolbar.urls)),
#    )
