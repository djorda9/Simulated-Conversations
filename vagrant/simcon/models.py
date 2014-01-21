# Simulated Conversation Models
from django.db import models
from django.contrib.auth.models import User

# Create your models here. 
# NOTE(Nick):  spec refers to keeping the researcher ID, username, password 
#              in this model but it seems cleaner to use the existing 
#              auth model
class Researcher(models.Model):  
    user = models.ForeignKey (User)   # tie into auth user table
    authLevel = models.IntegerField("Authorization level", default=0) # authentication level
    
    def __unicode__(self):
        return u"Researcher: %s with authLevel: %d" % (self.user.username, self.authLevel)
       
    #following is the proposed permissions
    #class Meta:
    #permissions = (("can_add_researchers", "Can add researchers"),)

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
#       pageInstanceID  = models.ForeignKey(PageInstance) 
        conversationID  = models.ForeignKey(Conversation)
        order           = models.SmallIntegerField()
        choice          = models.CharField(max_length=1000)
        audioFile       = models.FileField(upload_to='test')
#       audioFile is tied to MEDIA_ROOT set in settings, to save in a
#       subdirectory within MEDIA_ROOT, set upload_to=$PATH.  
#       To do the madia management manually change this to a FilePathField 
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


class StudentAccess(models.Model):
    studentAccessID = models.AutoField(primary_key=True)
    templateID = models.ForeignKey('Template')
    researcherID = models.ForeignKey('Researcher')
    validationKey = models.CharField(max_length = 50)
    expirationDate = models.DateField()
    def __unicode__(self):
        return u'%s %s %s %s %s' % \
            (self.studentAccessID, self.templateID, 
             self.researcherID, self.validationKey, 
             self.expirationDate)

class Template(models.Model):
    # FIXME dummy template model to suppress warnings while integrating
    pass
