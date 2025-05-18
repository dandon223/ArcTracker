from django.urls import path

from . import views

urlpatterns = [
    path("", views.menu, name="menu"),
    path("new_game/", views.new_game, name="new_game"),
    path("new_player/", views.new_player, name="new_player"),
    path("players/", views.players, name="players"),
    path("games/", views.games, name="games"),
    path("game/<str:game_id>/<int:game_chapter>/<int:game_round>", views.game, name="game"),
]
