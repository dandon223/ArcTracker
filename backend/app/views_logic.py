import uuid
from collections import defaultdict
from typing import Dict, List

from django.db.models import Case, IntegerField, When
from django.db.models.query import QuerySet

from .forms import CardPlayedInRoundForm, NumberOfCardsAddedForm, PlayerCardForm
from .models import Card, CardNumber, CardPlayedInRound, Game, GameRound, Player, PlayerHand

cards_number_order = Case(
    When(number="ONE", then=1),
    When(number="TWO", then=2),
    When(number="THREE", then=3),
    When(number="FOUR", then=4),
    When(number="FIVE", then=5),
    When(number="SIX", then=6),
    When(number="SEVEN", then=7),
    output_field=IntegerField(),
)


def assign_cards(game: Game) -> None:
    """Assign appropriate cards to the game based on player count.

    :param game: Game object
    """
    if game.players.count() < 4:
        cards = Card.objects.exclude(number__in=[CardNumber.ONE, CardNumber.SEVEN])
    else:
        cards = Card.objects.all()
    game.cards_not_played.set(cards)


def create_initial_round(game: Game) -> None:
    """Create the first round of the game.

    :param game: Game object
    """
    GameRound.objects.create(game=game, chapter=1, round=1)


def deal_initial_hands(game: Game) -> None:
    """Give each player their starting hand.

    :param game: Game object
    """
    PlayerHand.objects.bulk_create(
        [PlayerHand(player=player, game=game, number_of_cards=6) for player in game.players.all()]
    )


def start_new_chapter(game: Game, chapter_number: int) -> None:
    """Creates new chapter and prepares new card hands for players

    :param game: Game object
    :param chapter_number: Number of new chapter
    """
    GameRound.objects.create(game=game, chapter=chapter_number + 1, round=1)
    assign_cards(game)

    for player in game.players.all():
        hand = PlayerHand.objects.get(player=player, game=game)
        hand.cards.clear()
        hand.number_of_cards = 6
        hand.save()


def get_cards_to_play(game: Game, player: Player) -> QuerySet[Card]:
    """Returns cards that we believe the player can play in this round

    :param game: Game object
    :param player: Active Player object
    :return: QuerySet of cards
    """
    player_hand = PlayerHand.objects.get(player=player, game=game)
    player_card_ids = player_hand.cards.values_list("id", flat=True)
    not_played_card_ids = game.cards_not_played.values_list("id", flat=True)
    card_ids = list(player_card_ids) + list(not_played_card_ids)
    return Card.objects.filter(id__in=card_ids).order_by("suit", cards_number_order)


def get_cards_to_reveal(game: Game) -> QuerySet[Card]:
    """Returns cards that we believe the player can reveal in this round

    :param game: Game object
    :return: QuerySet of cards
    """
    not_played_card_ids = game.cards_not_played.values_list("id", flat=True)
    return Card.objects.filter(id__in=not_played_card_ids).order_by("suit", cards_number_order)


def get_cards_to_retrieve(game: Game, chapter_number: int, round_number: int) -> QuerySet[Card]:
    """Returns cards that we believe the player can retrieve in this round (played cars in active round face up)

    :param game: Game object
    :param chapter_number: game chapter
    :param round_number: chapter round
    :return: QuerySet of cards
    """
    game_round = GameRound.objects.get(game=game, chapter=chapter_number, round=round_number)
    card_ids_played_in_round = CardPlayedInRound.objects.filter(game_round=game_round).values_list(
        "card_face_up__id", flat=True
    )
    player_card_ids: List[uuid.UUID] = [
        card_id
        for card_id in PlayerHand.objects.filter(game=game, player__in=game.players.all()).values_list(
            "cards__id", flat=True
        )
        if card_id is not None
    ]
    return (
        Card.objects.filter(id__in=card_ids_played_in_round)
        .exclude(id__in=player_card_ids)
        .order_by("suit", cards_number_order)
    )


def get_cards_to_images_by_suit(cards: QuerySet[Card]) -> Dict[str, List[str]]:
    """Prepares cards to be show in frontend as images. It sorts them by card suit.

    :param cards: cards that we want to show
    :return: Dictionary with keys as suit and image paths as values
    """
    cards_by_suit: Dict[str, List[str]] = defaultdict(list)
    for card in cards:
        cards_by_suit[card.suit].append(card.suit + "/" + card.number + ".jpg")
    return cards_by_suit


