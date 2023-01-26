from django.shortcuts import render

# Create your views here.

def showHome(request):
    return render(request, 'home/home.html')