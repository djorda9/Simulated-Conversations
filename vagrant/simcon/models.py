# Simulated Conversation Models
from django.db import models
from django.contrib.auth.models import User
<<<<<<< HEAD
from django.conf import settings
from django.core.files import File
import datetime
=======
from tinymce.models import HTMLField  # tinymce for rich text embeds
>>>>>>> nate

class Researcher (models.Model):  
    user = models.OneToOneField (User)   # tie into auth user table
    
    def __unicode__(self):
        if self.user.has_perm('simcon.authLevel2'):
            return u"Super Researcher: %s" % self.user.username
        elif self.user.has_perm('simcon.authLevel1'):
            return u"Researcher: %s" % self.user.username
        else:
            return u"Not a researcher: %s" % self.user.username
       
    class Meta:
        permissions = (("authLevel1", "Normal researcher"),
                       ("authLevel2", "Can create and delete researchers"),
                       ("authLevel3", "Can promote other researchers to authLevel2")) # may want this to reduce runaway super user creation, can be ignored
                       
        # NOTE: a common pattern is to use a decorator as follows:
        # from django.contrib.auth.decorators import permission_required
        # @permission_required('researcher.authLevel2')
        # def my_view_requiring_authLevel2(request):

####NOTE#####   -Griff
#This does not align exactly with the database example in the spec (as of v.2)
#response metadata is no longer in pageInstance but split into a separate
# db called "conversation"
#
#correct db outline is as follows:
#response:
#       responseID
#       pageInstanceID  -foreign key to page instance 1:1
#               (still refers to pageinstance, not conversation)
#       conversationID  -foreign key to conversation many:1
#       order                   -position within the conversation response
#               (I am the nth answer)
#       choice                  -sentence the student chose to describe answer
#       audioFile               -path to audio file
#
#
#conversation:
#       conversationID
#       templateID- the related template
#       researcherID- researcher that owns the template (redundant)
#       studentName- whatever the student provides
#       studentEmail- "                         "
#       dateTime- start time for the conversation (sets automatically)


####remember to uncomment foreign key entries as models are added####
class Conversation(models.Model):
        templateID      = models.ForeignKey('Template')
        researcherID    = models.ForeignKey('Researcher')
        studentName     = models.CharField(max_length=50)
        studentEmail    = models.EmailField(max_length=254)
        dateTime        = models.DateTimeField(auto_now_add=True)

        def __unicode__(self):
                return u" %s: %s" % (str(self.dateTime), self.studentName)
        
class Response(models.Model):
        pageInstanceID  = models.ForeignKey(PageInstance) 
        conversationID  = models.ForeignKey(Conversation)
        order           = models.SmallIntegerField()
        choice          = models.CharField(max_length=1000)
        audioFile       = models.FileField(upload_to='test')
#       audioFile is tied to MEDIA_ROOT set in settings, to save in a
#       subdirectory within MEDIA_ROOT, set upload_to=$PATH.  
#       To do the madia management manually change this to assume ( FilePathField );
        def __unicode__(self):
                return u"%d: %s" % (self.order, self.choice)


# Note(Daniel): Implemented the SharedResponse class per the design spec.
class SharedResponses(models.Model):
    sharedResponseID = models.AutoField(primary_key=True)
    responseID = models.ForeignKey('Response')
    researcherID = models.ForeignKey('Researcher')
    dateTimeShared = models.DateTimeField(auto_now=True)

    # Note(Daniel): To insure that a response is only shared once
    # with a researcher, I used the unique_together to force this 
    # requirement on the responseID and researcherID
    # Note - This requirement was not specified in the design spec.
    class Meta:
        unique_together = ("responseID", "researcherID")

    def __unicode__(self):
        return '%s' % self.sharedResponseID

#The validationKey must be unique to allow the Student Login page to look up the templateID by validation key
class StudentAccess(models.Model):
    studentAccessID = models.AutoField(primary_key=True)
    templateID 		= models.ForeignKey('Template')
    researcherID 	= models.ForeignKey('Researcher')
    validationKey 	= models.CharField(max_length = 50)
    expirationDate 	= models.DateField()
    
    def __unicode__(self):
        return u'%s %s %s %s %s' % \
            (self.studentAccessID, self.templateID, 
             self.researcherID, self.validationKey, 
             self.expirationDate)

    # Returns a url for the student login page with the passed 'key'.
    def get_link(self, key):
        student_site = "/student/"
        return settings.SITE_ID + student_site + key + "/"

    #Returns a url for the student login page without a key passed.
    def get_base_link(self):
        student_site = "/student/"
        return settings.SITE_ID + student_site

