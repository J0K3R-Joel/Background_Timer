import json
from fileR import FileR
from pathR import PathR
from messageR import MessageR
from timing import Timing

class Constants():
    def __init__(self, class_: Timing):
        self.class_ = class_
        self.msg = MessageR(self.__class__.__name__)
        self.path_man = PathR(self.class_.__class__.__name__)
        self.file_man = FileR(self.path_man.get_config_path())

        self._default_dict = {}
        self.__handle_conf_file()


    def __handle_conf_file(self):
        conf_file = self.path_man.get_config_file_path()
        if not self.file_man.exists(conf_file):
            self.file_man.writer(conf_file, 'w', json.dumps(self.class_.DEFAULT_CONSTANTS, indent=4))

        text = self.file_man.reader(conf_file)

        try:
            self._default_dict = json.loads(text)
        except json.decoder.JSONDecodeError as e:  # json file has an error, so reset the file to the default values
            self.msg.error(str(e))
            self._default_dict = self.class_.DEFAULT_CONSTANTS
            self.file_man.writer(conf_file, 'w', json.dumps(self.class_.DEFAULT_CONSTANTS))

    def get_default_dict(self):
        return self._default_dict

    def change_element(self, key: str, value, create_key: bool = False):
        if not create_key and not key in self._default_dict.keys():
            raise KeyError('Element with key "', key, '" does not exist')

        self._default_dict[key] = value
        self.file_man.writer(self.path_man.get_config_file_path(), 'w', json.dumps(self._default_dict, indent=4))