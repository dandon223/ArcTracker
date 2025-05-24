from django.urls import path

from . import views

urlpatterns = [
    path("", views.menu, name="menu"),
    path("new_game/", views.new_game, name="new_game"),
    path("new_player/", views.new_player, name="new_player"),
    path("players/", views.players, name="players"),
    path("games/", views.games, name="games"),
    path("game/<str:game_id>/<int:chapter_number>/<int:round_number>", views.current_game, name="game"),
    path(
        "game/<str:game_id>/<int:chapter_number>/<int:round_number>/<str:player_id>",
        views.new_action,
        name="new_action",
    ),
]
