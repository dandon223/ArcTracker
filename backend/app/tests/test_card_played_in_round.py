import uuid
from typing import Any

from django.contrib.auth import get_user_model
from django.db import transaction
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from ..api_views_logic import prepare_new_game
from ..models import Card, CardPlayedInRound, Game, GameRound, Player

User = get_user_model()


class CardPlayedInRoundAPITests(APITestCase):  # type: ignore[misc]

    fixtures = ["app/initial_data/initial_data.json"]

    def get_player_id(self, nick: str, user: Any) -> uuid.UUID:
        return Player.objects.get(nick=nick, user=user).id

    def get_card_played_in_round_url(self, game_id: uuid.UUID) -> str:
        return reverse("played-cards", kwargs={"game_id": str(game_id)})

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

    def test_card_played_in_round_get(self) -> None:
        game = Game.objects.first()
        assert game is not None
        game_round = GameRound.objects.first()
        assert game_round is not None
        player = game.players.first()
        assert player is not None
        CardPlayedInRound.objects.create(player=player, game_round=game_round)
        response = self.client.get(self.get_card_played_in_round_url(game.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_card_played_in_round_get_chapter(self) -> None:
        game = Game.objects.first()
        assert game is not None
        game_round = GameRound.objects.first()
        assert game_round is not None
        player = game.players.first()
        assert player is not None
        CardPlayedInRound.objects.create(player=player, game_round=game_round)
        response = self.client.get(self.get_card_played_in_round_url(game.id), {"chapter": 2})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_card_played_in_round_get_chapter_not_number(self) -> None:
        game = Game.objects.first()
        assert game is not None
        response = self.client.get(self.get_card_played_in_round_url(game.id), {"chapter": "a"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "chapter must be an integer")

    def test_card_played_in_round_get_game_not_exists(self) -> None:
        game = Game.objects.create(name="b", user=self.user_two)
        response = self.client.get(self.get_card_played_in_round_url(game.id))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["error"], f"game {game.id} does not exist")

    def test_card_played_in_round_post(self) -> None:
        game = Game.objects.first()
        assert game is not None
        card = Card.objects.first()
        assert card is not None
        player_id = self.get_player_id("a", self.user)
        data = {"player": player_id, "card_face_up": card.id}
        response = self.client.post(self.get_card_played_in_round_url(game.id), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_card_played_in_round_post_game_not_exists(self) -> None:
        game = Game.objects.create(name="b", user=self.user_two)
        player_id = self.get_player_id("a", self.user)
        data = {"player": player_id, "number_of_cards_face_down": 2}
        response = self.client.post(self.get_card_played_in_round_url(game.id), data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["error"], f"game {game.id} does not exist")

    def test_card_played_in_round_post_already_played(self) -> None:
        game = Game.objects.first()
        assert game is not None
        card = Card.objects.first()
        assert card is not None
        player_id = self.get_player_id("a", self.user)
        data = {"player": player_id, "card_face_up": card.id}
        response = self.client.post(self.get_card_played_in_round_url(game.id), data)
        data_two = {"player": player_id, "number_of_cards_face_down": 2}
        response = self.client.post(self.get_card_played_in_round_url(game.id), data_two)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], f"player {player_id} played card this round")

    def test_card_played_in_round_post_card_was_already_played(self) -> None:
        game = Game.objects.first()
        assert game is not None
        card = Card.objects.first()
        assert card is not None
        player_id = self.get_player_id("a", self.user)
        data = {"player": player_id, "card_face_up": card.id}
        self.client.post(self.get_card_played_in_round_url(game.id), data)
        player_id = self.get_player_id("b", self.user)
        data = {"player": player_id, "card_face_up": card.id}
        response = self.client.post(self.get_card_played_in_round_url(game.id), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], f"card {card.id} was already played face up")

    def test_card_played_in_round_post_wrong_number_of_cards_one(self) -> None:
        game = Game.objects.first()
        assert game is not None
        card = Card.objects.first()
        assert card is not None
        player_id = self.get_player_id("a", self.user)
        data = {"player": player_id, "card_face_up": card.id, "number_of_cards_face_down": 2}
        response = self.client.post(self.get_card_played_in_round_url(game.id), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["non_field_errors"][0], "With played card face up you can only play up to one card face down."
        )

    def test_card_played_in_round_post_wrong_number_of_cards_two(self) -> None:
        game = Game.objects.first()
        assert game is not None
        card = Card.objects.first()
        assert card is not None
        player_id = self.get_player_id("a", self.user)
        data = {"player": player_id, "number_of_cards_face_down": 3}
        response = self.client.post(self.get_card_played_in_round_url(game.id), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["number_of_cards_face_down"][0], '"3" is not a valid choice.')

    def test_card_played_in_round_post_wrong_number_of_cards_three(self) -> None:
        game = Game.objects.first()
        assert game is not None
        card = Card.objects.first()
        assert card is not None
        player_id = self.get_player_id("a", self.user)
        data = {"player": player_id}
        response = self.client.post(self.get_card_played_in_round_url(game.id), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["non_field_errors"][0], "You have to play atleast one card.")

    def test_card_played_in_round_post_wrong_player(self) -> None:
        game = Game.objects.first()
        assert game is not None
        card = Card.objects.first()
        assert card is not None
        player_id = self.get_player_id("e", self.user)
        data = {"player": player_id, "card_face_up": card.id}
        response = self.client.post(self.get_card_played_in_round_url(game.id), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], f"player {player_id} does not play in this game")
