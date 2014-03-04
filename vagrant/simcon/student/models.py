from django.db import models
from django.contrib.auth.models import User
from template.models import Templates

class StudentAccess (models.Model):
    studentAccessID = AutoField(primary_key=True)
#    templateID = models.ForeignKey (Templates)
    researcherID = models.ForeignKey (User)
    validationKey = models.CharField(max_length = 50)
    expirationDate = models.DateField()
    def __unicode__(self):
        return u'%s %s %s %s %s' % (self.studentAccessID, self.templateID, self.researcherID, self.validationKey, self.expirationDate)