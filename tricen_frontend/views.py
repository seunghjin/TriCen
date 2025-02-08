from django.http import HttpResponse
from django.shortcuts import render
import requests

def dashboard(request):
    print("Request received!")
    responses = requests.get('https://dummyjson.com/users').json()
    return render(request, 'dashboard/index.html', {'responses':responses})