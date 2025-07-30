from typing import Any, Dict

from django.contrib.auth import models as auth_models
from django.db import transaction
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .api_views_logic import prepare_new_game
from .models import CardPlayedInRound, Game, GameRound, Player, PlayerHand
from .serializers import (
    CardPlayedInRoundSerializerGet,
    CardPlayedInRoundSerializerPost,
    GameRoundSerializerGet,
    GameSerializerGet,
    GameSerializerPost,
    PlayerSerializerGet,
    PlayerSerializerPost,
)


class PlayerAPIView(APIView):  # type: ignore[misc]

    def get(self, request: Request) -> Response:
        assert isinstance(request.user, auth_models.User)
        nick = request.query_params.get("nick")
        if nick:
            try:
                player = Player.objects.get(user=request.user, nick=nick)
                serializer = PlayerSerializerGet(player)
            except Player.DoesNotExist:
                return Response(
                    {"error": f"player with nick {nick} does not exists"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        else:
            players = Player.objects.filter(user=request.user)
            serializer = PlayerSerializerGet(players, many=True)
        return Response(serializer.data)

    def post(self, request: Request) -> Response:
        assert isinstance(request.user, auth_models.User)
        serializer = PlayerSerializerPost(data=request.data)
        if serializer.is_valid():
            if Player.objects.filter(nick=serializer.validated_data["nick"], user=request.user).exists():
                return Response(
                    {"error": f"player with nick {serializer.validated_data['nick']} already exists"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GameAPIView(APIView):  # type: ignore[misc]

    def get(self, request: Request) -> Response:
        assert isinstance(request.user, auth_models.User)
        name = request.query_params.get("name")
        if name:
            try:
                game = Game.objects.get(user=request.user, name=name)
                serializer = GameSerializerGet(game)
            except Game.DoesNotExist:
                return Response(
                    {"error": f"game with name {name} does not exists"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        else:
            games = Game.objects.filter(user=request.user)
            serializer = GameSerializerGet(games, many=True)
        return Response(serializer.data)

    def post(self, request: Request) -> Response:
        assert isinstance(request.user, auth_models.User)
        serializer = GameSerializerPost(data=request.data)
        if serializer.is_valid():
            if Game.objects.filter(name=serializer.validated_data["name"], user=request.user).exists():
                return Response(
                    {"error": f"game with name {serializer.validated_data['name']} already exists"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if not 5 > len(serializer.validated_data["players"]) > 1:
                return Response(
                    {"error": "game has to have from 2 to 4 players"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            with transaction.atomic():
                game = serializer.save(user=request.user)
                prepare_new_game(game)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GameRoundAPIView(APIView):  # type: ignore[misc]
    def get(self, request: Request, game_id: str) -> Response:
        assert isinstance(request.user, auth_models.User)
        try:
            game = Game.objects.get(user=request.user, id=game_id)
        except Game.DoesNotExist:
            return Response(
                {"error": f"game with id {game_id} does not exists"},
                status=status.HTTP_404_NOT_FOUND,
            )
        round_games = GameRound.objects.filter(game=game)
        serializer = GameRoundSerializerGet(round_games, many=True)
        return Response(serializer.data)


class RoundCreateAPIView(APIView):  # type: ignore[misc]
    def post(self, request: Request, game_id: str) -> Response:
        assert isinstance(request.user, auth_models.User)
        try:
            game = Game.objects.get(user=request.user, id=game_id)
        except Game.DoesNotExist:
            return Response(
                {"error": f"game with id {game_id} does not exists"},
                status=status.HTTP_404_NOT_FOUND,
            )
        latest_round = GameRound.objects.filter(game=game).order_by("-chapter", "-round").first()
        assert latest_round is not None
        player_hands = PlayerHand.objects.filter(game=game).all()
        number_of_players = len(game.players.all())
        cards_played_in_latest_round = len(CardPlayedInRound.objects.filter(game_round=latest_round))
        for player_hand in player_hands:
            if player_hand.number_of_cards != 0 and cards_played_in_latest_round < number_of_players:
                return Response({"error": "not all players that have cards played in this round"})
        GameRound.objects.create(game=game, chapter=latest_round.chapter, round=latest_round.round + 1).save()
        return Response(status=status.HTTP_201_CREATED)


class ChapterCreateAPIView(APIView):  # type: ignore[misc]
    def post(self, request: Request, game_id: str) -> Response:
        assert isinstance(request.user, auth_models.User)
        try:
            game = Game.objects.get(user=request.user, id=game_id)
        except Game.DoesNotExist:
            return Response(
                {"error": f"game with id {game_id} does not exists"},
                status=status.HTTP_404_NOT_FOUND,
            )
        latest_round = GameRound.objects.filter(game=game).order_by("-chapter", "-round").first()
        assert latest_round is not None
        player_hands = PlayerHand.objects.filter(game=game).all()
        for player_hand in player_hands:
            if player_hand.number_of_cards != 0:
                return Response({"error": "not all players have 0 cards"})
        GameRound.objects.create(game=game, chapter=latest_round.chapter + 1, round=1).save()
        return Response(status=status.HTTP_201_CREATED)


class LatestChapterAPIView(APIView):  # type: ignore[misc]
    def get(self, request: Request, game_id: str) -> Response:
        assert isinstance(request.user, auth_models.User)
        try:
            game = Game.objects.get(user=request.user, id=game_id)
        except Game.DoesNotExist:
            return Response(
                {"error": f"game with id {game_id} does not exists"},
                status=status.HTTP_404_NOT_FOUND,
            )
        latest_round = GameRound.objects.filter(game=game).order_by("-chapter", "-round").first()
        assert latest_round is not None
        return Response({"chapter": latest_round.chapter})


class CardPlayedInRoundAPIView(APIView):  # type: ignore[misc]
    def get(self, request: Request, game_id: str) -> Response:
        assert isinstance(request.user, auth_models.User)
        try:
            game = Game.objects.get(user=request.user, id=game_id)
        except Game.DoesNotExist:
            return Response(
                {"error": f"game with id {game_id} does not exists"},
                status=status.HTTP_404_NOT_FOUND,
            )
        chapter_param = request.query_params.get("chapter")
        filters: Dict[str, Any] = {"game_round__game": game}
        if chapter_param:
            try:
                chapter = int(chapter_param)
                filters["game_round__chapter"] = chapter
            except ValueError:
                return Response(
                    {"error": "chapter must be an integer"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        cards_played_in_round = CardPlayedInRound.objects.filter(**filters)
        serializer = CardPlayedInRoundSerializerGet(cards_played_in_round, many=True)
        return Response(serializer.data)

    def post(self, request: Request, game_id: str) -> Response:
        assert isinstance(request.user, auth_models.User)
        try:
            game = Game.objects.get(user=request.user, id=game_id)
        except Game.DoesNotExist:
            return Response(
                {"error": f"game with id {game_id} does not exists"},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = CardPlayedInRoundSerializerPost(data=request.data)
        if serializer.is_valid():
            latest_round = GameRound.objects.filter(game=game).order_by("-chapter", "-round").first()
            assert latest_round is not None
            if CardPlayedInRound.objects.filter(
                game_round=latest_round, player=serializer.validated_data["player"]
            ).exists():
                return Response(
                    {"error": f"player with id {serializer.validated_data['player'].id} played card this round"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            with transaction.atomic():
                card_played = serializer.save(game_round=latest_round)
                assert isinstance(card_played, CardPlayedInRound)
                player_hand = PlayerHand.objects.get(player=card_played.player, game=game)
                if card_played.card_face_up:
                    if card_played.card_face_up not in game.cards_not_played.all():
                        return Response(
                            {"error": f"card face up {card_played.card_face_up.id} was already played"},
                            status=status.HTTP_400_BAD_REQUEST,
                        )
                    player_hand.number_of_cards -= 1
                    game.cards_not_played.remove(card_played.card_face_up)
                    game.save()
                player_hand.number_of_cards -= card_played.number_of_cards_face_down
                player_hand.save()

                return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
