import uuid
from typing import Any

from django.contrib.auth import get_user_model
from django.db import transaction
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from ..api_views_logic import prepare_new_game
from ..models import Game, Player, PlayerHand

User = get_user_model()


class AddCardAPITests(APITestCase):  # type: ignore[misc]

    fixtures = ["app/initial_data/initial_data.json"]

    def get_player_id(self, nick: str, user: Any) -> uuid.UUID:
        return Player.objects.get(nick=nick, user=user).id

    def get_add_card_url(self, game_id: uuid.UUID, player_id: uuid.UUID) -> str:
        return reverse("add-card", kwargs={"game_id": str(game_id), "player_id": str(player_id)})

    def setUp(self) -> None:
        self.client = APIClient()
        self.user = User.objects.create_user(username="testuser", password="12345")
        self.user_two = User.objects.create_user(username="testuser_two", password="12345")
        self.client.login(username="testuser", password="12345")
        players = []
        for nick in ["a", "b", "c", "d", "e"]:
            players.append(Player.objects.create(nick=nick, user=self.user))
        with transaction.atomic():
            game = Game.objects.create(name="a", user=self.user)
            game.players.set(players[:3])
            prepare_new_game(game)

    def test_add_card_post(self) -> None:
        game = Game.objects.first()
        assert game is not None
        player_id = self.get_player_id("a", self.user)
        data = {"number_of_cards": 4}
        self.client.post(self.get_add_card_url(game.id, player_id), data)
        player_hand = PlayerHand.objects.get(game=game, player_id=player_id)
        self.assertEqual(player_hand.number_of_cards, 10)

    def test_add_card_post_player_not_in_game(self) -> None:
        game = Game.objects.first()
        assert game is not None
        player_id = self.get_player_id("e", self.user)
        data = {"number_of_cards": 4}
        response = self.client.post(self.get_add_card_url(game.id, player_id), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["detail"], f"player {player_id} does not play in this game")

    def test_add_card_post_negative(self) -> None:
        game = Game.objects.first()
        assert game is not None
        player_id = self.get_player_id("a", self.user)
        data = {"number_of_cards": -1}
        response = self.client.post(self.get_add_card_url(game.id, player_id), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["detail"], "error: number_of_cards must be greater than zero")

    def test_add_card_post_game_not_exists(self) -> None:
        game = Game.objects.create(name="b", user=self.user_two)
        player_id = self.get_player_id("a", self.user)
        data = {"number_of_cards_face_down": 2}
        response = self.client.post(self.get_add_card_url(game.id, player_id), data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["detail"], f"game {game.id} does not exist")
