from django.urls import path

from . import views

urlpatterns = [
    path("", views.menu, name="menu"),
    path("new_game/", views.new_game, name="new_game"),
    path("game/<str:id>/", views.game, name="game"),
]