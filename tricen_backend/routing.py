from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/media/stream/(?P<call_sid>\w+)/$', consumers.AudioStreamConsumer.as_asgi()),
]