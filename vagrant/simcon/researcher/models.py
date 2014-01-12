#researcher models
from django.db import models
from django.contrib.auth.models import User  # for User tie in

# Create your models here. 
# NOTE(Nick):  spec refers to keeping the researcher ID, username, password in this model
# but it seems cleaner to use the existing auth model
class Researcher (models.Model):  
    user = models.ForeignKey (User)   # tie into auth user table
    authLevel = models.IntegerField("Authorization level", default=0) # authentication level
    
    def __unicode__(self):
        return u"Researcher: %s with authLevel: %d" % (self.user.username, self.authLevel)
       
    #following is the proposed permissions
    #class Meta:
        #permissions = (("can_add_researchers", "Can add researchers"),)