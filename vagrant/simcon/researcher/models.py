#researcher models
from django.db import models
from django.contrib.auth.models import User  # for User tie in

# Create your models here. 
# NOTE(Nick):  spec refers to keeping the researcher ID, username, password in this model
# but it seems cleaner to use the existing auth model
class Researcher (models.Model):  
    user = models.ForeignKey (User)   # tie into auth user table
    authLevel = models.IntegerField() # authentication level
    #TODO provide admin with a way of modifying this
    
    def __unicode__(self):
        return u"Researcher: %s with authLevel: %d" % (self.user.get_username(), self.authLevel)
        
