# tests.py
from django.test import TestCase

from models import Researcher
from models import Template
from models import Conversation
from models import StudentAccess
from models import PageInstance
from models import Response
from models import SharedResponses
from models import TemplateResponseRel
from models import TemplateFlowRel

from model_mommy import mommy

from django.test import Client

import datetime

class ResearcherTestCase(TestCase):
    def setUp(self):
        self.adminuser = User.objects.create_user('admin1', 'admin1@test.com', 'pass1')
        self.adminuser.save()

        self.User = User.objects.create_user('admin2', 'admin2@test.com', 'pass2')
        self.User.save()

        self.client = Client()

# assert that adminuser is super researcher
# assert that user is researcher
# assert that username and password pair equates to a particular user

#template has foreign key to TemplateRel, TemplateRel has foreign key to Template? Which comes first?
class TemplateTestCase(TestCase):
    def setUp(self):
        Template.objects.create(templateID = 1, resercherID = 1, firstInstanceID = 1, shortDesc="This is the first template")
        Template.objects.create(templateID = 2, resercherID = 1, firstInstanceID = 5, shortDesc="This is the second template", version = 3)

        Template.objects.create(templateID = 3, resercherID = 2, firstInstanceID = 1, shortDesc="This is the third template", deleted = True)
        Template.objects.create(templateID = 4, resercherID = 2, firstInstanceID = 5, shortDesc="This is the fourth template", version = 2)

        self.client = Client()
# assert that template 2 is version 3
# assert that template 3 is deleted
# assert Template2.version() == 3?

#note: date time's are set to default, which is at the time of script running
class ConversationTestCase(TestCase):
    def setUp(self):
        Conversation.objects.create(templateID = 1, resercherID = 1, studentName = "Joseph", studentEmail = "Joe@fake.com")
        Conversation.objects.create(templateID = 2, resercherID = 1, studentName = "Rose")

        Conversation.objects.create(templateID = 3, resercherID = 2, studentName = "Henry", studentEmail = "Henry#fake.com")
        Conversation.objects.create(templateID = 4, resercherID = 2, studentName = "Ally")

        self.client = Client()
#assert that conversation 1 has student name Joseph

class StudentAccessTestCase(TestCase):
    def setUp(self):
        testDate = "2014-10-01 14:33"
#        StudentAccess.objects.create(studentAccessID = 1, templateID = 1, researcherID = 1, validationKey = "1234567890", expirationDate = datetime.datetime.strptime(testDate, "%Y-%m-%d %H:%M"))
#        StudentAccess.objects.create(studentAccessID = 2, templateID = 2, researcherID = 1, validationKey = "1234567890", expirationDate = datetime.datetime.strptime(testDate, "%Y-%m-%d %H:%M"))

#        StudentAccess.objects.create(studentAccessID = 3, templateID = 3, researcherID = 2, validationKey = "12345678", expirationDate = datetime.datetime.strptime(testDate, "%Y-%m-%d %H:%M"))
#        StudentAccess.objects.create(studentAccessID = 4, templateID = 4, researcherID = 2, validationKey = "12345678", expirationDate = datetime.datetime.strptime(testDate, "%Y-%m-%d %H:%M"))

        self.client = Client()
    def test_accesses_have_link(self):
        """Each access instance has a link associated with it"""
        firstAccess = mommy.make(Template)
        print(firstAccess.get_link('1234567890'))
        self.assertEqual(firstAccess.get_link('1234567890'), )

class PageInstanceTestCase(TestCase):
    def setUp(self):
        PageInstance.objects.create(PageInstanceID = 1, templateID = 1, videoOrResponse = "video", videoLink = "zJ8Vfx4721M", richText = "hey watch the video")
        PageInstance.objects.create(PageInstanceID = 2, templateID = 1, videoOrResponse = "response", richText = "hey select your response")
        PageInstance.objects.create(PageInstanceID = 3, templateID = 1, videoOrResponse = "video", videoLink = "zJ8Vfx4721M", richText = "hey watch this next video", enablePlayback = False)
        PageInstance.objects.create(PageInstanceID = 4, templateID = 1, videoOrResponse = "response", richText = "hey select your next response")
        PageInstance.objects.create(PageInstanceID = 5, templateID = 1, videoOrResponse = "video", videoLink = "zJ8Vfx4721M", richText = "hey watch the ending video")
        PageInstance.objects.create(PageInstanceID = 6, templateID = 1, videoOrResponse = "response", richText = "hey select your last response")

        PageInstance.objects.create(PageInstanceID = 7, templateID = 2, videoOrResponse = "video", videoLink = "zJ8Vfx4721M", richText = "hey watch this video")
        PageInstance.objects.create(PageInstanceID = 8, templateID = 2, videoOrResponse = "response", richText = "hey select your first response")
        PageInstance.objects.create(PageInstanceID = 9, templateID = 2, videoOrResponse = "video", videoLink = "zJ8Vfx4721M", richText = "hey watch the next video")
        PageInstance.objects.create(PageInstanceID = 10, templateID = 2, videoOrResponse = "response", richText = "hey select your subsequent response")

        self.client = Client()
