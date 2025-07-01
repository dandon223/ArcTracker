from django.urls import path

from .api_views import PlayerAPIView

urlpatterns = [
    path("players/", PlayerAPIView.as_view(), name="players"),
]
