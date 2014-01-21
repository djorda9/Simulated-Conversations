from django.shortcuts import render

def Submission(request):
    return render(request, 'Student_Submission.html')

def Login(request):
    return render(request, 'Student_Login.html')
