import uuid
from typing import Union, List, Tuple

from django.http import HttpRequest, HttpResponse, HttpResponseNotFound
from django.shortcuts import redirect, render
from django.db.models import Max, Case, When, IntegerField, Q
from collections import defaultdict

from .forms import GameForm, PlayerForm, CardPlayedInRoundForm, CardRetrievedInRoundForm
from .models import Game, Player, GameRound, CardNumber, CardSuit, CardPlayedInRound, CardRetrievedInRound, Card, PlayerHand

# Create your views here.

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

def menu(request: HttpRequest) -> HttpResponse:
    for suit in[suit.value for suit in CardSuit]:
        for number in [number.value for number in CardNumber]:
            if not Card.objects.filter(suit=suit, number=number).exists():
                Card(suit=suit, number=number).save()
    return render(request, "menu.html")


def new_game(request: HttpRequest) -> HttpResponse:
    form = GameForm()

    if request.method == "POST":
        form = GameForm(request.POST)
        if form.is_valid():
            game = form.save()
            game_round = GameRound(game=game, chapter=1, round = 1)
            game_round.save()
            for player in game.players.all():
                PlayerHand(player=player, game=game, number_of_cards=6).save()
            return redirect(f"/game/{game.id}/1/1")

    return render(request, "new_game.html", {"form": form})

def new_player(request: HttpRequest) -> HttpResponse:
    form = PlayerForm()

    if request.method == "POST":
        form = PlayerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(f"/new_player/")
    return render(request, "new_player.html", {"form": form})

def players(request: HttpRequest) -> HttpResponse:
    player_objects = Player.objects.all()
    return render(request, "view.html", {"name": "players", "models":player_objects})

def games(request: HttpRequest) -> HttpResponse:
    game_objects = Game.objects.all()
    return render(request, "view.html", {"name": "games", "models":game_objects})

def get_cards_to_play(game_object: Game, game_chapter: int, game_round: int):
    cards_out_of_play_tmp = {}

    card_by_str = {}
    if len(game_object.players.all()) < 4:
        card_objects = list(Card.objects.exclude(number__in = [CardNumber.ONE, CardNumber.SEVEN]))
    else:
        card_objects = list(Card.objects.all())
    for card_object in card_objects:
        card_by_str[str(card_object)] = card_object

    game_round_objects = GameRound.objects.filter(game=game_object, chapter=game_chapter).all()
    card_played_in_round_objects = CardPlayedInRound.objects.filter(game_round__in=game_round_objects).all()

    for card_played_in_round_object in card_played_in_round_objects:
        if card_played_in_round_object.card is None:
            continue
        key = str(card_played_in_round_object.card)
        if key not in cards_out_of_play_tmp:
            cards_out_of_play_tmp[key] = 1
        else:
            cards_out_of_play_tmp[key] = cards_out_of_play_tmp[key] +  1

    game_round_objects = GameRound.objects.filter(game=game_object, chapter=game_chapter).exclude(round=game_round).all()
    card_retrieved_in_round_objects = CardRetrievedInRound.objects.filter(game_round__in=game_round_objects).all()
    for card_retrieved_in_round_object in card_retrieved_in_round_objects:
        if card_retrieved_in_round_object.card is None:
            continue
        key = str(card_retrieved_in_round_object.card)
        cards_out_of_play_tmp[key] = cards_out_of_play_tmp[key] - 1

    for card, number in cards_out_of_play_tmp.items():
        if number == 1:
            card_by_str.pop(card)

    return Card.objects.filter(id__in=[card.id for card in card_by_str.values()]).order_by("suit", number_order).all()

def get_players_to_play(game_object: Game, game_chapter: int, game_round:int):
    player_objects = game_object.players.all()
    game_round_object = GameRound.objects.filter(game=game_object, chapter=game_chapter, round=game_round).get()
    player_ids = []
    for player_object in player_objects:
        if not CardPlayedInRound.objects.filter(game_round=game_round_object, player=player_object).exists():
            player_ids.append(player_object.id)
    return Player.objects.filter(pk__in=player_ids).all()

def get_cards_to_retrieve(game_object: Game, cards_to_play):
    player_objects = game_object.players.all()
    card_ids = [card.id for card in cards_to_play]
    for player_object in player_objects:
        player_hand_object = PlayerHand.objects.filter(game=game_object, player=player_object).get()
        for card_object in player_hand_object.cards.all():
            card_ids.append(card_object.id)
    if len(player_objects) == 4:
        return Card.objects.exclude(id__in=card_ids).order_by("suit", number_order).all()
    else:
        return Card.objects.exclude(Q(id__in=card_ids) | Q(number__in = [CardNumber.ONE, CardNumber.SEVEN])).order_by("suit", number_order).all()

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

