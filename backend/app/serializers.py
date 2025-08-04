from typing import Any

from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Card, CardPlayedInRound, Game, GameRound, Player

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):  # type: ignore[misc]
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("username", "password")

    def create(self, validated_data: Any) -> Any:
        user = User.objects.create_user(username=validated_data["username"], password=validated_data["password"])
        return user


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
        fields = ["id", "name", "players", "cards_not_played", "finished"]


class GameSerializerPost(serializers.ModelSerializer):  # type: ignore[misc]
    class Meta:
        model = Game
        fields = ["name", "players"]


class GameRoundSerializerGet(serializers.ModelSerializer):  # type: ignore[misc]
    class Meta:
        model = GameRound
        fields = ["id", "game", "chapter", "round"]


class CardPlayedInRoundSerializerPost(serializers.ModelSerializer):  # type: ignore[misc]
    class Meta:
        model = CardPlayedInRound
        fields = ["card_face_up", "number_of_cards_face_down"]

    def validate(self, attrs):  # type: ignore[no-untyped-def]
        instance = CardPlayedInRound(**attrs)
        instance.clean()
        return attrs


class CardPlayedInRoundSerializerGet(serializers.ModelSerializer):  # type: ignore[misc]
    class Meta:
        model = CardPlayedInRound
        fields = ["id", "player", "game_round", "card_face_up", "number_of_cards_face_down"]


class CardSerializerGet(serializers.ModelSerializer):  # type: ignore[misc]
    class Meta:
        model = Card
        fields = ["id", "suit", "number"]


class CardSerializerPost(serializers.Serializer):  # type: ignore[misc]
    id = serializers.PrimaryKeyRelatedField(queryset=Card.objects.all())

    def update(self, instance: Any, validated_data: Any) -> Any:
        raise NotImplementedError("Update is not supported.")

    def create(self, validated_data: Any) -> Any:
        raise NotImplementedError("Create is not supported.")


class NumberOfCardsAddedSerializerPost(serializers.Serializer):  # type: ignore[misc]
    number_of_cards = serializers.IntegerField()

    def validate(self, attrs):  # type: ignore[no-untyped-def]
        if attrs["number_of_cards"] <= 0:
            raise serializers.ValidationError({"error": "number_of_cards must be greater than zero"})
        return attrs

    def update(self, instance: Any, validated_data: Any) -> Any:
        raise NotImplementedError("Update is not supported.")

    def create(self, validated_data: Any) -> Any:
        raise NotImplementedError("Create is not supported.")
