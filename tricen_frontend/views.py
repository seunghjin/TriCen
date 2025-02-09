from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.test import Client
from django.http import JsonResponse
import requests

from tricen_backend.models import Conversation

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
        conversation = Conversation.objects.get(caller_id=id)
        
        # Get the user and AI content
        user_content = conversation.get_user_content()
        ai_content = conversation.get_ai_content()

        client = Client()
        url = reverse('conversation_details', args=[id])
        response = client.get(url)

        if response.status_code == 200:
            response_data = response.json()
        elif response.status_code == 404:
            print(f"Conversation not found for ID: {id}")
            return HttpResponse("Conversation not found", status=404)
        else:
            print(f"Failed to fetch conversation details. Status code: {response.status_code}")
            return HttpResponse("Failed to fetch conversation details", status=500)

        
        # Zip the messages together for easy templating
        messages = list(zip(user_content, ai_content))
        
        conversation_data = {
            'caller_id': conversation.caller_id,
            'phone_number': conversation.phone_number,
            'messages': messages,
            'timestamp': conversation.timestamp,
            'small_description': response_data['small_description'],
            'summary': response_data['summary'],
            'name': response_data['name'],
        }
        
        return render(request, 'user_detail/user_detail.html', {
            'conversation': conversation_data
        })
    except Conversation.DoesNotExist:
        print(f"Conversation not found for ID: {id}")
        return HttpResponse("Conversation not found", status=404)
    except Exception as e:
        print(f"Error in user_detail view: {str(e)}")
        return HttpResponse("An unexpected error occurred", status=500)