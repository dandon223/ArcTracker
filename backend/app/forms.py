from django import forms
from django.core.exceptions import ValidationError
from .models import Game, Player


class GameForm(forms.ModelForm):  # type: ignore[type-arg]
    class Meta:
        model = Game
        fields = ["name", "players"]
    players = forms.ModelMultipleChoiceField(
        queryset=Player.objects.all(),
        widget=forms.CheckboxSelectMultiple
    )
    def clean_players(self):
        players = self.cleaned_data.get('players')
        if (players.count() < 2 or players.count() > 4):
            raise ValidationError("You must select between 2 and 4 players.")
        return players

class PlayerForm(forms.ModelForm):  # type: ignore[type-arg]
    class Meta:
        model = Player
        fields = ["nick"]
