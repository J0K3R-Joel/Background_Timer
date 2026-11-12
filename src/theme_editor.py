from __future__ import annotations
import colorsys
import math
from tkinter import messagebox
import customtkinter as ctk
from PIL import Image, ImageTk

from constants import Constants


class ColorPicker(ctk.CTkToplevel):
    def __init__(self, master, utility, initial_color, callback):
        super().__init__(master)

        self.title("Pick a color")
        self.geometry("390x535")
        self.utility = utility
        self.resizable(False, False)
        self.transient(master.winfo_toplevel())
        self.grab_set()

        self.callback = callback

        percentage = 0.85
        self.h, self.s, self.v = colorsys.rgb_to_hsv(*(int(initial_color[i:i + 2], 16) / 255 for i in (1, 3, 5)))
        self.v = min(max(self.v, percentage), min(self.v, percentage), key=lambda x: abs(x - percentage))  # Default value is 75% brightness - passt noch nicht, weil bei hellen standard farben ists auf 100% und bei dunklen bei den gewollten 75%

        self._wheel_img = None
        self._brightness_img = None

        ctk.CTkLabel(self, text="Color wheel", font=ctk.CTkFont(size=18, weight="bold")).place(relx=0.5, rely=0.015, anchor="n")

        self.wheel = ctk.CTkCanvas(self, width=280, height=280, highlightthickness=0, bg="#242424")
        self.wheel.place(relx=0.5, rely=0.075, anchor="n")
        self.wheel.bind("<Button-1>", self._wheel_pick)
        self.wheel.bind("<B1-Motion>", self._wheel_pick)

        self._draw_wheel()

        ctk.CTkLabel(self, text="Brightness").place(relx=0.5, rely=0.60, anchor="n")

        self.brightness = ctk.CTkCanvas(self, width=280, height=20, highlightthickness=0, bg="#242424")
        self.brightness.place(relx=0.5, rely=0.645, anchor="n")
        self.brightness.bind("<Button-1>", self._brightness_pick)
        self.brightness.bind("<B1-Motion>", self._brightness_pick)

        self._draw_brightness()

        fields = ctk.CTkFrame(self, fg_color="transparent", width=334, height=78)
        fields.place(relx=0.5, rely=0.70, anchor="n")

        ctk.CTkLabel(fields, text="HEX", width=55, height=28).place(relx=0.015, rely=0.06)

        self.hex_entry = ctk.CTkEntry(fields, width=240, height=28)
        self.hex_entry.place(relx=0.22, rely=0.06)
        self.hex_entry.bind("<Return>", self._hex_changed)

        ctk.CTkLabel(fields, text="RGB", width=55, height=28).place(relx=0.015, rely=0.54)

        self.rgb_entry = ctk.CTkEntry(fields, width=240, height=28, placeholder_text="255, 120, 40")
        self.rgb_entry.place(relx=0.22, rely=0.54)
        self.rgb_entry.bind("<Return>", self._rgb_changed)

        self.preview = ctk.CTkFrame(self, height=28, corner_radius=8)
        self.preview.place(relx=0.09, rely=0.86, relwidth=0.82)

        buttons = ctk.CTkFrame(self, fg_color="transparent")
        buttons.place(relx=0.5, rely=0.93, relwidth=0.72, relheight=0.065, anchor="n")

        ctk.CTkButton(buttons, text="Save", command=self._accept).place(relx=0, rely=0, relwidth=0.46, relheight=1)
        ctk.CTkButton(buttons, text="Cancel", text_color=self.utility.complementaryColor(self.utility.STANDARD_BUTTON_TEXT_COLOR), fg_color=self.utility.complementaryColor(self.utility.STANDARD_FG_COLOR), command=self.destroy).place(relx=0.54, rely=0, relwidth=0.46, relheight=1)

        self.utility.apply_standard_colors(self)
        self._sync()

    def _color(self):
        rgb = colorsys.hsv_to_rgb(self.h, self.s, self.v)
        return "#{:02X}{:02X}{:02X}".format(*(round(c * 255) for c in rgb))

    def _sync(self):
        color = self._color()
        rgb = tuple(int(color[i:i + 2], 16) for i in (1, 3, 5))

        self.hex_entry.delete(0, "end")
        self.hex_entry.insert(0, color)

        self.rgb_entry.delete(0, "end")
        self.rgb_entry.insert(0, ", ".join(map(str, rgb)))

        self.preview.configure(fg_color=color)

        self._draw_marker()
        self._draw_brightness()

    def _draw_wheel(self):
        size = 280
        center = 140
        radius = 132

        image = Image.new("RGB", (size, size), "#242424")
        pixels = image.load()

        for y in range(size):
            for x in range(size):
                dx = x - center
                dy = center - y

                dist = math.hypot(dx, dy)

                if dist <= radius:
                    h = (math.atan2(dy, dx) / (2 * math.pi)) % 1
                    s = dist / radius

                    pixels[x, y] = tuple(round(c * 255) for c in colorsys.hsv_to_rgb(h, s, 1))

        self._wheel_img = ImageTk.PhotoImage(image)
        self.wheel.create_image(0, 0, anchor="nw", image=self._wheel_img)

        self._draw_marker()

    def _draw_marker(self):
        self.wheel.delete("marker")

        angle = self.h * 2 * math.pi
        radius = self.s * 132

        x = 140 + math.cos(angle) * radius
        y = 140 - math.sin(angle) * radius

        self.wheel.create_oval(x - 6, y - 6, x + 6, y + 6, outline="white", width=2, tags="marker")

    def _draw_brightness(self):
        image = Image.new("RGB", (280, 20))
        pixels = image.load()

        for x in range(280):
            v = 1 - x / 279
            rgb = tuple(round(c * 255) for c in colorsys.hsv_to_rgb(self.h, self.s, v))

            for y in range(20):
                pixels[x, y] = rgb

        self._brightness_img = ImageTk.PhotoImage(image)

        self.brightness.delete("all")
        self.brightness.create_image(0, 0, anchor="nw", image=self._brightness_img)

        x = round((1 - self.v) * 279)
        self.brightness.create_line(x, 0, x, 20, fill="white", width=2)

    def _wheel_pick(self, event):
        dx = event.x - 140
        dy = 140 - event.y

        radius = min(132, math.hypot(dx, dy))
        self.s = radius / 132

        if radius:
            self.h = (math.atan2(dy, dx) / (2 * math.pi)) % 1

        self._sync()

    def _brightness_pick(self, event):
        self.v = max(0, min(1, 1 - event.x / 279))
        self._sync()

    def _hex_changed(self, _event=None):
        try:
            value = self.hex_entry.get().strip().lstrip("#")

            if len(value) != 6:
                raise ValueError

            rgb = [int(value[i:i + 2], 16) / 255 for i in (0, 2, 4)]

            self.h, self.s, self.v = colorsys.rgb_to_hsv(*rgb)
            self._sync()

        except ValueError:
            messagebox.showerror("Invalid HEX-Code", "Type something like #FF8800.", parent=self)

    def _rgb_changed(self, _event=None):
        try:
            rgb = [int(part.strip()) for part in self.rgb_entry.get().split(",")]

            if len(rgb) != 3 or any(not 0 <= x <= 255 for x in rgb):
                raise ValueError

            self.h, self.s, self.v = colorsys.rgb_to_hsv(*(x / 255 for x in rgb))
            self._sync()

        except ValueError:
            messagebox.showerror("Invalid RGB-Code", "Format: 255, 120, 40", parent=self)

    def _accept(self):
        self.callback(self._color())
        self.destroy()


