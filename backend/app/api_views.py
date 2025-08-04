import uuid
from typing import Any, Dict

from django.contrib.auth import models as auth_models
from django.db import transaction
from rest_framework import status
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .api_views_logic import prepare_new_game
from .models import Card, CardPlayedInRound, Game, GameRound, Player, PlayerHand
from .serializers import (
    CardPlayedInRoundSerializerGet,
    CardPlayedInRoundSerializerPost,
    CardSerializerGet,
    CardSerializerPost,
    GameRoundSerializerGet,
    GameSerializerGet,
    GameSerializerPost,
    NumberOfCardsAddedSerializerPost,
    PlayerSerializerGet,
    PlayerSerializerPost,
    RegisterSerializer,
)
from .views_logic import get_cards_to_play, get_cards_to_retrieve, get_cards_to_reveal


class BaseAPIView(APIView):  # type: ignore[misc]

    def get_game(self, user: Any, game_id: uuid.UUID) -> Game:
        try:
            return Game.objects.get(user=user, id=game_id)
        except Game.DoesNotExist as exc:
            raise NotFound(detail=f"game {game_id} does not exist") from exc

    def get_game_by_name(self, user: Any, game_name: str) -> Game:
        try:
            return Game.objects.get(user=user, name=game_name)
        except Game.DoesNotExist as exc:
            raise NotFound(detail=f"game {game_name} does not exist") from exc

    def get_player(self, user: Any, player_id: uuid.UUID) -> Player:
        try:
            return Player.objects.get(user=user, id=player_id)
        except Player.DoesNotExist as exc:
            raise NotFound(detail=f"player {player_id} does not exist") from exc

    def get_player_by_nick(self, user: Any, player_nick: str) -> Player:
        try:
            return Player.objects.get(user=user, nick=player_nick)
        except Player.DoesNotExist as exc:
            raise NotFound(detail=f"player {player_nick} does not exist") from exc

    def get_player_hand(self, player_id: uuid.UUID, game: Game) -> PlayerHand:
        try:
            return PlayerHand.objects.get(player__id=player_id, game=game)
        except PlayerHand.DoesNotExist as exc:
            raise ValidationError(detail=f"player {player_id} does not play in this game") from exc

    def get_card(self, card_id: uuid.UUID) -> Card:
        try:
            return Card.objects.get(id=card_id)
        except Card.DoesNotExist as exc:
            raise ValidationError(detail=f"card {card_id} does not exist") from exc


