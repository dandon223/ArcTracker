import uuid
from typing import Any, Union

from django.contrib.auth.forms import UserCreationForm
from django.http import HttpRequest, HttpResponse, HttpResponseNotFound
from django.shortcuts import redirect, render

from .forms import CardPlayedInRoundForm, ChoosePlayerForm, GameForm, NumberOfCardsAddedForm, PlayerCardForm, PlayerForm
from .models import (
    Game,
    GameRound,
    Player,
    PlayerHand,
)
from .views_logic import (
    assign_cards,
    cards_number_order,
    create_initial_round,
    deal_initial_hands,
    get_cards_played_by_round,
    get_cards_to_images_by_hand,
    get_cards_to_images_by_suit,
    get_cards_to_play,
    get_cards_to_retrieve,
    get_cards_to_reveal,
    handle_card_played,
    handle_card_retrieved,
    handle_number_of_cards_added,
    handle_reveal_card,
    handle_unreveal_card,
    start_new_chapter,
)

# Create your views here.


def register(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        user_creation_form: Any = UserCreationForm(request.POST)
        if user_creation_form.is_valid():
            user_creation_form.save()
            return redirect("/")
    else:
        user_creation_form = UserCreationForm()
    return render(request, "register.html", {"user_creation_form": user_creation_form})


def menu(request: HttpRequest) -> HttpResponse:
    return render(request, "menu.html")


def user_menu(request: HttpRequest) -> HttpResponse:
    return render(request, "user_menu.html")


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
            return redirect("/new_player/")
    else:
        form = PlayerForm()
    return render(request, "new_player.html", {"form": form})


def players(request: HttpRequest) -> HttpResponse:
    return render(request, "view.html", {"name": "players", "models": Player.objects.all()})


def games(request: HttpRequest) -> HttpResponse:
    return render(request, "view.html", {"name": "games", "models": Game.objects.all()})


def new_action(  # pylint: disable=too-many-return-statements
    request: HttpRequest, game_id: uuid.UUID, chapter_number: int, round_number: int, player_id: uuid.UUID
) -> Union[HttpResponse, HttpResponseNotFound]:
    if not Game.objects.filter(id=game_id).exists():
        return HttpResponseNotFound(f"game with id {game_id} not found")
    game = Game.objects.filter(id=game_id).get()
    player = Player.objects.filter(id=player_id).get()
    player_hand = PlayerHand.objects.get(player=player, game=game)

    card_played_in_round_form = CardPlayedInRoundForm(cards=get_cards_to_play(game, player))
    card_retrived_in_round_form = PlayerCardForm(cards=get_cards_to_retrieve(game, chapter_number, round_number))
    number_of_cards_added_form = NumberOfCardsAddedForm()
    reveal_card_form = PlayerCardForm(cards=get_cards_to_reveal(game))
    unreveal_card_form = PlayerCardForm(cards=player_hand.cards.all())

    if request.method == "POST":
        submit_type = request.POST.get("submit_type")
        if submit_type == "card_played":
            card_played_in_round_form = CardPlayedInRoundForm(request.POST, cards=get_cards_to_play(game, player))
            if card_played_in_round_form.is_valid():
                handle_card_played(card_played_in_round_form, game, player, chapter_number, round_number)
                return redirect(f"/game/{game.id}/{chapter_number}/{round_number}")
        elif submit_type == "card_retrieved":
            card_retrived_in_round_form = PlayerCardForm(
                request.POST, cards=get_cards_to_retrieve(game, chapter_number, round_number)
            )
            if card_retrived_in_round_form.is_valid():
                handle_card_retrieved(card_retrived_in_round_form, game, player)
                return redirect(f"/game/{game_id}/{chapter_number}/{round_number}")
        elif submit_type == "number_of_cards_added":
            number_of_cards_added_form = NumberOfCardsAddedForm(request.POST)
            if number_of_cards_added_form.is_valid():
                handle_number_of_cards_added(number_of_cards_added_form, player)
                return redirect(f"/game/{game_id}/{chapter_number}/{round_number}")
        elif submit_type == "reveal_card":
            reveal_card_form = PlayerCardForm(request.POST, cards=get_cards_to_reveal(game))
            if reveal_card_form.is_valid():
                handle_reveal_card(reveal_card_form, game, player)
                return redirect(f"/game/{game_id}/{chapter_number}/{round_number}")
        elif submit_type == "unreveal_card":
            unreveal_card_form = PlayerCardForm(request.POST, cards=player_hand.cards.all())
            if unreveal_card_form.is_valid():
                handle_unreveal_card(unreveal_card_form, game, player)
                return redirect(f"/game/{game_id}/{chapter_number}/{round_number}")

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


def current_game(
    request: HttpRequest, game_id: uuid.UUID, chapter_number: int, round_number: int
) -> Union[HttpResponse, HttpResponseNotFound]:
    if not Game.objects.filter(id=game_id).exists():
        return HttpResponseNotFound(f"game with id {game_id} not found")

    game_object = Game.objects.get(id=game_id)
    choose_player_form = ChoosePlayerForm(players=game_object.players.all())

    if request.method == "POST":
        submit_type = request.POST.get("submit_type")
        if submit_type == "new_round":
            GameRound(game=game_object, chapter=chapter_number, round=round_number + 1).save()
            return redirect(f"/game/{game_id}/{chapter_number}/{round_number + 1}")
        if submit_type == "new_chapter":
            start_new_chapter(game_object, chapter_number)
            return redirect(f"/game/{game_id}/{chapter_number + 1}/{1}")
        if submit_type == "new_action":
            choose_player_form = ChoosePlayerForm(request.POST, players=game_object.players.all())
            if choose_player_form.is_valid():
                return redirect(
                    f"/game/{game_id}/{chapter_number}/{round_number}/{choose_player_form.cleaned_data['player'].id}"
                )

    return render(
        request,
        "game.html",
        {
            "name": game_object.name,
            "cards_by_hand": get_cards_to_images_by_hand(game_object).items(),
            "cards_played": get_cards_played_by_round(game_object, chapter_number, round_number).items(),
            "cards_by_suit": get_cards_to_images_by_suit(
                game_object.cards_not_played.order_by("suit", cards_number_order)
            ).values(),
            "chapter_number": chapter_number,
            "round_number": round_number,
            "new_player_action": choose_player_form,
        },
    )
