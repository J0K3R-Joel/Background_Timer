import customtkinter as ctk


class Timing():
    def __init__(self, master, TOP_LABEL_POS, top_label_content: ctk.CTkLabel):
        self.master = master
        self.TOP_LABEL_POS = TOP_LABEL_POS
        self.top_label_content = top_label_content


    def start(self):
        pass

    def set_top_label_content(self, label: ctk.CTkLabel):
        self.top_label_content = label