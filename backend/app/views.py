import uuid
from typing import Union, List, Tuple

from django.http import HttpRequest, HttpResponse, HttpResponseNotFound
from django.shortcuts import redirect, render
from django.db.models import Max

from .forms import GameForm, PlayerForm, CardPlayedInRoundForm, CardRetrievedInRoundForm
from .models import Game, Player, GameRound, CardNumber, CardSuit, CardPlayedInRound, CardRetrievedInRound, Card

# Create your views here.


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

def get_cards_in_play(game_object: Game, game_chapter: int, game_round: int) -> Tuple[List[str], List[str]]:
    cards_out_of_play_tmp = {}

    card_by_str = {}
    if len(game_object.players.all()) < 4:
        card_objects = list(Card.objects.exclude(number__in = [CardNumber.ONE, CardNumber.SEVEN]))
    else:
        card_objects = list(Card.objects.all())
    for card_object in card_objects:
        card_by_str[str(card_object)] = card_object

    game_round_objects = GameRound.objects.filter(game=game_object, chapter=game_chapter).all()
    card_played_in_round_objects = CardPlayedInRound.objects.filter(game_round__in = game_round_objects).all()

    for card_played_in_round_object in card_played_in_round_objects:
        key = str(card_played_in_round_object.card)
        if key not in cards_out_of_play_tmp:
            cards_out_of_play_tmp[key] = 1
        else:
            cards_out_of_play_tmp[key] = cards_out_of_play_tmp[key] +  1

    game_round_objects = GameRound.objects.filter(game=game_object, chapter=game_chapter).exclude(round=game_round).all()
    card_retrieved_in_round_objects = CardRetrievedInRound.objects.filter(game_round__in = game_round_objects).all()
    for card_retrieved_in_round_object in card_retrieved_in_round_objects:
        key = str(card_retrieved_in_round_object.card)
        cards_out_of_play_tmp[key] = cards_out_of_play_tmp[key] - 1
    
    for card, number in cards_out_of_play_tmp.items():
        if number == 1:
            card_by_str.pop(card)
    return list(card_by_str.keys()), list(card_by_str.values())

def game(request: HttpRequest, game_id: uuid.UUID, game_chapter: int, game_round: int) -> Union[HttpResponse, HttpResponseNotFound]:
    if not Game.objects.filter(id=game_id).exists():
        return HttpResponseNotFound(f"game with id {game_id} not found")

    game_object = Game.objects.filter(id=game_id).get()
    cards_in_play_by_str, cards_in_play = get_cards_in_play(game_object, game_chapter, game_round)
    card_played_in_round_form = CardPlayedInRoundForm(game=game_object, cards=cards_in_play, chapter=game_chapter, round=game_round)
    card_retrived_in_round_form = CardRetrievedInRoundForm(game=game_object, cards=cards_in_play)

    if request.method == "POST":
        submit_type = request.POST.get('submit_type')
        if submit_type == 'card_played':
            card_played_in_round_form = CardPlayedInRoundForm(request.POST)
            if card_played_in_round_form.is_valid():
                game_round_object = GameRound.objects.filter(game = game_object, chapter = game_chapter, round = game_round).get()
                card_played_in_round = card_played_in_round_form.save(commit=False)
                card_played_in_round.game_round = game_round_object
                card_played_in_round.save()
                return redirect(f"/game/{game_id}/{game_chapter}/{game_round}")
        elif submit_type == 'card_retrieved':
            card_retrived_in_round_form = CardRetrievedInRoundForm(request.POST)
            if card_retrived_in_round_form.is_valid():
                game_round_object = GameRound.objects.filter(game = game_object, chapter = game_chapter, round = game_round).get()
                card_retrieved_in_round = card_retrived_in_round_form.save(commit=False)
                card_retrieved_in_round.game_round = game_round_object
                card_retrieved_in_round.save()
                return redirect(f"/game/{game_id}/{game_chapter}/{game_round}")
        elif submit_type == 'new_round':
            GameRound(game = game_object, chapter = game_chapter, round = game_round + 1).save()
            return redirect(f"/game/{game_id}/{game_chapter}/{game_round + 1}")
        elif submit_type == 'new_chapter':
            GameRound(game = game_object, chapter = game_chapter + 1, round = 1).save()
            return redirect(f"/game/{game_id}/{game_chapter + 1}/{1}")

    rows_images = []
    for suit_name in [suit.value for suit in CardSuit]:
        images_tmp = []
        for number_value in [number.value for number in CardNumber]:
            if suit_name + "." + number_value in cards_in_play_by_str:
                images_tmp.append(suit_name + "/" + number_value + ".jpg")
        rows_images.append(images_tmp)

    cards_in_hand = {}

    cards_played_in_chapter = []
    for player in game_object.players.all():
        cards_played_in_chapter.append(player.nick)
        cards_in_hand[player.nick] = 6
        for i in range(1, game_round + 1):
            game_round_object = GameRound.objects.filter(game=game_object, chapter=game_chapter, round=i).get()
            if CardPlayedInRound.objects.filter(player=player, game_round=game_round_object).exists():
                card_played_in_round_object = CardPlayedInRound.objects.filter(player=player, game_round=game_round_object).get()
                cards_played_in_chapter[-1] += f" round {i}: {card_played_in_round_object.card}"
                cards_in_hand[player.nick] -= card_played_in_round_object.cards_face_down + 1

    cards_retrieved_in_chapter = []
    for player in game_object.players.all():
        cards_retrieved_in_chapter.append(player.nick)
        for i in range(1, game_round + 1):
            game_round_object = GameRound.objects.filter(game=game_object, chapter=game_chapter, round=i).get()
            if CardRetrievedInRound.objects.filter(player=player, game_round=game_round_object).exists():
                card_played_in_round_object = CardRetrievedInRound.objects.filter(player=player, game_round=game_round_object).get()
                cards_in_hand[player.nick] +=1
                cards_retrieved_in_chapter[-1] += f" round {i}: {card_played_in_round_object.card}"

    return render(request, "game.html", {"name": game_object.name,
                                         "cards_in_hand": cards_in_hand.items(),
                                         "cards_played": cards_played_in_chapter,
                                         "cards_retrieved": cards_retrieved_in_chapter,
                                         "rows_images": rows_images,
                                         "game_chapter": game_chapter,
                                         "game_round": game_round,
                                         "card_played_in_round_form": card_played_in_round_form,
                                         "card_retrived_in_round_form": card_retrived_in_round_form})
