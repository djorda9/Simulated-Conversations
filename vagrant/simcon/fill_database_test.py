# Jason Nelson
# Simulated Conversations
# This script automatically fills the various data tables in the SimCom project with test data

from django.db import models
import datetime
from django.core.files import File

from researcher.models import Researcher
#from template.models import Templates
from student.models import StudentAccess
from response.models import Conversation
from response.models import Response
from sharedresponses.models import SharedResponses

#auth user table?
T = Researcher(user='Researcher1', authLevel='0')
T.save()
T = Researcher(user='Researcher2', authLevel='1')
T.save()

testDate = "2014-10-01 14:33"
T = Conversation(researcherID='Researcher1', studentName = 'Billy', studentEmail = 'example@fake.com', dateTime = datetime.datetime.strptime(testDate, "%Y-%m-%d %H:%M"))
T.save()
testDate = "2013-9-01 9:12"
T = Conversation(researcherID='Researcher2', studentName = 'Bob', studentEmail = '', dateTime = datetime.datetime.strptime(testDate, "%Y-%m-%d %H:%M"))
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
T = Response(conversationID='2', order = 4, choice = 'Ill go onto the Internet!', audioFile = '/the/other/address')
T.save()

testDate = "2017-8-08 8:08"
T = SharedResponses(sharedResponseID=1, responseID = '1', researcherID = 'Researcher1', dateTime = datetime.datetime.strptime(testDate, "%Y-%m-%d %H:%M"))
T.save()

testDate = "2016-1-01 1:01"
T = SharedResponses(sharedResponseID=2, responseID = '2', researcherID = 'Researcher2', dateTime = datetime.datetime.strptime(testDate, "%Y-%m-%d %H:%M"))
T.save()

testDate = "2011-2-22 18:00"
T = StudentAccess(studentAccessID=1, researcherID = 'Researcher1', validationKey = 'supervalidkey111', expirationDate = datetime.datetime.strptime(testDate, "%Y-%m-%d %H:%M"))
T.save()

testDate = "2011-3-30 16:33"
T = StudentAccess(studentAccessID=2, researcherID = 'Researcher2', validationKey = 'supervalidkey222', expirationDate = datetime.datetime.strptime(testDate, "%Y-%m-%d %H:%M"))
T.save()