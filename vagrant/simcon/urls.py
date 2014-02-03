from django.conf.urls import patterns, include, url
#from django.conf import settings

from django.contrib import admin
admin.autodiscover()
   # Examples:
   # url(r'^$', 'simcon.views.home', name='home'),
   # url(r'^blog/', include('blog.urls')),
urlpatterns = patterns('simcon.views',
    url(r'^admin/template-wizard/$', 'TemplateWizard'),
    )
urlpatterns += patterns('simcon.views',
    url(r'^admin/template-wizard-include-left/$', 'TemplateWizardIncludeLeft'),
    )
urlpatterns += patterns('simcon.views',
    url(r'^admin/template-wizard-include-right/$', 'TemplateWizardIncludeRight'),
    )

urlpatterns += patterns('',
        url(r'^admin/', include(admin.site.urls))
    )



#if settings.DEBUG:
#    import debug_toolbar
#    urlpatterns += patterns('',
#        url(r'^__debug__/', include(debug_toolbar.urls)),
#    )
