import customtkinter as ctk
from timing import Timing

class Alarm(Timing):
    def __init__(self, master, TOP_LABEL_POS, top_label_content):
        Timing.__init__(self, master, TOP_LABEL_POS, top_label_content)

    def start(self):
        pass