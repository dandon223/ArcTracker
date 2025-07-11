from rest_framework import serializers

from .models import Game, Player


class PlayerSerializerGet(serializers.ModelSerializer):  # type: ignore[misc]
    class Meta:
        model = Player
        fields = ["nick", "id"]


class PlayerSerializerPost(serializers.ModelSerializer):  # type: ignore[misc]
    class Meta:
        model = Player
        fields = ["nick"]


class GameSerializerGet(serializers.ModelSerializer):  # type: ignore[misc]
    class Meta:
        model = Game
        fields = ["name", "players", "cards_not_played", "finished"]


class GameSerializerPost(serializers.ModelSerializer):  # type: ignore[misc]
    class Meta:
        model = Game
        fields = ["name", "players"]
