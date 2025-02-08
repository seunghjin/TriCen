from django.urls import path
from . import views

urlpatterns = [
    path('voice/incoming/', views.handle_incoming_call, name='handle_incoming_call'),
    path('voice/transcription_result/', views.handle_transcription_result, name='transcription_result'),
]