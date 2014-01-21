from django.db import models


####NOTE#####	-Griff
#This does not align exactly with the database example in the spec (as of v.2)
#response metadata is no longer in pageInstance but split into a separate
# db called "conversation"
#
#correct db outline is as follows:
#response:
#	responseID
#	pageInstanceID	-foreign key to page instance 1:1
#						(still refers to pageinstance, not conversation)
#	conversationID	-foreign key to conversation many:1
#	order			-position within the conversation response
#							(I am the nth answer)
#	choice			-sentence the student chose to describe answer
#	audioFile		-path to audio file
#
#
#conversation:
#	conversationID
#	templateID-		the related template
#	researcherID-	researcher that owns the template (redundant)
#	studentName-	whatever the student provides
#	studentEmail-	"				"
#	dateTime-		start time for the conversation (sets automatically)


####remember to uncomment foreign key entries as models are added####
class Conversation(models.Model):
#	templateID		=	models.ForeignKey(Templates)
	researcherID	=	models.ForeignKey('researcher.Researcher')
	studentName		=	models.CharField(max_length=50)
	studentEmail	=	models.EmailField(max_length=254)
	dateTime		=	models.DateTimeField(auto_now_add=True)
			#dateTime sets automatically on creation
			
	def __unicode__(self):
		return u" %s: %s" % (str(self.dateTime), self.studentName)
	
				
class Response(models.Model):
#	pageInstanceID	=	models.ForeignKey(PageInstance) 
	conversationID	=	models.ForeignKey(Conversation)
	order			=	models.SmallIntegerField()
	choice			=	models.CharField(max_length=1000)
	audioFile 		= 	models.FileField(upload_to='test')
#	audioFile is tied to MEDIA_ROOT set in settings, to save in a subdirectory
# 	within MEDIA_ROOT, set upload_to=$PATH.  To do the madia management 
#	manually change this to a FilePathField 

	def __unicode__(self):
		return u"%d: %s" %(self.order, self.choice)
