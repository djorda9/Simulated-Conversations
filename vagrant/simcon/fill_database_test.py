# Jason Nelson
# Simulated Conversations
# This script automatically fills the various data tables in the SimCom project with test data

from django.db import models
import datetime
from django.core.files import File

from simcom.models import *

#auth user table?
T = Researcher(user='Researcher1', authLevel='0')
T.save()
T = Researcher(user='Researcher2', authLevel='1')
T.save()
T = Researcher(user='Researcher3', authLevel='0')
T.save()
T = Researcher(user='Researcher4', authLevel='0')
T.save()

testDate = "2014-10-01 14:33"
T = Conversation(templateID=1,researcherID='Researcher1', studentName = 'Billy', studentEmail = 'example@fake.com', dateTime = datetime.datetime.strptime(testDate, "%Y-%m-%d %H:%M"))
T.save()
testDate = "2013-9-03 9:12"
T = Conversation(templateID=1,researcherID='Researcher1', studentName = 'Bob', studentEmail = '', dateTime = datetime.datetime.strptime(testDate, "%Y-%m-%d %H:%M"))
T.save()
testDate = "2014-11-02 11:00"
T = Conversation(templateID=2,researcherID='Researcher2', studentName = 'Billy', studentEmail = 'stuff@fake.com', dateTime = datetime.datetime.strptime(testDate, "%Y-%m-%d %H:%M"))
T.save()
testDate = "2013-6-04 2:10"
T = Conversation(templateID=3,researcherID='Researcher2', studentName = 'Ron', studentEmail = 'notreal@nope.com', dateTime = datetime.datetime.strptime(testDate, "%Y-%m-%d %H:%M"))
T.save()

with open('/the/address', 'w') as f:
    testFile = File(f)
    testFile.write('Hello World')
testFile.closed
f.closed
T = Response(conversationID='1', order = 1, choice = 'Lets go to the park!', audioFile = '/the/address')
T.save()
with open('/the/other/address', 'w') as f:
    testFile = File(f)
    testFile.write('I am world destroyer')
testFile.closed
f.closed
T = Response(conversationID='2', order = 2, choice = 'Ill go onto the Internet!', audioFile = '/the/other/address')
T.save()
with open('/the/address', 'w') as f:
    testFile = File(f)
    testFile.write('Hello World')
testFile.closed
f.closed
T = Response(conversationID='1', order = 1, choice = 'Lets go to the park!', audioFile = '/the/address')
T.save()
with open('/the/different/address', 'w') as f:
    testFile = File(f)
    testFile.write('How are you?')
testFile.closed
f.closed
T = Response(conversationID='4', order = 2, choice = 'How about the pub?', audioFile = '/the/different/address')
T.save()

testDate = "2017-8-08 8:08"
T = SharedResponses(sharedResponseID=1, responseID = '1', researcherID = 'Researcher1', dateTimeShared = datetime.datetime.strptime(testDate, "%Y-%m-%d %H:%M"))
T.save()
testDate = "2016-1-01 1:01"
T = SharedResponses(sharedResponseID=2, responseID = '2', researcherID = 'Researcher2', dateTimeShared = datetime.datetime.strptime(testDate, "%Y-%m-%d %H:%M"))
T.save()
testDate = "2015-9-17 7:08"
T = SharedResponses(sharedResponseID=3, responseID = '1', researcherID = 'Researcher3', dateTimeShared = datetime.datetime.strptime(testDate, "%Y-%m-%d %H:%M"))
T.save()
testDate = "2018-9-22 2:22"
T = SharedResponses(sharedResponseID=4, responseID = '1', researcherID = 'Researcher4', dateTimeShared = datetime.datetime.strptime(testDate, "%Y-%m-%d %H:%M"))
T.save()

testDate = "2011-2-22 18:00"
T = StudentAccess(studentAccessID=1, researcherID = 'Researcher1', validationKey = '1234567890', expirationDate = datetime.datetime.strptime(testDate, "%Y-%m-%d %H:%M"))
T.save()
testDate = "2011-3-30 16:33"
T = StudentAccess(studentAccessID=2, researcherID = 'Researcher2', validationKey = '2345678901', expirationDate = datetime.datetime.strptime(testDate, "%Y-%m-%d %H:%M"))
T.save()
testDate = "2016-6-5 18:00"
T = StudentAccess(studentAccessID=3, researcherID = 'Researcher3', validationKey = '3456789012', expirationDate = datetime.datetime.strptime(testDate, "%Y-%m-%d %H:%M"))
T.save()
testDate = "2017-7-10 16:33"
T = StudentAccess(studentAccessID=4, researcherID = 'Researcher4', validationKey = '4567890123', expirationDate = datetime.datetime.strptime(testDate, "%Y-%m-%d %H:%M"))
T.save()

T = Template(templateID = 1, researcherID = researcher1, firstInstanceID = 1, shortDesc = "let's go to the park", deleted = false, version = 1)
T.save()
T = Template(templateID = 2, researcherID = researcher2, firstInstanceID = 2, shortDesc = "let's not", deleted = false, version = 2)
T.save()
T = Template(templateID = 3, researcherID = researcher3, firstInstanceID = 3, shortDesc = "How are you?", deleted = false, version = 1)
T.save()
T = Template(templateID = 4, researcherID = researcher4, firstInstanceID = 4, shortDesc = "bring cookies on Monday", deleted = false, version = 3)
T.save()


T = PageInstance(pageInstanceID = 1, templateID = 1, videoOrResponse = "response", videoLink = zJ8Vfx4721M, richText = "hello", enablePlayback = True)
T.save()
T = PageInstance(pageInstanceID = 2, templateID = 2, videoOrResponse = "video", videoLink = zJ8Vfx4721M, richText = "goodbye", enablePlayback = True)
T.save()
T = PageInstance(pageInstanceID = 3, templateID = 3, videoOrResponse = "response", videoLink = zJ8Vfx4721M, richText = "this", enablePlayback = False)
T.save()
T = PageInstance(pageInstanceID = 4, templateID = 4, videoOrResponse = "video", videoLink = zJ8Vfx4721M, richText = "that", enablePlayback = False)
T.save()

T = TemplateResponseRel(templateResponseRelID = 1, templateID = 1, pageInstanceID = 1, responseText = "who", optionNumber = 1, nextPageInstanceID = 1)
T.save()
T = TemplateResponseRel(templateResponseRelID = 2, templateID = 2, pageInstanceID = 2, responseText = "what", optionNumber = 2, nextPageInstanceID = 1)
T.save()
T = TemplateResponseRel(templateResponseRelID = 3, templateID = 3, pageInstanceID = 3, responseText = "where", optionNumber = 3, nextPageInstanceID = 1)
T.save()
T = TemplateResponseRel(templateResponseRelID = 4, templateID = 4, pageInstanceID = 4, responseText = "when", optionNumber = 4, nextPageInstanceID = 1)
T.save()