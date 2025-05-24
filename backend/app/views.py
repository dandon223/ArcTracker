import uuid
from typing import Union

from django.db.models import Case, IntegerField, When
from django.http import HttpRequest, HttpResponse, HttpResponseNotFound
from django.shortcuts import redirect, render

from .forms import (
    CardPlayedInRoundForm,
    ChoosePlayerForm,
    GameForm,
    NumberOfCardsAddedForm,
    PlayerCardForm,
    PlayerForm,
    RevealCardForm,
)
from .models import (
    Card,
    CardNumber,
    CardPlayedInRound,
    CardSuit,
    Game,
    GameRound,
    Player,
    PlayerHand,
)
from .views_logic import (
    assign_cards,
    create_initial_round,
    deal_initial_hands,
    get_cards_in_hand,
    get_cards_played_by_round,
    get_cards_to_play_fixed,
    get_cards_to_play_images,
    get_cards_to_retrieve,
    handle_card_played,
    handle_card_retrieved,
    handle_number_of_cards_added,
    handle_reveal_card,
    handle_unreveal_card,
    number_order,
    start_new_chapter,
)

# Create your views here.


def menu(request: HttpRequest) -> HttpResponse:
    for suit in [suit.value for suit in CardSuit]:
        for number in [number.value for number in CardNumber]:
            if not Card.objects.filter(suit=suit, number=number).exists():
                Card(suit=suit, number=number).save()
    return render(request, "menu.html")


def new_game(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        game_form = GameForm(request.POST)
        if game_form.is_valid():
            game = game_form.save()
            assign_cards(game)
            create_initial_round(game)
            deal_initial_hands(game)
            return redirect(f"/game/{game.id}/1/1")
    else:
        game_form = GameForm()

    return render(request, "new_game.html", {"game_form": game_form})


def new_player(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = PlayerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(f"/new_player/")
    else:
        form = PlayerForm()
    return render(request, "new_player.html", {"form": form})


def players(request: HttpRequest) -> HttpResponse:
    return render(request, "view.html", {"name": "players", "models": Player.objects.all()})


def games(request: HttpRequest) -> HttpResponse:
    return render(request, "view.html", {"name": "games", "models": Game.objects.all()})


def new_action(
    request: HttpRequest, game_id: uuid.UUID, game_chapter: int, game_round: int, player_id: uuid.UUID
) -> Union[HttpResponse, HttpResponseNotFound]:
    if not Game.objects.filter(id=game_id).exists():
        return HttpResponseNotFound(f"game with id {game_id} not found")
    game_object = Game.objects.filter(id=game_id).get()
    player_object = Player.objects.filter(id=player_id).get()
    player_hand_object = PlayerHand.objects.get(player=player_object, game=game_object)

    card_played_in_round_form = CardPlayedInRoundForm(cards=get_cards_to_play_fixed(game_object, player_object))
    card_retrived_in_round_form = PlayerCardForm(
        cards=get_cards_to_retrieve(game_object, player_object, game_chapter, game_round)
    )
    number_of_cards_added_form = NumberOfCardsAddedForm()
    reveal_card_form = PlayerCardForm(cards=get_cards_to_play_fixed(game_object, player_object))
    unreveal_card_form = PlayerCardForm(cards=player_hand_object.cards.all())

    if request.method == "POST":
        submit_type = request.POST.get("submit_type")
        if submit_type == "card_played":
            card_played_in_round_form = CardPlayedInRoundForm(
                request.POST, cards=get_cards_to_play_fixed(game_object, player_object)
            )
            if card_played_in_round_form.is_valid():
                handle_card_played(card_played_in_round_form, game_object, player_object, game_chapter, game_round)
                return redirect(f"/game/{game_object.id}/{game_chapter}/{game_round}")
        elif submit_type == "card_retrieved":
            card_retrived_in_round_form = PlayerCardForm(
                request.POST, cards=get_cards_to_retrieve(game_object, player_object, game_chapter, game_round)
            )
            if card_retrived_in_round_form.is_valid():
                handle_card_retrieved(card_retrived_in_round_form, game_object, player_object)
                return redirect(f"/game/{game_id}/{game_chapter}/{game_round}")
        elif submit_type == "number_of_cards_added":
            number_of_cards_added_form = NumberOfCardsAddedForm(request.POST)
            if number_of_cards_added_form.is_valid():
                handle_number_of_cards_added(number_of_cards_added_form, player_object)
                return redirect(f"/game/{game_id}/{game_chapter}/{game_round}")
        elif submit_type == "reveal_card":
            reveal_card_form = PlayerCardForm(request.POST, cards=get_cards_to_play_fixed(game_object, player_object))
            if reveal_card_form.is_valid():
                handle_reveal_card(reveal_card_form, game_object, player_object)
                return redirect(f"/game/{game_id}/{game_chapter}/{game_round}")
        elif submit_type == "unreveal_card":
            unreveal_card_form = PlayerCardForm(request.POST, cards=player_hand_object.cards.all())
            if unreveal_card_form.is_valid():
                handle_unreveal_card(reveal_card_form, game_object, player_object)
                return redirect(f"/game/{game_id}/{game_chapter}/{game_round}")

    return render(
        request,
        "new_action.html",
        {
            "card_played_in_round_form": card_played_in_round_form,
            "card_retrived_in_round_form": card_retrived_in_round_form,
            "number_of_cards_added_form": number_of_cards_added_form,
            "reveal_card_form": reveal_card_form,
            "unreveal_card_form": unreveal_card_form,
        },
    )


def game(
    request: HttpRequest, game_id: uuid.UUID, game_chapter: int, game_round: int
) -> Union[HttpResponse, HttpResponseNotFound]:
    if not Game.objects.filter(id=game_id).exists():
        return HttpResponseNotFound(f"game with id {game_id} not found")

    game_object = Game.objects.get(id=game_id)

    cards_to_play = game_object.cards_not_played.order_by("suit", number_order)
    choose_player_action_form = ChoosePlayerForm(players=game_object.players.all())

    if request.method == "POST":
        submit_type = request.POST.get("submit_type")
        if submit_type == "new_round":
            GameRound(game=game_object, chapter=game_chapter, round=game_round + 1).save()
            return redirect(f"/game/{game_id}/{game_chapter}/{game_round + 1}")
        elif submit_type == "new_chapter":
            start_new_chapter(game_object, game_chapter)
            return redirect(f"/game/{game_id}/{game_chapter + 1}/{1}")
        elif submit_type == "new_action":
            choose_player_action_form = ChoosePlayerForm(request.POST, players=game_object.players.all())
            if choose_player_action_form.is_valid():
                return redirect(
                    f"/game/{game_id}/{game_chapter}/{game_round}/{choose_player_action_form.cleaned_data["player"].id}"
                )

    return render(
        request,
        "game.html",
        {
            "name": game_object.name,
            "cards_in_hand": get_cards_in_hand(game_object).items(),
            "cards_played": get_cards_played_by_round(game_object, game_chapter, game_round).items(),
            "rows_images": get_cards_to_play_images(cards_to_play),
            "game_chapter": game_chapter,
            "game_round": game_round,
            "new_player_action": choose_player_action_form,
        },
    )
