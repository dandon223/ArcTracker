import uuid
from typing import Union

from django.http import HttpRequest, HttpResponse, HttpResponseNotFound
from django.shortcuts import redirect, render

from .forms import GameForm, PlayerForm
from .models import Game, Player

# Create your views here.


def menu(request: HttpRequest) -> HttpResponse:
    return render(request, "menu.html")


def new_game(request: HttpRequest) -> HttpResponse:
    form = GameForm()

    if request.method == "POST":
        form = GameForm(request.POST)
        if form.is_valid():
            game = form.save()
            return redirect(f"/game/{game.id}/")

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

def game(request: HttpRequest, id: uuid.UUID) -> Union[HttpResponse, HttpResponseNotFound]:
    if Game.objects.filter(id=id).exists():
        game_object = Game.objects.filter(id=id).get()
        return render(request, "game.html", {"name": game_object})
    return HttpResponseNotFound(f"game with id {id} not found")
