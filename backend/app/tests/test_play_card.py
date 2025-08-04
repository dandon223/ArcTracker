import uuid
from typing import Any

from django.contrib.auth import get_user_model
from django.db import transaction
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from ..api_views_logic import prepare_new_game
from ..models import CardPlayedInRound, Game, GameRound, Player

User = get_user_model()


class CardPlayedInRoundAPITests(APITestCase):  # type: ignore[misc]

    fixtures = ["app/initial_data/initial_data.json"]

    def get_player_id(self, nick: str, user: Any) -> uuid.UUID:
        return Player.objects.get(nick=nick, user=user).id

    def get_card_played_in_round_url(self, game_id: uuid.UUID, player_id: uuid.UUID) -> str:
        return reverse("play-card", kwargs={"game_id": str(game_id), "player_id": str(player_id)})

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

    def test_play_card_get(self) -> None:
        game = Game.objects.first()
        assert game is not None
        game_round = GameRound.objects.first()
        assert game_round is not None
        player = game.players.first()
        assert player is not None
        CardPlayedInRound.objects.create(player=player, game_round=game_round)
        response = self.client.get(self.get_card_played_in_round_url(game.id, player.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_play_card_get_chapter(self) -> None:
        game = Game.objects.first()
        assert game is not None
        game_round = GameRound.objects.first()
        assert game_round is not None
        player = game.players.first()
        assert player is not None
        CardPlayedInRound.objects.create(player=player, game_round=game_round)
        response = self.client.get(self.get_card_played_in_round_url(game.id, player.id), {"chapter": 2})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_play_card_get_chapter_not_number(self) -> None:
        game = Game.objects.first()
        assert game is not None
        player = game.players.first()
        assert player is not None
        response = self.client.get(self.get_card_played_in_round_url(game.id, player.id), {"chapter": "a"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["detail"], "chapter must be an integer")

    def test_play_card_get_game_not_exists(self) -> None:
        game = Game.objects.create(name="b", user=self.user_two)
        player_id = self.get_player_id("a", self.user)
        response = self.client.get(self.get_card_played_in_round_url(game.id, player_id))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["detail"], f"game {game.id} does not exist")

    def test_play_card_get_player_not_in_game(self) -> None:
        game = Game.objects.first()
        assert game is not None
        player_id = self.get_player_id("e", self.user)
        response = self.client.get(self.get_card_played_in_round_url(game.id, player_id))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["detail"], f"player {player_id} does not play in this game")

    def test_play_card_post(self) -> None:
        game = Game.objects.first()
        assert game is not None
        card = game.cards_not_played.first()
        assert card is not None
        player_id = self.get_player_id("a", self.user)
        data = {"card_face_up": card.id}
        response = self.client.post(self.get_card_played_in_round_url(game.id, player_id), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_play_card_post_game_not_exists(self) -> None:
        game = Game.objects.create(name="b", user=self.user_two)
        player_id = self.get_player_id("a", self.user)
        data = {"number_of_cards_face_down": 2}
        response = self.client.post(self.get_card_played_in_round_url(game.id, player_id), data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["detail"], f"game {game.id} does not exist")

    def test_play_card_post_already_played(self) -> None:
        game = Game.objects.first()
        assert game is not None
        card = game.cards_not_played.first()
        assert card is not None
        player_id = self.get_player_id("a", self.user)
        data = {"card_face_up": card.id}
        response = self.client.post(self.get_card_played_in_round_url(game.id, player_id), data)
        data_two = {"number_of_cards_face_down": 2}
        response = self.client.post(self.get_card_played_in_round_url(game.id, player_id), data_two)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["detail"], f"player {player_id} played card this round")

    def test_play_card_post_card_was_already_played(self) -> None:
        game = Game.objects.first()
        assert game is not None
        card = game.cards_not_played.first()
        assert card is not None
        player_id = self.get_player_id("a", self.user)
        data = {"card_face_up": card.id}
        self.client.post(self.get_card_played_in_round_url(game.id, player_id), data)
        player_id = self.get_player_id("b", self.user)
        data = {"card_face_up": card.id}
        response = self.client.post(self.get_card_played_in_round_url(game.id, player_id), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["detail"], f"card {card.id} was already played face up")

    def test_play_card_post_wrong_number_of_cards_one(self) -> None:
        game = Game.objects.first()
        assert game is not None
        card = game.cards_not_played.first()
        assert card is not None
        player_id = self.get_player_id("a", self.user)
        data = {"card_face_up": card.id, "number_of_cards_face_down": 2}
        response = self.client.post(self.get_card_played_in_round_url(game.id, player_id), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["detail"],
            "non_field_errors: with played card face up you can only play up to one card face down",
        )

    def test_play_card_post_wrong_number_of_cards_two(self) -> None:
        game = Game.objects.first()
        assert game is not None
        card = game.cards_not_played.first()
        assert card is not None
        player_id = self.get_player_id("a", self.user)
        data = {"number_of_cards_face_down": 3}
        response = self.client.post(self.get_card_played_in_round_url(game.id, player_id), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["detail"], 'number_of_cards_face_down: "3" is not a valid choice.')

    def test_play_card_post_wrong_number_of_cards_three(self) -> None:
        game = Game.objects.first()
        assert game is not None
        card = game.cards_not_played.first()
        assert card is not None
        player_id = self.get_player_id("a", self.user)
        response = self.client.post(self.get_card_played_in_round_url(game.id, player_id), {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["detail"], "non_field_errors: you have to play atleast one card")

    def test_play_card_post_wrong_player(self) -> None:
        game = Game.objects.first()
        assert game is not None
        card = game.cards_not_played.first()
        assert card is not None
        player_id = self.get_player_id("e", self.user)
        data = {"card_face_up": card.id}
        response = self.client.post(self.get_card_played_in_round_url(game.id, player_id), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["detail"], f"player {player_id} does not play in this game")