class RegisterAPIView(APIView):  # type: ignore[misc]
    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({"message": "User created successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PlayerAPIView(BaseAPIView):

    def get(self, request: Request) -> Response:
        assert isinstance(request.user, auth_models.User)
        nick = request.query_params.get("nick")
        if nick:
            player = self.get_player_by_nick(request.user, nick)
            serializer = PlayerSerializerGet(player)
        else:
            players = Player.objects.filter(user=request.user)
            serializer = PlayerSerializerGet(players, many=True)
        return Response(serializer.data)

    def post(self, request: Request) -> Response:
        assert isinstance(request.user, auth_models.User)
        serializer = PlayerSerializerPost(data=request.data)
        if serializer.is_valid(raise_exception=True):
            if Player.objects.filter(nick=serializer.validated_data["nick"], user=request.user).exists():
                return Response(
                    {"detail": f"player {serializer.validated_data['nick']} already exist"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GameAPIView(BaseAPIView):

    def get(self, request: Request) -> Response:
        assert isinstance(request.user, auth_models.User)
        name = request.query_params.get("name")
        if name:
            game = self.get_game_by_name(request.user, name)
            serializer = GameSerializerGet(game)
        else:
            games = Game.objects.filter(user=request.user)
            serializer = GameSerializerGet(games, many=True)
        return Response(serializer.data)

    def post(self, request: Request) -> Response:
        assert isinstance(request.user, auth_models.User)
        serializer = GameSerializerPost(data=request.data)
        if serializer.is_valid(raise_exception=True):
            if Game.objects.filter(name=serializer.validated_data["name"], user=request.user).exists():
                return Response(
                    {"detail": f"game {serializer.validated_data['name']} already exist"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if not 5 > len(serializer.validated_data["players"]) > 1:
                return Response(
                    {"detail": "game has to have from 2 to 4 players"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            with transaction.atomic():
                game = serializer.save(user=request.user)
                prepare_new_game(game)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GameRoundAPIView(BaseAPIView):
    def get(self, request: Request, game_id: uuid.UUID) -> Response:
        assert isinstance(request.user, auth_models.User)
        game = self.get_game(request.user, game_id)
        game_rounds = GameRound.objects.filter(game=game)
        serializer = GameRoundSerializerGet(game_rounds, many=True)
        return Response(serializer.data)


class RoundCreateAPIView(BaseAPIView):
    def post(self, request: Request, game_id: uuid.UUID) -> Response:
        assert isinstance(request.user, auth_models.User)
        game = self.get_game(request.user, game_id)
        latest_round = GameRound.objects.filter(game=game).order_by("-chapter", "-round").first()
        assert latest_round is not None
        player_hands = PlayerHand.objects.filter(game=game).all()
        for player_hand in player_hands:
            if (
                player_hand.number_of_cards != 0
                and not CardPlayedInRound.objects.filter(player=player_hand.player, game_round=latest_round).exists()
            ):
                return Response(
                    {"detail": "not all players that have cards played in this round"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        game_round = GameRound.objects.create(game=game, chapter=latest_round.chapter, round=latest_round.round + 1)
        game_round.save()
        serializer = GameRoundSerializerGet(game_round)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ChapterCreateAPIView(BaseAPIView):
    def post(self, request: Request, game_id: uuid.UUID) -> Response:
        assert isinstance(request.user, auth_models.User)
        game = self.get_game(request.user, game_id)
        latest_round = GameRound.objects.filter(game=game).order_by("-chapter", "-round").first()
        assert latest_round is not None
        player_hands = PlayerHand.objects.filter(game=game).all()
        for player_hand in player_hands:
            if player_hand.number_of_cards != 0:
                return Response({"detail": "not all players have 0 cards"}, status=status.HTTP_400_BAD_REQUEST)
        game_round = GameRound.objects.create(game=game, chapter=latest_round.chapter + 1, round=1)
        game_round.save()
        serializer = GameRoundSerializerGet(game_round)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class LatestChapterAPIView(BaseAPIView):
    def get(self, request: Request, game_id: uuid.UUID) -> Response:
        assert isinstance(request.user, auth_models.User)
        game = self.get_game(request.user, game_id)
        latest_round = GameRound.objects.filter(game=game).order_by("-chapter", "-round").first()
        assert latest_round is not None
        return Response({"chapter": latest_round.chapter, "round": latest_round.round})


class CardPlayedInRoundAPIView(BaseAPIView):
    def get(self, request: Request, game_id: uuid.UUID, player_id: uuid.UUID) -> Response:
        assert isinstance(request.user, auth_models.User)
        game = self.get_game(request.user, game_id)
        player = self.get_player(request.user, player_id)
        self.get_player_hand(player_id, game)
        chapter_param = request.query_params.get("chapter")
        round_param = request.query_params.get("round")
        filters: Dict[str, Any] = {"game_round__game": game, "player": player}
        if chapter_param:
            try:
                chapter = int(chapter_param)
                filters["game_round__chapter"] = chapter
            except ValueError:
                return Response(
                    {"detail": "chapter must be an integer"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        if round_param:
            try:
                _round = int(round_param)
                filters["game_round__round"] = _round
            except ValueError:
                return Response(
                    {"detail": "round must be an integer"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        cards_played_in_round = CardPlayedInRound.objects.filter(**filters)
        serializer = CardPlayedInRoundSerializerGet(cards_played_in_round, many=True)
        return Response(serializer.data)

    def post(self, request: Request, game_id: uuid.UUID, player_id: uuid.UUID) -> Response:
        assert isinstance(request.user, auth_models.User)
        game = self.get_game(request.user, game_id)
        player = self.get_player(request.user, player_id)
        player_hand = self.get_player_hand(player_id, game)
        serializer = CardPlayedInRoundSerializerPost(data=request.data)
        if serializer.is_valid(raise_exception=True):
            latest_round = GameRound.objects.filter(game=game).order_by("-chapter", "-round").first()
            assert latest_round is not None
            if CardPlayedInRound.objects.filter(game_round=latest_round, player=player).exists():
                return Response(
                    {"detail": f"player {player.id} played card this round"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            with transaction.atomic():
                card_played = serializer.save(player=player, game_round=latest_round)
                assert isinstance(card_played, CardPlayedInRound)
                if card_played.card_face_up:
                    if card_played.card_face_up not in get_cards_to_play(game, player):
                        return Response(
                            {"detail": f"card {card_played.card_face_up.id} was already played face up"},
                            status=status.HTTP_400_BAD_REQUEST,
                        )
                    player_hand.number_of_cards -= 1
                    game.cards_not_played.remove(card_played.card_face_up)
                    game.save()
                player_hand.number_of_cards -= card_played.number_of_cards_face_down
                player_hand.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CardAPIView(APIView):  # type: ignore[misc]
    def get(self, request: Request) -> Response:
        assert isinstance(request.user, auth_models.User)
        filters: Dict[str, Any] = {}
        suit = request.query_params.get("suit")
        number = request.query_params.get("number")
        if suit:
            filters["suit"] = suit
        if number:
            filters["number"] = number
        cards = Card.objects.filter(**filters)
        if len(cards) == 0:
            return Response({"detail": "no card found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = CardSerializerGet(cards, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CardRetrievedSerializerAPIView(BaseAPIView):
    def post(self, request: Request, game_id: uuid.UUID, player_id: uuid.UUID) -> Response:
        assert isinstance(request.user, auth_models.User)
        game = self.get_game(request.user, game_id)
        player_hand = self.get_player_hand(player_id, game)
        serializer = CardSerializerPost(data=request.data)
        if serializer.is_valid(raise_exception=True):
            card: Card = serializer.validated_data["id"]
            latest_round = GameRound.objects.filter(game=game).order_by("-chapter", "-round").first()
            assert latest_round is not None
            if card not in get_cards_to_retrieve(game, latest_round.chapter, latest_round.round):
                return Response(
                    {"detail": f"card {card.id} can not be retrieved"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            player_hand.number_of_cards += 1
            player_hand.cards.add(card)
            player_hand.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class NumberOfCardsAddedSerializerAPIView(BaseAPIView):
    def post(self, request: Request, game_id: uuid.UUID, player_id: uuid.UUID) -> Response:
        assert isinstance(request.user, auth_models.User)
        game = self.get_game(request.user, game_id)
        player_hand = self.get_player_hand(player_id, game)
        serializer = NumberOfCardsAddedSerializerPost(data=request.data)
        if serializer.is_valid(raise_exception=True):
            player_hand.number_of_cards += serializer.validated_data["number_of_cards"]
            player_hand.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CardRevealedSerializerAPIView(BaseAPIView):
    def post(self, request: Request, game_id: uuid.UUID, player_id: uuid.UUID) -> Response:
        assert isinstance(request.user, auth_models.User)
        game = self.get_game(request.user, game_id)
        player_hand = self.get_player_hand(player_id, game)
        serializer = CardSerializerPost(data=request.data)
        if serializer.is_valid(raise_exception=True):
            card: Card = serializer.validated_data["id"]
            if card not in get_cards_to_reveal(game):
                return Response(
                    {"detail": f"card {card.id} can not be revealed"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            with transaction.atomic():
                player_hand.cards.add(card)
                game.cards_not_played.remove(card)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CardUnrevealedSerializerAPIView(BaseAPIView):
    def post(self, request: Request, game_id: uuid.UUID, player_id: uuid.UUID) -> Response:
        assert isinstance(request.user, auth_models.User)
        game = self.get_game(request.user, game_id)
        player_hand = self.get_player_hand(player_id, game)
        serializer = CardSerializerPost(data=request.data)
        if serializer.is_valid(raise_exception=True):
            card: Card = serializer.validated_data["id"]
            if card not in player_hand.cards.all():
                return Response(
                    {"detail": f"card {card.id} can not be unrevealed"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            with transaction.atomic():
                player_hand.cards.remove(card)
                game.cards_not_played.add(card)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