class ThemeEditor:
    COLOR_DESCRIPTIONS = {
        "STANDARD_FG_COLOR": "Foreground color",
        "STANDARD_BACKGROUND_COLOR": "Window background color",
        "STANDARD_TEXT_COLOR": "General text color",
        "STANDARD_BUTTON_TEXT_COLOR": "Button text color",
        "STANDARD_MODE_BORDER_COLOR": "Mode border color",
        "STANDARD_WRITABLE_CONTENT_COLOR": "Entry color",
        "STANDARD_ORDERED_FRAME_COLOR": "Color in bordered areas",
        "STANDARD_ORDERED_FRAME_BORDER_COLOR": "Color of the border",
    }

    DEFAULT_CONSTANTS = {
        "STANDARD_FG_COLOR": "#FF0000",
        "STANDARD_HOVER_COLOR": "#FF0000",
        "STANDARD_TEXT_COLOR": "#FFFFFF",
        "STANDARD_BUTTON_TEXT_COLOR": "#FFFFFF",
        "STANDARD_BACKGROUND_COLOR": "#2b2b2b",
        "STANDARD_MODE_BORDER_COLOR": "#474747",
        "STANDARD_WRITABLE_CONTENT_COLOR": "#343638",
        "STANDARD_ORDERED_FRAME_COLOR": "#353535",
        "STANDARD_ORDERED_FRAME_BORDER_COLOR": "#686868",
    }

    def __init__(self, utility, scope, title_label=None, back_callback=None):
        self.utility = utility
        self.constants = Constants(self)
        self.DEFAULT_CONSTANTS["STANDARD_HOVER_COLOR"] = self.utility.adjust_color(self.DEFAULT_CONSTANTS["STANDARD_FG_COLOR"], 50)
        self.constants.change_element("STANDARD_HOVER_COLOR", self.DEFAULT_CONSTANTS["STANDARD_HOVER_COLOR"])

        self.card_height = 100
        self._app = scope
        self.title_label = title_label
        self.back_callback = back_callback
        self.working = self.constants.get_default_dict()
        self.scope = ctk.CTkFrame(scope, fg_color=self.working['STANDARD_BACKGROUND_COLOR'])
        self._images = []


    def _render(self):
        if self.title_label is not None:
            self.title_label.configure(text="Appearance / Colors")

        for child in self._app.winfo_children():
            try:
                child.place_forget()
            except AttributeError:
                child.withdraw()

        for child in self.scope.winfo_children():
            child.destroy()

        self.scope.configure(fg_color=self.working['STANDARD_BACKGROUND_COLOR'])

        self.main_canvas = ctk.CTkCanvas(self.scope, highlightthickness=0, borderwidth=0, bg=self.working["STANDARD_BACKGROUND_COLOR"])
        self.main_canvas.place(relx=0, rely=0, relwidth=0.97, relheight=0.88)

        self.main_scrollbar = ctk.CTkScrollbar(self.scope, bg_color=self.working['STANDARD_BACKGROUND_COLOR'], orientation="vertical", command=self.main_canvas.yview)
        self.main_scrollbar.place(relx=0.97, rely=0, relwidth=0.03, relheight=0.88)

        self.main_canvas.configure(yscrollcommand=self.main_scrollbar.set)

        self.main_content = ctk.CTkFrame(self.main_canvas, fg_color="transparent")
        self.main_window = self.main_canvas.create_window((0, 0), window=self.main_content, anchor="nw", width=max(1, self.main_canvas.winfo_width()))

        self.main_content.bind("<Configure>", self._update_main_scrollregion)
        self.main_canvas.bind("<Configure>", self._resize_main_content)

        color_section = self._section(self.main_content, "Color settings", height=240)

        classes = self._widget_classes()
        columns = 2
        rows = math.ceil(len(classes) / columns)
        cards_height = rows * (self.card_height + 10)

        preview_section_height = cards_height + 70
        preview_section = self._section(self.main_content, "Widget preview", height=preview_section_height)

        self.preview_grid = ctk.CTkFrame(preview_section, fg_color="transparent", height=cards_height)
        self.preview_grid.pack(fill="x", expand=False, padx=8, pady=(48, 10))
        self.preview_grid.pack_propagate(False)
        self._create_widget_previews(classes)

        self._update_layout()

        actions = ctk.CTkFrame(self.scope, fg_color=self.working['STANDARD_BACKGROUND_COLOR'])
        actions.place(relx=0.5, rely=0.95, relwidth=0.98, relheight=0.075, anchor='center')
        fg_color = self.utility.complementaryColor(self.working['STANDARD_FG_COLOR'])

        ctk.CTkButton(actions, text="Cancel", font=('Arial', 18), command=self.cancel, text_color=self.utility.complementaryColor(self.working['STANDARD_BUTTON_TEXT_COLOR']), fg_color=fg_color).place(relx=0, rely=0, relwidth=0.47, relheight=1)
        ctk.CTkButton(actions, text="Save", font=('Arial', 18), command=self.save).place(relx=0.53, rely=0, relwidth=0.47, relheight=1)

        self._bind_mousewheel()
        self.utility.apply_standard_colors(self._app)

        for index, (key, description) in enumerate(self.COLOR_DESCRIPTIONS.items()):
            col = index % 2
            row_index = index // 2

            row = ctk.CTkFrame(color_section, fg_color="transparent")
            row.place(relx=0.015 + col * 0.49, rely=0.17 + row_index * 0.16, relwidth=0.47, relheight=0.14)

            ctk.CTkLabel(row, text=description, text_color=self.working['STANDARD_TEXT_COLOR'], anchor="w").place(relx=0, rely=0, relwidth=0.62, relheight=1)
            ctk.CTkButton(row, text=self.working[key], border_color=self.utility.complementaryColor(self.utility.STANDARD_BACKGROUND_COLOR), text_color=self.working[key], fg_color=self.utility.STANDARD_BACKGROUND_COLOR, hover_color=self.utility.complementaryColor(self.utility.STANDARD_BACKGROUND_COLOR), border_width=2, command=lambda k=key: self._pick(k)).place(relx=0.64, rely=0, relwidth=0.36, relheight=1)

        self.scope.place(relx=0.5, rely=0.5, relwidth=1, relheight=1, anchor='center')


    def _section(self, parent, title, height):
        outer = ctk.CTkFrame(parent, fg_color=self.working["STANDARD_ORDERED_FRAME_COLOR"], border_width=3, border_color=self.working["STANDARD_ORDERED_FRAME_BORDER_COLOR"], corner_radius=10, height=height)
        outer.pack(fill="x", padx=12, pady=(10, 0))
        outer.pack_propagate(False)

        inner = ctk.CTkFrame(outer, fg_color=self.working["STANDARD_BACKGROUND_COLOR"], corner_radius=7)
        inner.pack(fill="both", expand=True, padx=5, pady=5)

        ctk.CTkLabel(inner, text=title, font=ctk.CTkFont(size=18, weight="bold"), height=32).place(relx=0.015, y=7, relwidth=0.97)

        return inner


    def _update_main_scrollregion(self, event=None):
        self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all"))

    def _resize_main_content(self, event):
        self.main_canvas.itemconfigure(self.main_window, width=event.width)


    def _bind_mousewheel(self, event=None):
        self.main_canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.main_canvas.bind_all("<Button-4>", self._on_mousewheel_linux)
        self.main_canvas.bind_all("<Button-5>", self._on_mousewheel_linux)


    def _unbind_mousewheel(self, event=None):
        self.main_canvas.unbind_all("<MouseWheel>")
        self.main_canvas.unbind_all("<Button-4>")
        self.main_canvas.unbind_all("<Button-5>")

    def _on_mousewheel(self, event):
        x = event.x_root - self.main_canvas.winfo_rootx()
        y = event.y_root - self.main_canvas.winfo_rooty()

        if 0 <= x <= self.main_canvas.winfo_width() and 0 <= y <= self.main_canvas.winfo_height():
            if event.delta:
                self.main_canvas.yview_scroll(-1 if event.delta > 0 else 1, "units")

    def _on_mousewheel_linux(self, event):
        x = event.x_root - self.main_canvas.winfo_rootx()
        y = event.y_root - self.main_canvas.winfo_rooty()

        if 0 <= x <= self.main_canvas.winfo_width() and 0 <= y <= self.main_canvas.winfo_height():
            if event.num == 4:
                self.main_canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                self.main_canvas.yview_scroll(1, "units")


    def _widget_classes(self):
        candidates = [
            ctk.CTkLabel,
            ctk.CTkButton,
            ctk.CTkEntry,
            ctk.CTkTextbox,
            ctk.CTkCheckBox,
            ctk.CTkSwitch,
            ctk.CTkSlider,
            ctk.CTkProgressBar,
            ctk.CTkOptionMenu,
            ctk.CTkComboBox,
            ctk.CTkRadioButton,
            ctk.CTkFrame,
        ]

        try:
            widgets = self.utility.get_widgets_from_scope([], self.utility.master.winfo_children())
            for widget in widgets:
                cls = type(widget)
                if cls.__module__.startswith("customtkinter") and cls not in candidates:
                    candidates.append(cls)
        except Exception:
            pass

        if ctk.CTkCanvas in candidates:  # canvas should (until now) never be shown)
            candidates.remove(ctk.CTkCanvas)

        return candidates


    def _create_widget_previews(self, classes=None):
        if classes is None:
            classes = self._widget_classes()

        columns = 2
        rows = math.ceil(len(classes) / columns)

        for index, cls in enumerate(classes):
            col = index % columns
            row_index = index // columns
            card = ctk.CTkFrame(self.preview_grid, height=self.card_height, border_width=3, fg_color=self.working["STANDARD_ORDERED_FRAME_COLOR"], border_color=self.working["STANDARD_ORDERED_FRAME_BORDER_COLOR"], corner_radius=9)
            card.place(relx=col * 0.50 + 0.005, y=row_index * (self.card_height + 10), relwidth=0.49)

            inner = ctk.CTkFrame(card, fg_color=self.working["STANDARD_ORDERED_FRAME_COLOR"], corner_radius=6)
            inner.place(relx=0.02, rely=0.05, relwidth=0.96, relheight=0.90)

            ctk.CTkLabel(inner, text=cls.__name__, text_color=self.working["STANDARD_TEXT_COLOR"], font=ctk.CTkFont(weight="bold")).place(relx=0.025, rely=0.04, relwidth=0.95, relheight=0.25)

            widget = self._make_sample(cls, inner)
            widget.place(relx=0.025, rely=0.38, relwidth=0.94)


    def _make_sample(self, cls, parent):
        try:
            if cls is ctk.CTkLabel:
                return ctk.CTkLabel(parent, text="Example text")

            if cls is ctk.CTkButton:
                return ctk.CTkButton(parent, text="Example text")

            if cls is ctk.CTkEntry:
                widget = ctk.CTkEntry(parent, placeholder_text="Example text")
                widget.insert(0, "Example text")
                return widget

            if cls is ctk.CTkTextbox:
                widget = ctk.CTkTextbox(parent)
                widget.insert("1.0", "Example text")
                return widget

            if cls is ctk.CTkCheckBox:
                return ctk.CTkCheckBox(parent, text="Example text")

            if cls is ctk.CTkSwitch:
                return ctk.CTkSwitch(parent, text="Example text")

            if cls is ctk.CTkSlider:
                return ctk.CTkSlider(parent)

            if cls is ctk.CTkProgressBar:
                widget = ctk.CTkProgressBar(parent)
                widget.set(0.65)
                return widget

            if cls is ctk.CTkOptionMenu:
                return ctk.CTkOptionMenu(parent, values=["Example text", "Option 2"])

            if cls is ctk.CTkComboBox:
                return ctk.CTkComboBox(parent, values=["Example text", "Option 2"])

            if cls is ctk.CTkRadioButton:
                return ctk.CTkRadioButton(parent, text="Example text")

            if cls is ctk.CTkFrame:
                frame = ctk.CTkFrame(parent, fg_color=self.working['STANDARD_BACKGROUND_COLOR'], border_width=2, border_color=self.working["STANDARD_ORDERED_FRAME_BORDER_COLOR"])
                ctk.CTkLabel(frame, text="Example text").place(relx=0.5, rely=0.5, anchor="center")
                return frame

            if cls is ctk.CTkScrollbar:
                parent.update_idletasks()
                return ctk.CTkScrollbar(parent, width=parent.winfo_width()//4, height=parent.winfo_height()//4)

            # if cls is ctk.CTkCanvas:
            #     return ctk.CTkCanvas(parent)

            return ctk.CTkLabel(parent, text=f"{cls.__name__}: Preview not available")

        except Exception as exc:
            return ctk.CTkLabel(parent, text=f"{cls.__name__}: {exc}")


    def _pick(self, key):
        ColorPicker(self.scope.winfo_toplevel(), self.utility, self.working[key], lambda color: self._set_color(key, color))

    def _update_layout(self):
        self.main_content.update_idletasks()
        self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all"))

    def _set_color(self, key, color):
        if getattr(self.utility, key):
            setattr(self.utility, key, color)
            print(key, color)
            self.utility.set_hover_color()
        self.working[key] = color
        self._render()


    def get_standard_colors(self):
        return self.constants.get_default_dict()


    def save(self):
        self.utility.set_theme_colors(self.working, apply=True)
        if self.back_callback:
            self.back_callback()
            self.__clear_editor()

    def cancel(self):
        self.working = self.constants.get_default_dict()

        if self.back_callback:
            self.back_callback()
            self.__clear_editor()
        else:
            self._render()

    def __clear_editor(self):
        self._unbind_mousewheel()
        self.utility.clear_visible_widgets(True, scope=self.scope)
        self.scope.destroy()

    # @TODO fix save / cancel button