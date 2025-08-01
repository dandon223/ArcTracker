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
    path("games/<str:game_id>/rounds", GameRoundAPIView.as_view(), name="game-rounds"),
    path("games/<str:game_id>/new_round", RoundCreateAPIView.as_view(), name="create-round"),
    path("games/<str:game_id>/new_chapter", ChapterCreateAPIView.as_view(), name="create-chapter"),
    path("games/<str:game_id>/played_cards", CardPlayedInRoundAPIView.as_view(), name="played-cards"),
    path("games/<str:game_id>/retrieved_cards", CardRetrievedSerializerAPIView.as_view(), name="retrieved-cards"),
    path("games/<str:game_id>/revealed_cards", CardRevealedSerializerAPIView.as_view(), name="revealed-cards"),
    path("games/<str:game_id>/unrevealed_cards", CardUnrevealedSerializerAPIView.as_view(), name="unrevealed-cards"),
    path("games/<str:game_id>/latest_chapter", LatestChapterAPIView.as_view(), name="latest-chapter"),
]
