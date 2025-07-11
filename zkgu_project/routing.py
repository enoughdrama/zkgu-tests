from django.urls import re_path
from ..zkgu_persons import consumers

websocket_urlpatterns = [
    re_path(r'ws/person-updates/$', consumers.PersonUpdatesConsumer.as_asgi()),
]