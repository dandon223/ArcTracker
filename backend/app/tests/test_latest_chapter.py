import uuid

from django.contrib.auth import get_user_model
from django.db import transaction
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from ..api_views_logic import prepare_new_game
from ..models import Game, Player

User = get_user_model()


class LatestChapterAPITests(APITestCase):  # type: ignore[misc]

    fixtures = ["app/initial_data/initial_data.json"]

    def get_latest_chapter_url(self, game_id: uuid.UUID) -> str:
        return reverse("latest-chapter", kwargs={"game_id": str(game_id)})

    def setUp(self) -> None:
        self.client = APIClient()
        self.user = User.objects.create_user(username="testuser", password="12345")
        self.user_two = User.objects.create_user(username="testuser_two", password="12345")
        self.client.login(username="testuser", password="12345")
        for nick in ["a", "b"]:
            Player.objects.create(nick=nick, user=self.user)

    def test_latest_chapter_get(self) -> None:
        with transaction.atomic():
            game = Game.objects.create(name="a", user=self.user)
            game.players.set(Player.objects.all())
            prepare_new_game(game)
        response = self.client.get(self.get_latest_chapter_url(game.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["chapter"], 1)
        self.assertEqual(response.data["round"], 1)

    def test_latest_chapter_game_not_exists(self) -> None:
        game = Game.objects.create(name="a", user=self.user_two)
        response = self.client.get(self.get_latest_chapter_url(game.id))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["detail"], f"game {game.id} does not exist")
