from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpRequest, HttpResponseNotFound
from django.views import View
from .forms import GameForm
from .models import Game
# Create your views here.

def menu(request):
    return render(request, 'menu.html')

def new_game(request: HttpRequest):
    form = GameForm()

    if request.method == 'POST':
        form = GameForm(request.POST)
        if form.is_valid():
            game = form.save()
            return redirect(f'/game/{game.id}/')

    return render(request, "new_game.html", {'form' : form})

def game(request, id):
    if Game.objects.filter(id=id).exists():
        game = Game.objects.filter(id=id).get()
        return render(request, 'game.html', {'name': game})
    else:
        return HttpResponseNotFound(f"game with id {id} not found")
    