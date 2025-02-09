from django.urls import path
from . import views

urlpatterns = [
    path('voice/incoming/', views.handle_incoming_call, name='handle_incoming_call'),
    path('voice/transcription_result/', views.handle_transcription_result, name='transcription_result'),
    path('voice/audio/<str:filename>', views.serve_audio, name='serve_audio'),
    path('conversations/', views.get_conversations, name='conversation_list'),
    path('conversation_details/<str:caller_id>', views.get_conversation, name='conversation_details'),
    path('transfer/<str:call_sid>/', views.initiate_transfer, name='initiate_transfer'),
]