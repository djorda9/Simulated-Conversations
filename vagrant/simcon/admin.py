# researcher admin
import models
from django.contrib import admin
from django.contrib.auth.decorators import permission_required

# Custom model admins
# Note: flat admin may handle our mockups better
# TODO:  filter templates, responses, etc by user ownership, so they can only see things they own
class TemplateAdmin(admin.ModelAdmin):
    actions = ['edit_template', 'share_template', 'generate_link']
    
    #@permission_required('simcon.authLevel1') #TODO fix this
    def edit_template(self, request, queryset):
        "Edit the selected template"
        
        self.message_user(request, "Edit template %s with %d items" % (request.user.username, queryset.objects.all().aggregate(Count('templateID'))))
        #TODO redirect to template_wizard, increment a version
    edit_template.short_description = "Edit template"
    
    @permission_required('simcon.authLevel1') #TODO fix this
    def share_template(self, request, queryset):
        "Share the selected template(s)"
        pass
    share_template.short_description = "Share these templates"
    
    @permission_required('simcon.authLevel1') #TODO fix this
    def generate_link(self, request, queryset):
        "Generate a link for the selected template(s)"
        pass
    generate_link.short_description = "Generate a link"
       
    
class ResearcherAdmin(admin.ModelAdmin):
    actions = ['promote_users']
    
    @permission_required('simcon.authLevel3') #TODO fix this
    def promote_users(self, request, queryset):
        "Promote the selected researcher(s)"
        pass
    promote_users.short_description = "Promote selected user(s)"
    
class ResponseAdmin(admin.ModelAdmin):
    actions = ['view_response']  #TODO does adding a response make any sense?  probably should be disabled
    fields = ('order', 'choice')
    
    def view_response(self, request, queryset):
        "View the selected response(s)"
        pass
    view_response.short_description = "View selected response"

# register models and modeladmins
admin.site.register(models.Researcher, ResearcherAdmin)
admin.site.register(models.Template, TemplateAdmin)
admin.site.register(models.Response, ResponseAdmin)

#temporarily adding all
admin.site.register(models.Conversation)
admin.site.register(models.SharedResponses)
admin.site.register(models.StudentAccess)
admin.site.register(models.PageInstance)
admin.site.register(models.TemplateResponseRel)
admin.site.register(models.TemplateFlowRel)
