import uuid

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from ..models import Game, GameRound, Player

User = get_user_model()


class GameRoundAPITests(APITestCase):  # type: ignore[misc]

    fixtures = ["app/initial_data/initial_data.json"]

    def get_game_url(self, game_id: uuid.UUID) -> str:
        return reverse("game-rounds", kwargs={"game_id": str(game_id)})

    def setUp(self) -> None:
        self.client = APIClient()
        self.user = User.objects.create_user(username="testuser", password="12345")
        self.user_two = User.objects.create_user(username="testuser_two", password="12345")
        self.client.login(username="testuser", password="12345")
        for nick in ["a", "b", "c", "d", "e"]:
            Player.objects.create(nick=nick, user=self.user)

    def test_game_round_get(self) -> None:
        game = Game.objects.create(name="a", user=self.user)
        GameRound.objects.create(game=game, chapter=1, round=1)
        response = self.client.get(self.get_game_url(game.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_game_round_get_game_not_exists(self) -> None:
        game = Game.objects.create(name="a", user=self.user_two)
        GameRound.objects.create(game=game, chapter=1, round=1)
        response = self.client.get(self.get_game_url(game.id))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["detail"], f"game {game.id} does not exist")
