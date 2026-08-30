import time
import tkinter as tk
import math


class CircularProgressBar(tk.Canvas):
    def __init__(
        self,
        master,
        size=200,
        max_value=100,
        value=0,
        thickness=20,
        progress_color="#4CAF50",
        background_color="#333333",
        text_color="#FFFFFF",
        font=("Arial", 24),
        **kwargs,
    ):
        super().__init__(master, width=size, height=size, highlightthickness=0, bg=background_color, **kwargs,)

        self.size = size
        self.max_value = max_value
        self.value = value
        self.thickness = thickness

        self.progress_color = progress_color
        self.background_color = background_color
        self.text_color = text_color
        self.font = font

        self._text = None

        self._draw()

    def set_value(self, value):
        value = max(0, min(value, self.max_value))
        self.after(0, lambda: self._set_value(value))

    def set_max_value(self, max_value):
        if max_value <= 0:
            raise ValueError("max_value has to be bigger than 0")

        self.after(0, lambda: self._set_max_value(max_value))

    def set_text(self, text):
        self.after(
            0,
            lambda: self._set_text(text)
        )

    def set_colors(self, progress=None, background=None, text=None):
        self.after(0, lambda: self._set_colors(progress, background, text))

    def set_thickness(self, thickness):
        self.after(
            0,
            lambda: self._set_thickness(thickness)
        )

    def reset(self):
        self.set_value(0)


    def _set_value(self, value):
        self.value = value
        self._draw()

    def _set_max_value(self, max_value):
        self.max_value = max_value
        self.value = min(self.value, max_value)
        self._draw()

    def _set_text(self, text):
        self._text = text
        self._draw()

    def _set_colors(self, progress, background, text):
        if progress is not None:
            self.progress_color = progress

        if background is not None:
            self.background_color = background

        if text is not None:
            self.text_color = text

        self.configure(bg=self.background_color)

        self._draw()

    def _set_thickness(self, thickness):
        self.thickness = thickness
        self._draw()

    def _draw(self):
        self.delete("all")

        padding = self.thickness / 2

        x1 = padding
        y1 = padding
        x2 = self.size - padding
        y2 = self.size - padding

        percentage = self.value / self.max_value

        self.create_arc(
            x1,
            y1,
            x2,
            y2,
            start=90,
            extent=-359.999,
            style=tk.ARC,
            width=self.thickness,
            outline=self.background_color,
        )
        if percentage <= 0.005:
            self.create_oval(
                x1,
                y1,
                x2,
                y2,
                width=0,
                outline=self.background_color
            )

        elif percentage >= 1:
            self.create_oval(
                x1,
                y1,
                x2,
                y2,
                width=self.thickness,
                outline=self.progress_color,
            )
        elif percentage > 0.005:
            self.create_arc(
                x1,
                y1,
                x2,
                y2,
                start=90,
                extent=-360 * percentage,
                style=tk.ARC,
                width=self.thickness,
                outline=self.progress_color,
            )

        if self._text is None:
            text = f"{percentage * 100:.0f}%"
        else:
            text = str(self._text)

        self.create_text(
            self.size / 2,
            self.size / 2,
            text=text,
            fill=self.text_color,
            font=self.font,
        )


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Circular Progress Bar")

    progress = CircularProgressBar(
        root,
        size=250,
        max_value=100,
        thickness=25,
        progress_color="#4CAF50",
        background_color="#333333",
        text_color="#FFFFFF",
        font=("Arial", 24),
    )
    progress.pack(padx=30, pady=30)

    def start(i=0):
        if i >= 100:
            return

        progress.set_value(i)

        root.after(300, lambda: start(i + 1))

    start_b = tk.Button(root, text="Start", command=start)
    start_b.pack(padx=40, pady=10)

    root.mainloop()

