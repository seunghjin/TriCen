from django.http import HttpResponse
from django.shortcuts import render


def dashboard(request):
    print("Request received!")
    return render(request, 'dashboard/index.html')