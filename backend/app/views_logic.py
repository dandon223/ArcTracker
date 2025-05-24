import uuid
from collections import defaultdict
from typing import List, Tuple, Union

from django.db.models import Case, IntegerField, When

from .models import (
    Card,
    CardNumber,
    CardPlayedInRound,
    Game,
    GameRound,
    Player,
    PlayerHand,
)

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


def assign_cards(game_object: Game):
    """Assign appropriate cards to the game based on player count."""
    if game_object.players.count() < 4:
        cards = Card.objects.exclude(number__in=[CardNumber.ONE, CardNumber.SEVEN])
    else:
        cards = Card.objects.all()
    game_object.cards_not_played.set(cards)


def create_initial_round(game_object: Game):
    """Create the first round of the game."""
    GameRound.objects.create(game=game_object, chapter=1, round=1)


def deal_initial_hands(game_object: Game):
    """Give each player their starting hand."""
    PlayerHand.objects.bulk_create(
        [PlayerHand(player=player, game=game_object, number_of_cards=6) for player in game_object.players.all()]
    )


def start_new_chapter(game_object: Game, chapter: int):
    GameRound.objects.create(game=game_object, chapter=chapter + 1, round=1)
    assign_cards(game_object)

    for player in game_object.players.all():
        hand = PlayerHand.objects.get(player=player, game=game_object)
        hand.cards.clear()
        hand.number_of_cards = 6
        hand.save()


def get_cards_to_play_fixed(game_object, player_object):
    player_hand_object = PlayerHand.objects.get(player=player_object, game=game_object)
    player_card_ids = player_hand_object.cards.values_list("id", flat=True)
    not_played_card_ids = game_object.cards_not_played.values_list("id", flat=True)
    card_ids = list(player_card_ids) + list(not_played_card_ids)
    return Card.objects.filter(id__in=card_ids).order_by("suit", number_order)


def get_cards_to_retrieve(game_object: Game, player_object_active: Player, game_chapter, game_round):
    game_round_object = GameRound.objects.get(game=game_object, chapter=game_chapter, round=game_round)
    card_ids_played_in_round = CardPlayedInRound.objects.filter(game_round=game_round_object).values_list(
        "card_face_up__id", flat=True
    )
    return Card.objects.filter(id__in=card_ids_played_in_round).order_by("suit", number_order)


def get_cards_to_play_images(cards_to_play):
    rows_images = defaultdict(list)
    for card_to_play in cards_to_play:
        rows_images[card_to_play.suit].append(card_to_play.suit + "/" + card_to_play.number + ".jpg")
    return rows_images.values()


def get_cards_in_hand(game_object: Game):
    player_objects = game_object.players.all()
    cards_in_hand = defaultdict(list)
    for player_object in player_objects:
        player_hand_object = PlayerHand.objects.filter(player=player_object, game=game_object).get()
        player_card_objects = player_hand_object.cards.all()
        for player_card_object in player_card_objects:
            cards_in_hand[player_object.nick].append(player_card_object.suit + "/" + player_card_object.number + ".jpg")
        for i in range(0, player_hand_object.number_of_cards - len(player_card_objects)):
            cards_in_hand[player_object.nick].append("back.png")
    return cards_in_hand


def get_cards_played_by_round(game_object, game_chapter, game_round):
    cards_played_in_chapter = defaultdict(list)
    for player in game_object.players.all():
        cards_played_in_chapter[player.nick] = []
        for i in range(1, game_round + 1):
            cards_played_in_chapter[player.nick].append([])
            game_round_object = GameRound.objects.filter(game=game_object, chapter=game_chapter, round=i).get()
            if CardPlayedInRound.objects.filter(player=player, game_round=game_round_object).exists():
                card_played_in_round_object = CardPlayedInRound.objects.filter(
                    player=player, game_round=game_round_object
                ).get()
                if card_played_in_round_object.card_face_up is not None:
                    cards_played_in_chapter[player.nick][-1].append(
                        card_played_in_round_object.card_face_up.suit
                        + "/"
                        + card_played_in_round_object.card_face_up.number
                        + ".jpg"
                    )
                for i in range(0, card_played_in_round_object.number_of_cards_face_down):
                    cards_played_in_chapter[player.nick][-1].append("back.png")
    return cards_played_in_chapter


def handle_card_played(card_played_in_round_form, game_object, player_object, game_chapter, game_round):
    card_played = card_played_in_round_form.save(commit=False)
    card_played.player = player_object
    card_played.game_round = GameRound.objects.get(game=game_object, chapter=game_chapter, round=game_round)
    card_played.save()
    player_hand = PlayerHand.objects.get(player=player_object, game=game_object)

    if card_played.card_face_up:
        player_hand.number_of_cards -= 1
        game_object.cards_not_played.remove(card_played.card_face_up)
        game_object.save()

    player_hand.number_of_cards -= card_played.number_of_cards_face_down
    player_hand.save()


def handle_card_retrieved(card_retrived_in_round_form, game_object, player_object):
    player_hand = PlayerHand.objects.filter(player=player_object, game=game_object).get()
    player_hand.number_of_cards += 1
    player_hand.cards.add(card_retrived_in_round_form.cleaned_data["card"])
    player_hand.save()
    game_object.cards_not_played.remove(card_retrived_in_round_form.cleaned_data["card"])


def handle_number_of_cards_added(number_of_cards_added_form, player_object):
    player_hand_object = PlayerHand.objects.get(player=player_object)
    player_hand_object.number_of_cards += number_of_cards_added_form.cleaned_data["number_of_cards"]
    player_hand_object.save()


def handle_reveal_card(reveal_card_form, game_object, player_object):
    player_hand_object = PlayerHand.objects.filter(player=player_object, game=game_object).get()
    player_hand_object.cards.add(reveal_card_form.cleaned_data["card"])
    player_hand_object.save()
    game_object.cards_not_played.remove(reveal_card_form.cleaned_data["card"])


def handle_unreveal_card(unreveal_card_form, game_object, player_object):
    player_hand_object = PlayerHand.objects.filter(player=player_object, game=game_object).get()
    player_hand_object.cards.remove(unreveal_card_form.cleaned_data["card"])
    player_hand_object.save()
    game_object.cards_not_played.add(unreveal_card_form.cleaned_data["card"])
