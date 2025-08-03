import uuid

from django.contrib.auth import get_user_model
from django.db import transaction
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from ..api_views_logic import prepare_new_game
from ..models import CardPlayedInRound, Game, GameRound, Player, PlayerHand

User = get_user_model()


class RoundCreateAPITests(APITestCase):  # type: ignore[misc]

    fixtures = ["app/initial_data/initial_data.json"]

    def get_create_round_url(self, game_id: uuid.UUID) -> str:
        return reverse("create-round", kwargs={"game_id": str(game_id)})

    def setUp(self) -> None:
        self.client = APIClient()
        self.user = User.objects.create_user(username="testuser", password="12345")
        self.user_two = User.objects.create_user(username="testuser_two", password="12345")
        self.client.login(username="testuser", password="12345")
        for nick in ["a", "b"]:
            Player.objects.create(nick=nick, user=self.user)

    def test_create_round_post(self) -> None:
        with transaction.atomic():
            game = Game.objects.create(name="a", user=self.user)
            game.players.set(Player.objects.all())
            prepare_new_game(game)
            game_round = GameRound.objects.first()
            assert game_round is not None
            players = game.players.all()
            CardPlayedInRound.objects.create(player=players[0], game_round=game_round, number_of_cards_face_down=1)
            PlayerHand.objects.filter(player=players[1], game=game).update(number_of_cards=0)
        response = self.client.post(self.get_create_round_url(game.id))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        game_round = GameRound.objects.filter(game=game).order_by("-chapter", "-round").first()
        assert game_round is not None
        self.assertEqual(game_round.round, 2)
        self.assertEqual(game_round.chapter, 1)

    def test_create_round_post_not_all_players_played_in_current_round(self) -> None:
        with transaction.atomic():
            game = Game.objects.create(name="a", user=self.user)
            game.players.set(Player.objects.all())
            prepare_new_game(game)
            game_round = GameRound.objects.first()
            assert game_round is not None
            player = game.players.first()
            assert player is not None
            CardPlayedInRound.objects.create(player=player, game_round=game_round, number_of_cards_face_down=1)
        response = self.client.post(self.get_create_round_url(game.id))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["detail"], "not all players that have cards played in this round")

    def test_create_round_post_game_not_exists(self) -> None:
        game = Game.objects.create(name="a", user=self.user_two)
        response = self.client.post(self.get_create_round_url(game.id))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["detail"], f"game {game.id} does not exist")
