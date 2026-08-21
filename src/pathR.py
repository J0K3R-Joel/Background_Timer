import os

class PathR():
    def __init__(self):
        self.__base_path = os.path.expanduser('~')
        self.base_path_timer = self.__base_path + '\\Background Timer'
        os.makedirs(self.base_path_timer, exist_ok=True)

        self.sound_path = self.base_path_timer + '\\Sounds'
        self.config_path = self.base_path_timer + '\\Configs'

    def __get_base_path(self):
        return self.__base_path

    def get_base_path_timer(self):
        return self.base_path_timer

    def get_sound_path(self):
        return self.sound_path

    def get_config_path(self):
        return self.config_path