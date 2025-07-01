from django.contrib.auth import models as auth_models
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Player
from .serializers import PlayerSerializer


class PlayerAPIView(APIView):  # type: ignore[misc]

    def get(self, request: Request) -> Response:
        assert isinstance(request.user, auth_models.User)
        players = Player.objects.filter(user=request.user)
        serializer = PlayerSerializer(players, many=True)
        return Response(serializer.data)

    def post(self, request: Request) -> Response:
        assert isinstance(request.user, auth_models.User)
        serializer = PlayerSerializer(data=request.data)
        if serializer.is_valid():
            if Player.objects.filter(nick=serializer.validated_data["nick"], user=request.user).exists():
                return Response(
                    {"nick": f"player with nick {serializer.validated_data['nick']} already exists"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
