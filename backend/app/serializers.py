from rest_framework import serializers

from .models import CardPlayedInRound, Game, GameRound, Player


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
        fields = ["player", "card_face_up", "number_of_cards_face_down"]

    def validate(self, attrs):  # type: ignore[no-untyped-def]
        instance = CardPlayedInRound(**attrs)
        instance.clean()
        return attrs


class CardPlayedInRoundSerializerGet(serializers.ModelSerializer):  # type: ignore[misc]
    class Meta:
        model = CardPlayedInRound
        fields = ["id", "player", "game_round", "card_face_up", "number_of_cards_face_down"]
