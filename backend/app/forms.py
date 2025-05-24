from typing import Optional

from django import forms
from django.core.exceptions import ValidationError
from django.db.models.query import QuerySet

from .models import Card, CardPlayedInRound, Game, Player


class GameForm(forms.ModelForm):  # type: ignore[type-arg]
    class Meta:
        model = Game
        fields = ["name", "players"]

    players = forms.ModelMultipleChoiceField(queryset=Player.objects.all(), widget=forms.CheckboxSelectMultiple)

    def clean_players(self):  # type: ignore[no-untyped-def]
        players = self.cleaned_data.get("players")
        assert players is not None
        if players.count() < 2 or players.count() > 4:
            raise ValidationError("You must select between 2 and 4 players.")
        return players


class PlayerForm(forms.ModelForm):  # type: ignore[type-arg]
    class Meta:
        model = Player
        fields = ["nick"]


class CardPlayedInRoundForm(forms.ModelForm):  # type: ignore[type-arg]
    class Meta:
        model = CardPlayedInRound
        fields = ["card_face_up", "number_of_cards_face_down"]

    def __init__(self, *args, cards: Optional[QuerySet[Card]] = None, **kwargs):  # type: ignore[no-untyped-def]
        super().__init__(*args, **kwargs)

        if cards is not None:
            self.fields["card_face_up"].queryset = cards  # type: ignore[attr-defined]


class PlayerCardForm(forms.Form):
    card = forms.ModelChoiceField(queryset=Card.objects.none())

    def __init__(self, *args, cards: Optional[QuerySet[Card]] = None, **kwargs):  # type: ignore[no-untyped-def]
        super().__init__(*args, **kwargs)

        if cards is not None:
            self.fields["card"].queryset = cards  # type: ignore[attr-defined]


class NumberOfCardsAddedForm(forms.Form):
    number_of_cards = forms.IntegerField(initial=0)


class ChoosePlayerForm(forms.Form):
    player = forms.ModelChoiceField(queryset=Player.objects.none())

    def __init__(self, *args, players: Optional[QuerySet[Player]] = None, **kwargs):  # type: ignore[no-untyped-def]
        super().__init__(*args, **kwargs)

        if players is not None:
            self.fields["player"].queryset = players  # type: ignore[attr-defined]
