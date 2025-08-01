import uuid
from typing import Any

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from ..models import Game, GameRound, Player, PlayerHand

User = get_user_model()


class GameAPITests(APITestCase):  # type: ignore[misc]

    fixtures = ["app/initial_data/initial_data.json"]

    def get_player_id(self, nick: str, user: Any) -> uuid.UUID:
        return Player.objects.get(nick=nick, user=user).id

    def setUp(self) -> None:
        self.client = APIClient()
        self.url = reverse("games")
        self.user = User.objects.create_user(username="testuser", password="12345")
        self.user_two = User.objects.create_user(username="testuser_two", password="12345")
        self.client.login(username="testuser", password="12345")
        for nick in ["a", "b", "c", "d", "e"]:
            Player.objects.create(nick=nick, user=self.user)

    def test_game_post(self) -> None:
        test_cases = [("a", ["a", "b"], 20), ("b", ["a", "b", "c"], 20), ("c", ["a", "b", "c", "d"], 28)]
        for game_name, player_nicks, number_of_cards in test_cases:
            with self.subTest():
                new_data = {"name": game_name, "players": []}
                for player_nick in player_nicks:
                    new_data["players"].append(self.get_player_id(player_nick, self.user))  # type: ignore[attr-defined]
                response = self.client.post(self.url, new_data)
                self.assertEqual(response.status_code, status.HTTP_201_CREATED)
                game_object = Game.objects.filter(name=game_name, user=self.user).get()
                self.assertEqual(game_object.cards_not_played.count(), number_of_cards)
                self.assertEqual(GameRound.objects.filter(game=game_object).count(), 1)
                self.assertEqual(PlayerHand.objects.filter(game=game_object).count(), len(player_nicks))

    def test_game_post_wrong_number_of_players(self) -> None:
        test_cases = [("a", ["a"]), ("b", ["a", "b", "c", "d", "e"])]
        for game_name, player_nicks in test_cases:
            with self.subTest():
                new_data = {"name": game_name, "players": []}
                for player_nick in player_nicks:
                    new_data["players"].append(self.get_player_id(player_nick, self.user))  # type: ignore[attr-defined]
                response = self.client.post(self.url, new_data)
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertEqual(response.data["error"], "game has to have from 2 to 4 players")

    def test_game_post_already_created(self) -> None:
        Game.objects.create(name="a", user=self.user)
        new_data = {"name": "a", "players": []}
        for player_nick in ["a", "b"]:
            new_data["players"].append(self.get_player_id(player_nick, self.user))  # type: ignore[attr-defined]
        response = self.client.post(self.url, new_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "game a already exist")

    def test_game_post_duplcated_name_in_database(self) -> None:
        Game.objects.create(name="a", user=self.user_two)
        new_data = {"name": "a", "players": []}
        for player_nick in ["a", "b"]:
            new_data["players"].append(self.get_player_id(player_nick, self.user))  # type: ignore[attr-defined]
        response = self.client.post(self.url, new_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Game.objects.filter(user=self.user).count(), 1)

    def test_game_get(self) -> None:
        Game.objects.create(name="a", user=self.user)
        Game.objects.create(name="b", user=self.user_two)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "a")

    def test_game_get_one(self) -> None:
        Game.objects.create(name="a", user=self.user)
        Game.objects.create(name="b", user=self.user_two)
        response = self.client.get(self.url, {"name": "a"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "a")

    def test_game_get_no_player(self) -> None:
        response = self.client.get(self.url, {"name": "a"})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["error"], "game a does not exist")
