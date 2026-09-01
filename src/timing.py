import customtkinter as ctk
from util import Utility

class Timing():
    def __init__(self, master, TOP_LABEL_POS, top_label_content: ctk.CTkLabel, mode_site):
        self.master = master
        self.TOP_LABEL_POS = TOP_LABEL_POS
        self.top_label_content = top_label_content
        self._mode_site = mode_site
        self.utility = Utility(master)


    def start(self):
        pass

    def _get_mode_site(self):
        return self._mode_site

    def set_top_label_content(self, label: ctk.CTkLabel):
        self.top_label_content = label

    def disable_mode_buttons(self):
        self.utility.disable_all_buttons_from_scope(self._mode_site)

    def enable_mode_buttons(self):
        self.utility.enable_all_buttons_from_scope(self._mode_site)