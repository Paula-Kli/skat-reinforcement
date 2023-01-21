from os import path

from .player import Player
from .human_player import HumanPlayer
from .model_player import ModelPlayer
from .multi_model_player import MultiModelPlayer
from .random_player import RandomPlayer
from .simple_player_v1 import SimplePlayerV1
from .advanced_player import AdvancedPlayer


def get_player(name_or_path: str, **kwargs):
    player_class = globals().get(name_or_path)
    if player_class:
        return player_class(**kwargs)
    elif path.isdir(name_or_path):
        return MultiModelPlayer(name_or_path, **kwargs)
    else:
        return ModelPlayer(name_or_path, **kwargs)
