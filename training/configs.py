from typing import Optional

from sb3_contrib import MaskablePPO

from training_config import TrainingConfig
from observers import MarkovObserverV1, DrunkenRainerObserverV1, DrunkenRainerObserverV2, CountingObserver
from players.trump_strategies import SuitAmountTrumpStrategy, SuitAmountTrumpStrategyBetterSkat

configs = {
    "markov_suit_amount_small": TrainingConfig(
        MaskablePPO,
        "MultiInputPolicy",
        {},  # default net_arch: [dict(pi=[64, 64], vf=[64, 64])]
        MarkovObserverV1,
        dict(positional_trump=False, win_reward=False),
        SuitAmountTrumpStrategy
    )
}


def names():
    return configs.keys()


def get(config_name: str) -> Optional[TrainingConfig]:
    config = configs[config_name]
    config.name = config_name
    return config
