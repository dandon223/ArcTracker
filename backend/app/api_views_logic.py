from .models import Game
from .views_logic import assign_cards, create_initial_round, deal_initial_hands


def prepare_new_game(game: Game) -> None:
    assign_cards(game)
    create_initial_round(game)
    deal_initial_hands(game)
