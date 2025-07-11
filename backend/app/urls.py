from django.urls import include, path

from . import views

urlpatterns = [
    path("", views.menu_view, name="menu"),
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("user_menu/", views.user_menu_view, name="user_menu"),
    path("new_game/", views.new_game_view, name="new_game"),
    path("new_player/", views.new_player_view, name="new_player"),
    path("players/", views.players_view, name="players"),
    path("games/", views.games_view, name="games"),
    path("game/<str:game_id>/<int:chapter_number>/<int:round_number>", views.current_game_view, name="current_game"),
    path(
        "game/<str:game_id>/<int:chapter_number>/<int:round_number>/<str:player_id>",
        views.new_action_view,
        name="new_action",
    ),
    path("api/", include("app.api_urls")),
    path("api-auth/", include("rest_framework.urls")),
]
