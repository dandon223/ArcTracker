import uuid
from typing import Any

from django.contrib.auth import get_user_model
from django.db import transaction
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from ..api_views_logic import prepare_new_game
from ..models import Game, GameRound, Player, PlayerHand

User = get_user_model()


class RevealCardAPITests(APITestCase):  # type: ignore[misc]

    fixtures = ["app/initial_data/initial_data.json"]

    def get_player_id(self, nick: str, user: Any) -> uuid.UUID:
        return Player.objects.get(nick=nick, user=user).id

    def get_reveal_card_url(self, game_id: uuid.UUID, player_id: uuid.UUID) -> str:
        return reverse("reveal-card", kwargs={"game_id": str(game_id), "player_id": str(player_id)})

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

    def test_reveal_card_post(self) -> None:
        game = Game.objects.first()
        assert game is not None
        game_round = GameRound.objects.first()
        assert game_round is not None
        players = game.players.all()
        player = players[0]
        card = game.cards_not_played.first()
        assert card is not None
        response = self.client.post(self.get_reveal_card_url(game.id, player.id), {"id": card.id})
        player_hand = PlayerHand.objects.get(game=game, player_id=player.id)
        player_cards = player_hand.cards.all()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(player_hand.number_of_cards, 6)
        self.assertEqual(len(player_cards), 1)
        self.assertEqual(player_cards[0].id, card.id)
        self.assertEqual(len(game.cards_not_played.all()), 19)

    def test_reveal_card_post_already_played(self) -> None:
        game = Game.objects.first()
        assert game is not None
        game_round = GameRound.objects.first()
        assert game_round is not None
        players = game.players.all()
        player = players[0]
        player_two = players[1]
        card = game.cards_not_played.first()
        assert card is not None
        self.client.post(self.get_reveal_card_url(game.id, player.id), {"id": card.id})
        response = self.client.post(self.get_reveal_card_url(game.id, player_two.id), {"id": card.id})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["detail"], f"card {card.id} can not be revealed")
