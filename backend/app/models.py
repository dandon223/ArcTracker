import uuid

from django.contrib.auth import models as auth_models
from django.core.exceptions import ValidationError
from django.db import models

# Create your models here.


class CardSuit(models.TextChoices):
    ADMINISTRATION = "ADMINISTRATION"
    AGGRESSION = "AGGRESSION"
    CONSTRUCTION = "CONSTRUCTION"
    MOBILIZATION = "MOBILIZATION"


class CardNumber(models.TextChoices):
    ONE = "ONE"
    TWO = "TWO"
    THREE = "THREE"
    FOUR = "FOUR"
    FIVE = "FIVE"
    SIX = "SIX"
    SEVEN = "SEVEN"


class CardsPlayedFaceDown(models.IntegerChoices):
    ZERO = 0
    ONE = 1
    TWO = 2


class Card(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    suit = models.CharField(max_length=20, choices=CardSuit.choices)
    number = models.CharField(max_length=20, choices=CardNumber.choices)

    class Meta:
        unique_together = ("suit", "number")

    def __str__(self) -> str:
        return self.suit + "." + self.number


class Player(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(auth_models.User, on_delete=models.CASCADE)
    nick = models.CharField(max_length=256)
    created_time = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return "Nick: " + str(self.nick)

    class Meta:
        unique_together = ("user", "nick")


class Game(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(auth_models.User, on_delete=models.CASCADE)
    name = models.CharField(max_length=256, null=False, blank=False)
    created_time = models.DateTimeField(auto_now_add=True)
    players = models.ManyToManyField(Player)
    cards_not_played = models.ManyToManyField(Card)
    finished = models.BooleanField(default=False)

    def __str__(self) -> str:
        return "Name: " + str(self.name) + " Players: " + str([player.nick for player in self.players.all()])

    class Meta:
        unique_together = ("user", "name")


class PlayerHand(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    cards = models.ManyToManyField(Card)
    number_of_cards = models.IntegerField()


class GameRound(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    chapter = models.IntegerField()
    round = models.IntegerField()

    class Meta:
        unique_together = ("game", "chapter", "round")


class CardPlayedInRound(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    game_round = models.ForeignKey(GameRound, on_delete=models.CASCADE)
    card_face_up = models.ForeignKey(Card, null=True, blank=True, on_delete=models.SET_NULL)
    number_of_cards_face_down = models.IntegerField(
        choices=CardsPlayedFaceDown.choices, default=CardsPlayedFaceDown.ZERO
    )

    class Meta:
        unique_together = ("player", "game_round")

    def clean(self) -> None:
        if self.card_face_up is not None and self.number_of_cards_face_down == CardsPlayedFaceDown.TWO:
            raise ValidationError("With played card face up you can only play up to one card face down.")
        if self.card_face_up is None and self.number_of_cards_face_down == CardsPlayedFaceDown.ZERO:
            raise ValidationError("You have to play atleast one card.")
