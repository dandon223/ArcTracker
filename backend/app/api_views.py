from django.contrib.auth import models as auth_models
from django.db import transaction
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Game, Player
from .serializers import GameSerializerGet, GameSerializerPost, PlayerSerializerGet, PlayerSerializerPost
from .views_logic import assign_cards, create_initial_round, deal_initial_hands


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
                    {"nick": f"player with nick {nick} does not exists"},
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
                    {"nick": f"player with nick {serializer.validated_data['nick']} already exists"},
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
                    {"name": f"game with name {name} does not exists"},
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
                    {"name": f"game with name {serializer.validated_data['name']} already exists"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if not 5 > len(serializer.validated_data["players"]) > 1:
                return Response(
                    {"players": "game has to have from 2 to 4 players"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            with transaction.atomic():
                game = serializer.save(user=request.user)
                assign_cards(game)
                create_initial_round(game)
                deal_initial_hands(game)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
