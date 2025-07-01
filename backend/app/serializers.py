from rest_framework import serializers

from .models import Player


class PlayerSerializer(serializers.ModelSerializer):  # type: ignore[misc]
    class Meta:
        model = Player
        fields = ["nick"]
