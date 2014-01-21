from django.db import models

# Note(Daniel): Implemented the SharedResponse class per the design spec.
class SharedResponses(models.Model):
    sharedResponseID = models.AutoField(primary_key=True)
    responseID = models.ForeignKey('response.Response')
    researcherID = models.ForeignKey('researcher.Researcher')
    dateTimeShared = models.DateTimeField(auto_now=True)

    # Note(Daniel): To insure that a response is only shared once with a researcher,
    # I used the unique_together to force this requirement on the responseID and
    # researcherID
    # Note - This requirement was not specified in the design spec.
    class Meta:
        unique_together = ("responseID", "researcherID")
