import uuid
from typing import Any, Union

from django.contrib.auth import login, logout
from django.contrib.auth import models as auth_models
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.http import HttpRequest, HttpResponse, HttpResponseNotFound
from django.shortcuts import redirect, render

from .forms import CardPlayedInRoundForm, ChoosePlayerForm, GameForm, NumberOfCardsAddedForm, PlayerCardForm, PlayerForm
from .models import CardPlayedInRound, Game, GameRound, Player, PlayerHand
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


def register_view(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        user_creation_form: Any = UserCreationForm(request.POST)
        if user_creation_form.is_valid():
            login(request, user_creation_form.save())
            return redirect("/user_menu")
    else:
        user_creation_form = UserCreationForm()
    return render(request, "register.html", {"user_creation_form": user_creation_form})


def login_view(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        authentication_form = AuthenticationForm(data=request.POST)
        if authentication_form.is_valid():
            login(request, authentication_form.get_user())
            return redirect("/user_menu")
    else:
        authentication_form = AuthenticationForm()
    return render(request, "login.html", {"authentication_form": authentication_form})


@login_required(login_url="/login/")
def logout_view(request: HttpRequest) -> HttpResponse:
    logout(request)
    return redirect("/")


def menu_view(request: HttpRequest) -> HttpResponse:
    return render(request, "menu.html")


@login_required(login_url="/login/")
def user_menu_view(request: HttpRequest) -> HttpResponse:
    return render(request, "user_menu.html", {"user_name": request.user.username})


@login_required(login_url="/login/")
def new_game_view(request: HttpRequest) -> HttpResponse:
    assert isinstance(request.user, auth_models.User)
    if request.method == "POST":
        game_form = GameForm(request.POST, user=request.user)
        if game_form.is_valid():
            game = game_form.save(commit=False)
            game.user = request.user
            game.save()
            game_form.save_m2m()
            assign_cards(game)
            create_initial_round(game)
            deal_initial_hands(game)
            return redirect(f"/game/{game.id}/1/1")
    else:
        game_form = GameForm(user=request.user)

    return render(request, "new_game.html", {"game_form": game_form})


@login_required(login_url="/login/")
def new_player_view(request: HttpRequest) -> Union[HttpResponse, HttpResponseNotFound]:
    assert isinstance(request.user, auth_models.User)
    if request.method == "POST":
        form = PlayerForm(request.POST)
        if form.is_valid():
            if Player.objects.filter(nick=form.cleaned_data["nick"], user=request.user).exists():
                return HttpResponseNotFound(f"player with nick {form.cleaned_data['nick']} already exists")
            player = form.save(commit=False)
            player.user = request.user
            player.save()
            return redirect("/new_player/")
    else:
        form = PlayerForm()
    return render(request, "new_player.html", {"form": form})


@login_required(login_url="/login/")
def players_view(request: HttpRequest) -> HttpResponse:
    assert isinstance(request.user, auth_models.User)
    return render(request, "view.html", {"name": "players", "models": Player.objects.filter(user=request.user)})


@login_required(login_url="/login/")
def games_view(request: HttpRequest) -> HttpResponse:
    assert isinstance(request.user, auth_models.User)
    return render(request, "view.html", {"name": "games", "models": Game.objects.filter(user=request.user)})


@login_required(login_url="/login/")
def new_action_view(  # pylint: disable=too-many-return-statements, too-many-branches
    request: HttpRequest, game_id: uuid.UUID, chapter_number: int, round_number: int, player_id: uuid.UUID
) -> Union[HttpResponse, HttpResponseNotFound]:
    assert isinstance(request.user, auth_models.User)
    if not Game.objects.filter(id=game_id, user=request.user).exists():
        return HttpResponseNotFound(f"game with id {game_id} not found")
    if not Player.objects.filter(id=player_id, user=request.user).exists():
        return HttpResponseNotFound(f"player with id {player_id} not found")
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


@login_required(login_url="/login/")
def current_game_view(  # pylint: disable=too-many-return-statements
    request: HttpRequest, game_id: uuid.UUID, chapter_number: int, round_number: int
) -> Union[HttpResponse, HttpResponseNotFound]:
    assert isinstance(request.user, auth_models.User)
    if not Game.objects.filter(id=game_id, user=request.user).exists():
        return HttpResponseNotFound(f"game with id {game_id} not found")

    game_object = Game.objects.get(id=game_id)
    choose_player_form = ChoosePlayerForm(players=game_object.players.all())
    number_of_players = len(game_object.players.all())
    game_round = GameRound.objects.get(game=game_object, chapter=chapter_number, round=round_number)
    cards_played_in_rounds = len(CardPlayedInRound.objects.filter(game_round=game_round))
    if request.method == "POST":
        submit_type = request.POST.get("submit_type")
        if submit_type == "new_round":
            if cards_played_in_rounds < number_of_players:
                return HttpResponseNotFound("not all players played in this round")
            GameRound(game=game_object, chapter=chapter_number, round=round_number + 1).save()
            return redirect(f"/game/{game_id}/{chapter_number}/{round_number + 1}")
        if submit_type == "new_chapter":
            if cards_played_in_rounds < number_of_players:
                return HttpResponseNotFound("not all players played in this round")
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
