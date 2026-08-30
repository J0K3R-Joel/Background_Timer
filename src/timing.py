import customtkinter as ctk


class Timing():
    def __init__(self, master, TOP_LABEL_POS, top_label_content: ctk.CTkLabel, *mode_buttons):
        self.master = master
        self.TOP_LABEL_POS = TOP_LABEL_POS
        self.top_label_content = top_label_content
        self.mode_buttons = mode_buttons


    def start(self):
        pass

    def get_mode_buttons(self):
        return self.mode_buttons

    def set_top_label_content(self, label: ctk.CTkLabel):
        self.top_label_content = label