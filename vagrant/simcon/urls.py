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

#this is used to do the behind-the-scenes stuff on the 
#  conversation template wizard...update session variables
urlpatterns += patterns('simcon.views',
        url(r'^admin/template-wizard-update', 'TemplateWizardUpdate')
    )

#this is used to do the behind-the-scenes stuff on the
#  conversation template wizard...reload the left pane
urlpatterns += patterns('simcon.views',
        url(r'^admin/template-wizard-left-pane', 'TemplateWizardLeftPane')
    )

#this is used to do the behind-the-scenes stuff on the
#  conversation template wizard...reload the right pane
urlpatterns += patterns('simcon.views',
        url(r'^admin/template-wizard-right-pane', 'TemplateWizardRightPane')
    )


urlpatterns += patterns('',
        url(r'^admin/', include(admin.site.urls))
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
