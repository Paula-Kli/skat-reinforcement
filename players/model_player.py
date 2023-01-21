import numpy as np

from card import Card
from training import configs
from .player import Player


class ModelPlayer(Player):
    def __init__(self, path: str, device="auto", *args, **kwargs):
        """
        Creates a player from a trained model
        :param path: The path to the model, relative to the root folder. This also determines the config.
        """
        super().__init__(*args, **kwargs)
        try:
            if "self_train" in path:
                config_name, env_settings, _, filename = path.split("/")[-4:]
            else:
                config_name, env_settings, filename = path.split("/")[-3:]
        except ValueError:
            raise ValueError(f"invalid path: {path}")
        config = configs.get(config_name)
        self.model = config.algorithm.load(path, policy_kwargs=config.policy_kwargs, device=device)
        self.name = self.name or f"{config_name}_{env_settings}_{filename.replace('.zip', '')}"
        self.model_observer = config.observer(**config.observer_kwargs)
        self.observers.append(self.model_observer)
        self.trump_strategy = config.trump_strategy()
        self.kwargs.update(path=path)

    def _action_masks(self, valid_cards: list[Card]):
        return np.array([self.model_observer.get_card(action) in valid_cards for action in range(32)])

    def next_card(self, hand: list[Card], valid_cards: list[Card]):
        action, _ = self.model.predict(
            self.model_observer.get_observation(), deterministic=True, action_masks=self._action_masks(valid_cards))
        return self.model_observer.get_card(int(action))