def get_cards_to_images_by_hand(game: Game) -> Dict[str, List[str]]:
    """Prepares cards in players hand to be show in frontend as images. It sorts them by player names.

    :param game: Game object
    :return: Dictionary with keys as players nick and image paths as values
    """
    cards_by_hand: Dict[str, List[str]] = defaultdict(list)
    for player in game.players.all():
        player_hand = PlayerHand.objects.get(player=player, game=game)
        for player_card in player_hand.cards.all():
            cards_by_hand[player.nick].append(player_card.suit + "/" + player_card.number + ".jpg")
        for _ in range(0, player_hand.number_of_cards - player_hand.cards.count()):
            cards_by_hand[player.nick].append("back.png")
    return cards_by_hand


def get_cards_played_by_round(game: Game, chapter_number: int, round_number: int) -> Dict[str, List[List[str]]]:
    """Prepares history of played cards in chapter till given round by players. It sorts them by player names.

    :param game: Game object
    :param chapter_number: game chapter
    :param round_number: chapter round
    :return: Dictionary with keys as players nick and List of image paths of cards played in rounds as values
    """
    cards_played_in_chapter: Dict[str, List[List[str]]] = defaultdict(list)
    for player in game.players.all():
        cards_played_in_chapter[player.nick] = []
        for i in range(1, round_number + 1):
            cards_played_in_chapter[player.nick].append([])
            game_round = GameRound.objects.get(game=game, chapter=chapter_number, round=i)
            if CardPlayedInRound.objects.filter(player=player, game_round=game_round).exists():
                card_played_in_round = CardPlayedInRound.objects.filter(player=player, game_round=game_round).get()
                if card_played_in_round.card_face_up is not None:
                    cards_played_in_chapter[player.nick][-1].append(
                        card_played_in_round.card_face_up.suit + "/" + card_played_in_round.card_face_up.number + ".jpg"
                    )
                for i in range(0, card_played_in_round.number_of_cards_face_down):
                    cards_played_in_chapter[player.nick][-1].append("back.png")
    return cards_played_in_chapter


def handle_card_played(
    card_played_in_round_form: CardPlayedInRoundForm, game: Game, player: Player, chapter_number: int, round_number: int
) -> None:
    """Handles card_played POST submit

    :param card_played_in_round_form: card played by active player
    :param game: Game object
    :param player: Player object
    :param chapter_number: int
    :param round_number: int
    """
    card_played: CardPlayedInRound = card_played_in_round_form.save(commit=False)
    card_played.player = player
    card_played.game_round = GameRound.objects.get(game=game, chapter=chapter_number, round=round_number)
    card_played.save()
    player_hand = PlayerHand.objects.get(player=player, game=game)

    if card_played.card_face_up:
        player_hand.number_of_cards -= 1
        game.cards_not_played.remove(card_played.card_face_up)
        game.save()

    player_hand.number_of_cards -= card_played.number_of_cards_face_down
    player_hand.save()


def handle_card_retrieved(card_retrived_in_round_form: PlayerCardForm, game: Game, player: Player) -> None:
    """Handles card_retrieved POST submit

    :param card_retrived_in_round_form: card retrieved by active player
    :param game: Game object
    :param player: Player object
    """
    player_hand = PlayerHand.objects.get(player=player, game=game)
    player_hand.number_of_cards += 1
    player_hand.cards.add(card_retrived_in_round_form.cleaned_data["card"])
    player_hand.save()
    game.cards_not_played.remove(card_retrived_in_round_form.cleaned_data["card"])


def handle_number_of_cards_added(number_of_cards_added_form: NumberOfCardsAddedForm, player: Player) -> None:
    """Handles number_of_cards_added POST submit

    :param number_of_cards_added_form: cards added by active player
    :param player: Player object
    """
    player_hand = PlayerHand.objects.get(player=player)
    player_hand.number_of_cards += number_of_cards_added_form.cleaned_data["number_of_cards"]
    player_hand.save()


def handle_reveal_card(reveal_card_form: PlayerCardForm, game: Game, player: Player) -> None:
    """Handles reveal_card POST submit

    :param reveal_card_form: card revealed by active player
    :param game: Game object
    :param player: Player object
    """
    player_hand_object = PlayerHand.objects.filter(player=player, game=game).get()
    player_hand_object.cards.add(reveal_card_form.cleaned_data["card"])
    player_hand_object.save()
    game.cards_not_played.remove(reveal_card_form.cleaned_data["card"])


def handle_unreveal_card(unreveal_card_form: PlayerCardForm, game: Game, player: Player) -> None:
    """Handles unreveal_card POST submit

    :param unreveal_card_form: card unrevealed by active player
    :param game: Game object
    :param player: Player object
    """
    player_hand_object = PlayerHand.objects.filter(player=player, game=game).get()
    player_hand_object.cards.remove(unreveal_card_form.cleaned_data["card"])
    player_hand_object.save()
    game.cards_not_played.add(unreveal_card_form.cleaned_data["card"])
