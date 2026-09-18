import customtkinter as ctk


class FixedTextbox(ctk.CTkTextbox):
    def __init__(self, master, width=300, height=100, text="", **kwargs):
        super().__init__(
            master,
            width=width,
            height=height,
            wrap="word",
            **kwargs
        )

        if text:
            self.insert("1.0", text)

        self.bind("<KeyPress>", self.check_input)
        self.bind("<Return>", self.block_return)

    def check_input(self, event):
        if event.keysym in (
            "BackSpace",
            "Delete",
            "Left",
            "Right",
            "Up",
            "Down",
            "Home",
            "End",
            "Shift_L",
            "Shift_R",
            "Control_L",
            "Control_R",
            "Alt_L",
            "Alt_R"
        ):
            return

        if event.char:
            self.after(1, self.check_overflow)

    def block_return(self, event):
        self.after(1, self.check_overflow)

    def check_overflow(self):
        bbox = self.bbox("end-1c")

        if bbox:
            x, y, width, height = bbox
            textbox_height = self.winfo_height()

            if y + height > textbox_height:
                self.delete("end-2c", "end-1c")