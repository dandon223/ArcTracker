from django.urls import path

from .api_views import GameAPIView, PlayerAPIView

urlpatterns = [
    path("players/", PlayerAPIView.as_view(), name="players"),
    path("games/", GameAPIView.as_view(), name="games"),
]
