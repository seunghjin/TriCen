from django.db import models
import json
import uuid

class CallTranscription(models.Model):
    call_sid = models.CharField(max_length=34)
    transcript = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_final = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['timestamp']

class Conversation(models.Model):
    caller_id = models.CharField(max_length=34, unique=True, primary_key=True)
    phone_number = models.CharField(max_length=20, null=True)
    contentUser = models.TextField()
    contentAI = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    needs_transfer = models.BooleanField(default=False)  # Added this line
    transfer_reason = models.TextField(null=True, blank=True)  # Added this line

    def set_user_content(self, messages_list):
        self.contentUser = json.dumps(messages_list)

    def get_user_content(self):
        return json.loads(self.contentUser) if self.contentUser else []

    def set_ai_content(self, messages_list):
        self.contentAI = json.dumps(messages_list)

    def get_ai_content(self):
        return json.loads(self.contentAI) if self.contentAI else []

    def add_user_message(self, message):
        messages = self.get_user_content()
        messages.append(message)
        self.set_user_content(messages)
        self.save()

    def add_ai_message(self, message):
        messages = self.get_ai_content()
        messages.append(message)
        self.set_ai_content(messages)
        self.save()

    def __str__(self):
        return f"{self.caller_id} - {self.timestamp}"