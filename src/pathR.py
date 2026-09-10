import os
from pathlib import Path

class PathR():
    def __init__(self, mode: str = None):
        # HINT: paths must contain '\\' or '/' to automatically get created
        self.mode = mode
        self.__base_path = os.path.expanduser('~')
        self.__base_path_timer = self.__base_path + '\\Background Timer'
        os.makedirs(self.__base_path_timer, exist_ok=True)

        self.__base_sound_path = self.__base_path_timer + '\\Sounds'
        self.__base_config_path = self.__base_path_timer + '\\Configs'

        # ============ CONFIGS ============
        self.__create_class_config_paths()
        self.__create_var_paths()


    def __create_var_paths(self):
        class_variables = vars(self)
        for cv in class_variables:
            value = getattr(self, cv)

            if isinstance(value, str) and (value.find('\\') != -1 or value.find('/') != -1):
                char_double = value.find('\\')
                path_sep = '\\' if char_double != -1 else '/'
                last_index = value.rindex(path_sep)

                if value[last_index:].find('.') == -1:  # if not a file
                    os.makedirs(value, exist_ok=True)

    def __create_class_config_paths(self):
        if self.mode:
            conf_file = self.__base_config_path + '\\' + self.mode + '.conf'
            setattr(self, f'{self.mode}_conf_file', conf_file)


    def __get_base_path(self):
        return self.__base_path

    def __get_base_path_timer(self):
        return self.__base_path_timer

    def __get_sound_path(self):
        return self.__base_sound_path

    def get_config_path(self):
        return self.__base_config_path

    def get_config_file_path(self):
        return getattr(self, f'{self.mode}_conf_file', None)

    def get_directories_in_path(self, path_to_directory: str):
        return next(os.walk(path_to_directory))[1]

    def get_files_in_path(self, path_to_directory: str):
        return next(os.walk(path_to_directory), (None, None, []))[2]


if __name__ == '__main__':
    p = PathR()