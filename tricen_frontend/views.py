from django.http import HttpResponse
from django.shortcuts import render
import requests

def home(request):
    return render(request, 'home/index.html')    

def dashboard(request):
    responses = requests.get('https://dummyjson.com/users').json()
    return render(request, 'dashboard/dashboard.html', {'responses':responses})
  
def user_detail(request, id):
    responses = requests.get('https://dummyjson.com/users').json()
    user = None
    for i in responses['users']: 
        if i['id'] == id: 
            user = i
            break 
    if user is None:
        return HttpResponse("User not found", status=404)
    else:
        return render(request, 'user_detail/user_detail.html', {'user': user})
