from django import forms
from django.core.exceptions import ValidationError
from .models import Game, Player, CardPlayedInRound, Card, CardRetrievedInRound
from django.db.models import Case, When, IntegerField


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

number_order = Case(
    When(number='ONE', then=1),
    When(number='TWO', then=2),
    When(number='THREE', then=3),
    When(number='FOUR', then=4),
    When(number='FIVE', then=5),
    When(number='SIX', then=6),
    When(number='SEVEN', then=7),
    output_field=IntegerField()
)
class CardPlayedInRoundForm(forms.ModelForm):
    class Meta:
        model = CardPlayedInRound
        fields = ["player", "card", "card_face_down"]

    def __init__(self, *args, **kwargs):
        game = kwargs.pop('game', None)  # passed from view
        cards = kwargs.pop('cards', None)  # passed from view
        super().__init__(*args, **kwargs)

        if game is not None:
            assert isinstance(game, Game)
            self.fields['player'].queryset = game.players.get_queryset()
        if cards is not None:
            assert isinstance(cards, list)
            for card in cards:
                assert isinstance(card, Card)
            ids = [card.id for card in cards]
            self.fields['card'].queryset = Card.objects.filter(id__in=ids).order_by("suit", number_order)

class CardRetrievedInRoundForm(forms.ModelForm):
    class Meta:
        model = CardRetrievedInRound
        fields = ["player", "card"]

    def __init__(self, *args, **kwargs):
        game = kwargs.pop('game', None)  # passed from view
        cards = kwargs.pop('cards', None)  # passed from view
        super().__init__(*args, **kwargs)

        if game is not None:
            assert isinstance(game, Game)
            self.fields['player'].queryset = game.players.get_queryset()
        if cards is not None:
            assert isinstance(cards, list)
            for card in cards:
                assert isinstance(card, Card)
            ids = [card.id for card in cards]
            self.fields['card'].queryset = Card.objects.exclude(id__in=ids).order_by("suit", number_order)