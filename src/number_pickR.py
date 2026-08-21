import customtkinter as ctk

class NumberPicker(ctk.CTkFrame):
    def __init__(self, master, min_value, max_value, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)

        self.min_value = min_value
        self.max_value = max_value
        self.value = min_value
        self.blocked = False

        self.up_button = ctk.CTkButton(
            self,
            text="▲",
            width=60,
            height=30,
            command=self.increase
        )
        self.up_button.pack()

        self.label = ctk.CTkLabel(
            self,
            text=f"{self.value:02}",
            font=("Arial", 28),
            width=60
        )
        self.label.pack(pady=5)

        self.down_button = ctk.CTkButton(
            self,
            text="▼",
            width=60,
            height=30,
            command=self.decrease
        )
        self.down_button.pack()

        self.bind("<MouseWheel>", self.mousewheel)
        self.label.bind("<MouseWheel>", self.mousewheel)
        self.label.bind("<Double-Button-1>", self.double_click)
        self.label.bind("<Triple-Button-1>", self.triple_click)

    def increase(self):
        if self.value < self.max_value:
            self.value += 1
            self.update_label()

    def decrease(self):
        if self.value > self.min_value:
            self.value -= 1
            self.update_label()

    def set(self, value: int):
        if self.max_value >= value >= self.min_value:
            self.value = value
            self.update_label()


    def update_label(self):
        self.label.configure(text=f"{self.value:02}")

    def mousewheel(self, event):
        if not self.blocked:
            if event.delta > 0:
                self.increase()
            else:
                self.decrease()

    def double_click(self, event):
        if not self.blocked:
            self.value = self.min_value
            self.update_label()

    def triple_click(self, event):
        if not self.blocked:
            self.value = self.max_value
            self.update_label()

    def block_mouse(self):
        self.blocked = True

    def unblock_mouse(self):
        self.blocked = False

    def get(self):
        return self.value

    def get_max(self):
        return self.max_value

    def get_min(self):
        return self.min_value


