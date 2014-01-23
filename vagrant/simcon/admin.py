# researcher admin
import models
from django.contrib import admin
from django.contrib.auth.decorators import permission_required

# Custom model admins
# Note: flat admin may handle our mockups better
# TODO:  filter templates, responses, etc by user ownership, so they can only see things they own
#        make the things not needing a query a button on the template?
class TemplateAdmin(admin.ModelAdmin):
    actions = ['new_template', 'edit_template', 'share_template', 'generate_link']
    
    def new_template(self, request, queryset):
        pass
    new_template.short_description = "New Template >>"
    
    def edit_template(self, request, queryset):
        pass
    edit_template.short_description = "Edit template"
    
    def share_template(self, request, queryset):
        pass
    share_template.short_description = "Share these templates"
    
    def generate_link(self, request, queryset):
        pass
    generate_link.short_description = "Generate a link"
       
    
class ResearcherAdmin(admin.ModelAdmin):
    actions = ['promote_users']
    
    @permission_required('simcon.authLevel3') #TODO fix this
    def promote_users(self, request, queryset):
        pass
    promote_users.short_description = "Promote selected user(s)"
    
class ResponseAdmin(admin.ModelAdmin):
    actions = ['view_response']
    fields = ('order', 'choice')
    
    def view_response(self, request, queryset):
        pass
    view_response.short_description = "View selected response"

# register models and modeladmins
admin.site.register(models.Researcher, ResearcherAdmin)
admin.site.register(models.Template, TemplateAdmin)
admin.site.register(models.Response, ResponseAdmin)
