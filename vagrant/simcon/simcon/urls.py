from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'simcon.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^student/(?P<ValKey>\d{10})&(?P<TID>\d{10})&(?P<PIID>\d{10})/$', student.views.StudentVideoInstance),
    url(r'^admin/', include(admin.site.urls)),
	url(r'^student/(?P<VKey>\d{10})/$', student.views.StudentLogin),
    url(r'^student/submission/$', student.views.Submission),

