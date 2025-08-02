from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .api_views import (
    CardAPIView,
    CardPlayedInRoundAPIView,
    CardRetrievedSerializerAPIView,
    CardRevealedSerializerAPIView,
    CardUnrevealedSerializerAPIView,
    ChapterCreateAPIView,
    GameAPIView,
    GameRoundAPIView,
    LatestChapterAPIView,
    NumberOfCardsAddedSerializerAPIView,
    PlayerAPIView,
    RegisterAPIView,
    RoundCreateAPIView,
)

urlpatterns = [
    path("register/", RegisterAPIView.as_view(), name="register"),
    path("token/", TokenObtainPairView.as_view(), name="token-obtain-pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("cards/", CardAPIView.as_view(), name="cards"),
    path("players/", PlayerAPIView.as_view(), name="players"),
    path("games/", GameAPIView.as_view(), name="games"),
    path("games/<str:game_id>/game_rounds", GameRoundAPIView.as_view(), name="game-rounds"),
    path("games/<str:game_id>/rounds/create", RoundCreateAPIView.as_view(), name="create-round"),
    path("games/<str:game_id>/chapters/create", ChapterCreateAPIView.as_view(), name="create-chapter"),
    path("games/<str:game_id>/chapters/latest", LatestChapterAPIView.as_view(), name="latest-chapter"),
    path("games/<str:game_id>/players/<str:player_id>/hand/play", CardPlayedInRoundAPIView.as_view(), name="play-card"),
    path(
        "games/<str:game_id>/players/<str:player_id>/hand/add",
        NumberOfCardsAddedSerializerAPIView.as_view(),
        name="add-card",
    ),
    path(
        "games/<str:game_id>/players/<str:player_id>/hand/retrieve",
        CardRetrievedSerializerAPIView.as_view(),
        name="retrieve-card",
    ),
    path(
        "games/<str:game_id>/players/<str:player_id>/hand/reveal",
        CardRevealedSerializerAPIView.as_view(),
        name="reveal-card",
    ),
    path(
        "games/<str:game_id>/players/<str:player_id>/hand/unreveal",
        CardUnrevealedSerializerAPIView.as_view(),
        name="unreveal-card",
    ),
]
