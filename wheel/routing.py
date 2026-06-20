from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # Route pointing both player wheels and super user controls to the same coordinator consumer
    re_path(r'ws/wheel/$', consumers.WheelConsumer.as_asgi()),
]