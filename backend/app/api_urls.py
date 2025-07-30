from django.urls import path

from .api_views import (
    CardPlayedInRoundAPIView,
    ChapterCreateAPIView,
    GameAPIView,
    GameRoundAPIView,
    LatestChapterAPIView,
    PlayerAPIView,
    RoundCreateAPIView,
)

urlpatterns = [
    path("players/", PlayerAPIView.as_view(), name="players"),
    path("games/", GameAPIView.as_view(), name="games"),
    path("games/<str:game_id>/rounds", GameRoundAPIView.as_view(), name="game-rounds"),
    path("games/<str:game_id>/new_round", RoundCreateAPIView.as_view(), name="create-round"),
    path("games/<str:game_id>/new_chapter", ChapterCreateAPIView.as_view(), name="create-chapter"),
    path("games/<str:game_id>/played_cards", CardPlayedInRoundAPIView.as_view(), name="played-cards"),
    path("games/<str:game_id>/latest_chapter", LatestChapterAPIView.as_view(), name="latest-chapter"),
]