# assert that page instance 5 is a video, and that it has a correct video link
# assert that page instance 10 is a response, and that it has a correct richtext

class ResponseTestCase(TestCase):
    def setUp(self):

#joseph
        with open('/response/1', 'w') as f:
            testFile = File(f)
            testFile.write('Hello World')
        testFile.closed
        f.closed
        Response.objects.create(PageInstanceID = 2, conversationID = 1, order = 1, choice = 1, audioFile = "/response/1")
        with open('/response/2', 'w') as f:
            testFile = File(f)
            testFile.write('Goodbye World')
        testFile.closed
        f.closed
        Response.objects.create(PageInstanceID = 4, conversationID = 1, order = 2, choice = 1, audioFile = "/response/2")
        with open('/response/3', 'w') as f:
            testFile = File(f)
            testFile.write('Where is the world')
        testFile.closed
        f.closed
        Response.objects.create(PageInstanceID = 6, conversationID = 1, order = 3, choice = 2, audioFile = "/response/3")
#rose
        with open('/response/4', 'w') as f:
            testFile = File(f)
            testFile.write('foo')
        testFile.closed
        f.closed
        Response.objects.create(PageInstanceID = 2, conversationID = 2, order = 1, choice = 2, audioFile = "/response/4")
        with open('/response/5', 'w') as f:
            testFile = File(f)
            testFile.write('bar')
        testFile.closed
        f.closed
        Response.objects.create(PageInstanceID = 4, conversationID = 2, order = 2, choice = 2, audioFile = "/response/5")
        with open('/response/6', 'w') as f:
            testFile = File(f)
            testFile.write('doo')
        testFile.closed
        f.closed
        Response.objects.create(PageInstanceID = 6, conversationID = 2, order = 3, choice = 1, audioFile = "/response/6")

        self.client = Client()
#assert that response has correct order, that audioFile exists and that it is what it's supposed to be.

class TemplateFlowRelTestCase(TestCase):
    def setUp(self):
        TemplateFlowRel.objects.create(TemplateFlowRelID = 1, templateID = 1, pageInstanceID = 1, nextPageInstanceID = 2)
        TemplateFlowRel.objects.create(TemplateFlowRelID = 1, templateID = 1, pageInstanceID = 2, nextPageInstanceID = 3)
        TemplateFlowRel.objects.create(TemplateFlowRelID = 1, templateID = 1, pageInstanceID = 2, nextPageInstanceID = 5)
        TemplateFlowRel.objects.create(TemplateFlowRelID = 1, templateID = 1, pageInstanceID = 3, nextPageInstanceID = 4)
        TemplateFlowRel.objects.create(TemplateFlowRelID = 1, templateID = 1, pageInstanceID = 5, nextPageInstanceID = 6)

        self.client = Client()
# assert what?

class SharedResponsesTestCase(TestCase):
    def setUp(self):
        SharedResponses.objects.create(SharedResponsesID = 1, responseID = 1, researcherID = 2)
        SharedResponses.objects.create(SharedResponsesID = 2, responseID = 2, researcherID = 2)

        self.client = Client()
#assert?

class TemplateResponseRelTestCase(TestCase):
    def setUp(self):
        TemplateResponseRel.objects.create(TemplateResponseRelID = 1, templateID = 1, pageInstanceID = 2, responseText = "Let's go to the park!", optionNumber = 1, nextPageInstanceID = 3)
        TemplateResponseRel.objects.create(TemplateResponseRelID = 2, templateID = 1, pageInstanceID = 2, responseText = "Let's stay inside!", optionNumber = 2, nextPageInstanceID = 5)

        self.client = Client()
#assert?