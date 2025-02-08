from django.db import models

class CallTranscription(models.Model):
    call_sid = models.CharField(max_length=34)
    transcript = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_final = models.BooleanField(default=False)

    class Meta:
        ordering = ['timestamp']