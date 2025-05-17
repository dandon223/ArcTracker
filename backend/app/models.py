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


class Game(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=256)
    created_time = models.DateTimeField(auto_now_add=True)
    finished = models.BooleanField(default=False)

    def __str__(self) -> str:
        return str(self.name)
