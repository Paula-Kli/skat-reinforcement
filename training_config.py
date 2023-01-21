import time
from typing import Union, Type, Optional

from stable_baselines3.common.base_class import BaseAlgorithm
from stable_baselines3.common.policies import BasePolicy

from observers import ModelObserver
from players.trump_strategies import TrumpStrategy


class TrainingConfig:
    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name: Optional[str]):
        self._name = name or f"training_{time.strftime('%Y%m%d-%H%M%S')}"

    def __init__(
        self,
        algorithm: Type[BaseAlgorithm],
        policy: Union[str, BasePolicy],
        policy_kwargs: dict,
        observer: Type[ModelObserver],
        observer_kwargs: dict,
        trump_strategy: Type[TrumpStrategy],
        name: Optional[str] = None
    ):
        self.algorithm = algorithm
        self.policy = policy
        self.policy_kwargs = policy_kwargs
        self.observer = observer
        self.observer_kwargs = observer_kwargs
        self.trump_strategy = trump_strategy
        self.name = name

    def __str__(self):
        return self.name
