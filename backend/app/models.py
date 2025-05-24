import uuid

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

    def __str__(self) -> str:
        return self.suit + "." + self.number


class Player(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nick = models.CharField(max_length=256)
    created_time = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return "Nick: " + str(self.nick)


class Game(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=256)
    created_time = models.DateTimeField(auto_now_add=True)
    players = models.ManyToManyField(Player)
    finished = models.BooleanField(default=False)

    def __str__(self) -> str:
        return "Name: " + str(self.name) + " Players: " + str([player.nick for player in self.players.all()])


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
    card = models.ForeignKey(Card, null=True, blank=True, on_delete=models.SET_NULL)
    cards_face_down = models.IntegerField(choices=CardsPlayedFaceDown.choices, default=CardsPlayedFaceDown.ZERO)

    class Meta:
        unique_together = ("player", "game_round")

    def clean(self):
        from django.core.exceptions import ValidationError

        if self.card is not None and self.cards_face_down == CardsPlayedFaceDown.TWO:
            raise ValidationError("With played card face up you can only play up to one card face down.")
        if self.card is None and self.cards_face_down == CardsPlayedFaceDown.ZERO:
            raise ValidationError("You have to play atleast ine card.")


class CardRetrievedInRound(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    game_round = models.ForeignKey(GameRound, on_delete=models.CASCADE)
    card = models.ForeignKey(Card, on_delete=models.CASCADE)
