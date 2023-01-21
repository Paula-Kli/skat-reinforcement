from observers import Observer


class ModelObserver(Observer):
    def __init__(self):
        self.action_space = None
        self.observation_space = None

    def get_observation(self):
        raise NotImplementedError

    def get_reward(self):
        raise NotImplementedError

    def get_card(self, action: int):
        raise NotImplementedError
