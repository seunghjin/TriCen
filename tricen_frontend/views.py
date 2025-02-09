from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.test import Client
from django.http import JsonResponse
import requests

def home(request):
    return render(request, 'home/index.html')    

def dashboard(request):
    url = reverse('conversation_list')
    client = Client()
    response = client.get(url)
    if response.status_code == 200:
        response_data = response.json()
    else:
        response_data = {'error': 'Failed to fetch conversations'}
    return render(request, 'dashboard/dashboard.html', {'conversations':response_data})
  
def user_detail(request, id):
    try:
        # Use Django test client to make internal request
        client = Client()
        url = reverse('conversation_details', args=[id])
        response = client.get(url)

        if response.status_code == 200:
            conversation_data = response.json()
            return render(request, 'user_detail/user_detail.html', {
                'user': conversation_data
            })
        elif response.status_code == 404:
            print(f"Conversation not found for ID: {id}")
            return HttpResponse("Conversation not found", status=404)
        else:
            print(f"Failed to fetch conversation details. Status code: {response.status_code}")
            return HttpResponse("Failed to fetch conversation details", status=500)

    except Exception as e:
        print(f"Error in user_detail view: {str(e)}")
        return HttpResponse("An unexpected error occurred", status=500)