def game(request: HttpRequest, game_id: uuid.UUID, game_chapter: int, game_round: int) -> Union[HttpResponse, HttpResponseNotFound]:
    if not Game.objects.filter(id=game_id).exists():
        return HttpResponseNotFound(f"game with id {game_id} not found")

    game_object = Game.objects.filter(id=game_id).get()

    cards_to_play = get_cards_to_play(game_object, game_chapter, game_round)
    cards_to_play_images = get_cards_to_play_images(cards_to_play)
    players_to_play = get_players_to_play(game_object, game_chapter, game_round)
    cards_to_retrive = get_cards_to_retrieve(game_object, cards_to_play)
    card_played_in_round_form = CardPlayedInRoundForm(players=players_to_play, cards=cards_to_play)
    card_retrived_in_round_form = CardRetrievedInRoundForm(players=game_object.players.all(), cards=cards_to_retrive)

    if request.method == "POST":
        submit_type = request.POST.get('submit_type')
        if submit_type == 'card_played':
            card_played_in_round_form = CardPlayedInRoundForm(request.POST)
            if card_played_in_round_form.is_valid():
                game_round_object = GameRound.objects.filter(game = game_object, chapter = game_chapter, round = game_round).get()
                card_played_in_round = card_played_in_round_form.save(commit=False)
                card_played_in_round.game_round = game_round_object
                card_played_in_round.save()
                player_hand = PlayerHand.objects.filter(player=card_played_in_round.player, game=game_object).get()
                if card_played_in_round.card is not None:
                    player_hand.number_of_cards -= 1
                player_hand.number_of_cards -= card_played_in_round.cards_face_down
                player_hand.save()
                return redirect(f"/game/{game_id}/{game_chapter}/{game_round}")
        elif submit_type == 'card_retrieved':
            card_retrived_in_round_form = CardRetrievedInRoundForm(request.POST)
            if card_retrived_in_round_form.is_valid():
                game_round_object = GameRound.objects.filter(game = game_object, chapter = game_chapter, round = game_round).get()
                card_retrieved_in_round = card_retrived_in_round_form.save(commit=False)
                card_retrieved_in_round.game_round = game_round_object
                card_retrieved_in_round.save()
                player_hand = PlayerHand.objects.filter(player=card_retrieved_in_round.player, game=game_object).get()
                player_hand.number_of_cards += 1
                player_hand.cards.add(card_retrieved_in_round.card)
                player_hand.save()
                return redirect(f"/game/{game_id}/{game_chapter}/{game_round}")
        elif submit_type == 'new_round':
            GameRound(game = game_object, chapter = game_chapter, round = game_round + 1).save()
            return redirect(f"/game/{game_id}/{game_chapter}/{game_round + 1}")
        elif submit_type == 'new_chapter':
            GameRound(game = game_object, chapter = game_chapter + 1, round = 1).save()
            player_objects = game_object.players.all()
            for player_object in player_objects:
                player_hand = PlayerHand.objects.filter(player=player_object, game=game_object).get()
                player_hand.cards.clear()
                player_hand.number_of_cards = 6
                player_hand.save()
            return redirect(f"/game/{game_id}/{game_chapter + 1}/{1}")

    cards_in_hand = get_cards_in_hand(game_object)

    cards_played_in_chapter = defaultdict(list)
    for player in game_object.players.all():
        cards_played_in_chapter[player.nick] = []
        for i in range(1, game_round + 1):
            cards_played_in_chapter[player.nick].append([])
            game_round_object = GameRound.objects.filter(game=game_object, chapter=game_chapter, round=i).get()
            if CardPlayedInRound.objects.filter(player=player, game_round=game_round_object).exists():
                card_played_in_round_object = CardPlayedInRound.objects.filter(player=player, game_round=game_round_object).get()
                if card_played_in_round_object.card is not None:
                    cards_played_in_chapter[player.nick][-1].append(card_played_in_round_object.card.suit + "/" + card_played_in_round_object.card.number + ".jpg")
                for i in range(0, card_played_in_round_object.cards_face_down):
                    cards_played_in_chapter[player.nick][-1].append("back.png")
            

    return render(request, "game.html", {"name": game_object.name,
                                         "cards_in_hand": cards_in_hand.items(),
                                         "cards_played": cards_played_in_chapter.items(),
                                         "rows_images": cards_to_play_images,
                                         "game_chapter": game_chapter,
                                         "game_round": game_round,
                                         "card_played_in_round_form": card_played_in_round_form,
                                         "card_retrived_in_round_form": card_retrived_in_round_form})