#Templates: a list of templates and who they belong to. The firstInstanceID points to a 
#templateFlowRelID which is the first video in the template. Deleted refers to if a template was deleted.
#Version refers to template version
class Template(models.Model):
    templateID      = models.AutoField(primary_key = True)
    researcherID    = models.ForeignKey(Researcher)
    firstInstanceID = models.ForeignKey("TemplateFlowRel", blank=True, null=True)
    shortDesc       = models.TextField()
    deleted         = models.BooleanField(default = False)   # whether or not this template has been deleted
    version         = models.IntegerField(default = 1)    # particular version of this template, base 1
    
    def __unicode__(self):
        if self.version > 1:
            return u"%s Version: %d" % (self.shortDesc, self.version)
        else:
            return u"%s" % self.shortDesc
            
#PageInstance: this relates videos or responses to a template. The template is referenced by
#templateID and researcherID. videoOrResponse tells you whether it's a VIDEO INSTANCE or a 
#RESPONSE INSTANCE, by literally video or response. If its a video, it will have a videoLink 
#and richText, with enablePlayback as a boolean that can enable or disable the video playback buttons. 
#If it's a response instance, these values will be blank.
class PageInstance(models.Model):
    pageInstanceID  = models.AutoField(primary_key = True)
    templateID      = models.ForeignKey(Template, blank=True, null=True)
    videoOrResponse = models.CharField(max_length = 8, default = "response") #considering omitting this and just using videoLink to determine variety...
    videoLink       = models.CharField(max_length = 11, null = True)  # this will store the alphanumberic code of a url such as: http://img.youtube.com/vi/zJ8Vfx4721M
    #richText        = models.TextField()    # NOTE:  this has to store raw html
    richText        = HTMLField() # rich text field
    enablePlayback  = models.BooleanField(default = True)
    
    def __unicode__(self):
        if self.videoOrResponse == "video":  # consider change this to query videoLink not null?
            return u"Video instance"
        else:
            return u"Response instance"

    def get_pageInstanceID(self):
        return self.pageInstanceID

#TemplateResponseRel: this relates the several possible responses to one pageInstanceID, ordered by 
# optionNumber. If the pageInstance is a response, the next page instance will be referenced here.
class TemplateResponseRel(models.Model):
    templateResponseRelID = models.AutoField(primary_key = True)
    templateID            = models.ForeignKey(Template)
    pageInstanceID        = models.ForeignKey(PageInstance, related_name='templateresponserel_page') # id of dummy page
    responseText          = models.TextField()
    optionNumber          = models.IntegerField(default = 1)
    nextPageInstanceID    = models.ForeignKey(PageInstance, blank=True, null=True, related_name='templateresponserel_nextpage' )
    
    def __unicode__(self):
        return u"Template response relation for template: %s" % self.templateID.shortDesc

#TemplateFlowRel: this determines how the template will flow. A template is referenced by
# templateID and researcherID. The first page in the flow will be determined by the 
# Templates table, and each page after that can be looked up by referencing pageInstanceID
# and the corresponding nextPageInstanceID, but only if it's a video. If it's a response,
# you need to look up the nextPageInstanceID based on which optionNumber it is in the TemplateReponseRel table.
class TemplateFlowRel(models.Model):
    templateFlowRelID  = models.AutoField(primary_key = True)
    templateID         = models.ForeignKey(Template, blank=True, null=True)
    pageInstanceID     = models.ForeignKey(PageInstance, blank=True, null=True, related_name='templateflowrel_page')
    nextPageInstanceID = models.ForeignKey(PageInstance, default=None, blank=True, null=True, related_name='templateflowrel_nextpage')
      
    def __unicode__(self):
        return u"Template flow relation for template: %s" % self.templateID.shortDesc

    def curr_page(self):
        return self.pageInstanceID

    def nex_page(self):
        return self.nextPageInstanceID
