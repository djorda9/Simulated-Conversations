# admin
import models
from django.contrib import admin
from django.contrib.auth.decorators import permission_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse

from django.shortcuts import redirect, render_to_response, render
        
import logging
logger = logging.getLogger("simcon")

admin.site.disable_action('delete_selected') # remove the default delete site-wide
# Custom model admins
# Note: flat admin may handle our mockups better
# TODO:  filter templates, responses, etc by user ownership, so they can only see things they own
class TemplateAdmin(admin.ModelAdmin):
    actions = ['edit_template', 'share_template', 'generate_link', 'delete_template']
    
    def edit_template(self, request, queryset):
        "Edit the selected template"   
        if not queryset or queryset.count() != 1: #We can edit only 1 template
            self.message_user(request, "Can't edit more than 1 template at a time")
        else:
            temp = queryset[0]
            if not request.user.is_superuser and temp.researcherID != request.user:
                self.message_user(request, "Can't edit that")#raise PermissionDenied
            else:
                #self.message_user(request, "Edit template %s with %d items" % (request.user.username, queryset.count()))
                #self.message_user(request, "Editing template!")

                #TODO pump queryset into session, tag to add a version incrementation, maybe have a template id variable?
                #return render(request, 'template-wizard.html', {"template_to_edit": temp.templateID})
                return HttpResponseRedirect(reverse('simcon.views.TemplateDelete'), args=1)#(temp.templateID))

    edit_template.short_description = "Edit template"
    
    def delete_template(self, request, queryset):
        "Edit the selected template"   
        if not queryset or queryset.count() != 1:
            self.message_user(request, "Can't delete more than 1 template at a time")
        else:
            temp = queryset[0]
            if not request.user.is_superuser and temp.researcherID != request.user:
                self.message_user(request, "Can't delete that")#raise PermissionDenied
            else:
                #self.message_user(request, "Edit template %s with %d items" % (request.user.username, queryset.count()))
                #self.message_user(request, "Editing template!")

                #TODO pump queryset into session, tag to add a version incrementation, maybe have a template id variable?
                return render(request, 'template-delete.html', {"template_to_delete": temp.templateID})
    delete_template.short_description = "Delete template"
    
    def share_template(self, request, queryset):
        "Share the selected template(s)"
        self.message_user(request, "Not implemented")
        
        # FIXME raise PermissionDenied if we share someone else's template
    share_template.short_description = "Share these templates"
    
    def generate_link(self, request, queryset):
        "Generate a link for the selected template(s)"
        self.message_user(request, "Not implemented")
         # FIXME raise PermissionDenied if we generate a link to someone
         # else's Conversation


    generate_link.short_description = "Generate a link"
       
    
# register models and modeladmins
admin.site.register(models.Template, TemplateAdmin)

#temporarily adding all
admin.site.register(models.Conversation)
admin.site.register(models.SharedResponses)
admin.site.register(models.StudentAccess)
admin.site.register(models.PageInstance)
admin.site.register(models.TemplateResponseRel)
admin.site.register(models.TemplateFlowRel)

