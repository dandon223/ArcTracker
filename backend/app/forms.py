from django import forms
from django.core.exceptions import ValidationError
from django.db.models import Case, IntegerField, Q, When

from .models import Card, CardNumber, CardPlayedInRound, Game, GameRound, Player, PlayerHand


class GameForm(forms.ModelForm):  # type: ignore[type-arg]
    class Meta:
        model = Game
        fields = ["name", "players"]

    players = forms.ModelMultipleChoiceField(queryset=Player.objects.all(), widget=forms.CheckboxSelectMultiple)

    def clean_players(self):
        players = self.cleaned_data.get("players")
        if players.count() < 2 or players.count() > 4:
            raise ValidationError("You must select between 2 and 4 players.")
        return players


class PlayerHandForm(forms.ModelForm):  # type: ignore[type-arg]
    class Meta:
        model = PlayerHand
        fields = ["player", "cards"]


class PlayerForm(forms.ModelForm):  # type: ignore[type-arg]
    class Meta:
        model = Player
        fields = ["nick"]


number_order = Case(
    When(number="ONE", then=1),
    When(number="TWO", then=2),
    When(number="THREE", then=3),
    When(number="FOUR", then=4),
    When(number="FIVE", then=5),
    When(number="SIX", then=6),
    When(number="SEVEN", then=7),
    output_field=IntegerField(),
)


class CardPlayedInRoundForm(forms.ModelForm):
    class Meta:
        model = CardPlayedInRound
        fields = ["card_face_up", "number_of_cards_face_down"]

    def __init__(self, *args, **kwargs):
        cards = kwargs.pop("cards", None)  # passed from view
        super().__init__(*args, **kwargs)

        if cards is not None:
            self.fields["card_face_up"].queryset = cards


class PlayerCardForm(forms.Form):
    card = forms.ModelChoiceField(queryset=Card.objects.none())

    def __init__(self, *args, **kwargs):
        cards = kwargs.pop("cards", None)  # passed from view
        super().__init__(*args, **kwargs)

        if cards is not None:
            self.fields["card"].queryset = cards


class NumberOfCardsAddedForm(forms.Form):
    number_of_cards = forms.IntegerField(initial=0)


class ChoosePlayerForm(forms.Form):
    player = forms.ModelChoiceField(queryset=Player.objects.none())

    def __init__(self, *args, **kwargs):
        players = kwargs.pop("players", None)  # passed from view
        super().__init__(*args, **kwargs)

        if players is not None:
            self.fields["player"].queryset = players


class RevealCardForm(forms.Form):
    player = forms.ModelChoiceField(queryset=Player.objects.none())
    card = forms.ModelChoiceField(queryset=Card.objects.none())

    def __init__(self, *args, **kwargs):
        players = kwargs.pop("players", None)  # passed from view
        cards = kwargs.pop("cards", None)  # passed from view
        super().__init__(*args, **kwargs)

        if players is not None:
            self.fields["player"].queryset = players
        if cards is not None:
            self.fields["card"].queryset = cards
