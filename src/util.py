import time
import threading

import _tkinter
import customtkinter as ctk
import builtins
import colorsys
from messagR import MessageR
from ExpandingEntry import EntryExpanding


class Utility():
    def __init__(self, master):
        self.master = master
        self.STANDARD_FG_COLOR = '#FF0000'
        self.STANDARD_HOVER_COLOR = self.adjust_color(self.STANDARD_FG_COLOR, 50)
        self.STANDARD_TEXT_COLOR = '#FFFFFF'
        self.STANDARD_BUTTON_TEXT_COLOR = '#FFFFFF'
        self.STANDARD_BACKGROUND_COLOR = '#2b2b2b'
        self.STANDARD_MODE_BORDER_COLOR = '#474747'
        self.STANDARD_WRITABLE_CONTENT_COLOR = '#343638'
        self.STANDARD_ORDERED_FRAME_COLOR = '#353535'
        self.STANDARD_ORDERED_FRAME_BORDER_COLOR = '#686868'
        self.ENTRY_WIDGETS = {}
        self.msg = MessageR('Utility')


    def show_warning_text(self, text: str, seconds: float | int,  scope = None) -> None:
        scope = self.master if not scope else scope

        def show_text(scope, text, seconds):
            warning_label = ctk.CTkLabel(scope, text='', text_color='black', fg_color='yellow')
            warning_label.configure(text=text, font=('Arial', 20), text_color='black')
            warning_label.place(relx=0.5, rely=0.5, anchor='center')
            warning_label.lift()
            scope.after(seconds * 1000, lambda: hide_text(warning_label))

        def hide_text(label):
            try:
                label.place_forget()
            except _tkinter.TclError:
                pass

        threading.Thread(target=show_text, args=(scope, text, seconds,), daemon=True).start()


    def hide_all_frames(self, scope = None):
        scope = self.master if not scope else scope
        widgets = self.get_widgets_from_scope([], scope.winfo_children())
        for widget in widgets:
            if isinstance(widget, ctk.CTkFrame):
                if not isinstance(widget.cget('fg_color'), str) or widget.cget('fg_color')[0] != '#':
                    widget.configure(fg_color='transparent')


    def set_default_fg_color(self, scope = None):
        scope = self.master if not scope else scope
        widgets = self.get_widgets_from_scope([], scope.winfo_children())
        widget_types_to_change = [
            ctk.CTkButton,
            ctk.CTkCheckBox
        ]

        for widget in widgets:
            for widget_type in widget_types_to_change:
                if isinstance(widget, widget_type):
                    if widget.cget('fg_color') != self.complementaryColor(self.STANDARD_FG_COLOR):
                        widget.configure(fg_color=self.STANDARD_FG_COLOR)
            if isinstance(widget, ctk.CTkSlider):
                widget.configure(button_color=self.STANDARD_FG_COLOR, progress_color=self.STANDARD_FG_COLOR)
            elif isinstance(widget, ctk.CTkScrollbar):
                widget.configure(button_color=self.STANDARD_FG_COLOR)


    def set_default_hover_color(self, scope = None):
        scope = self.master if not scope else scope
        widgets = self.get_widgets_from_scope([], scope.winfo_children())
        hoverable_widgets = [
            ctk.CTkButton,
            ctk.CTkCheckBox,
        ]

        for widget in widgets:
            for hoverable in hoverable_widgets:
                if isinstance(widget, hoverable):
                    color = widget.cget('fg_color')

                    if isinstance(color, list):
                        self.msg.warning(f'{widget} with {color = }')
                    widget.configure(hover_color=self.adjust_color(color, 40))

            if isinstance(widget, ctk.CTkSlider):
                color = widget.cget('progress_color')

                if isinstance(color, list):
                    self.msg.warning(f'{widget} with {color = }')
                widget.configure(button_hover_color=self.adjust_color(color, 40))

            if isinstance(widget, ctk.CTkScrollbar):
                color = widget.cget('button_color')

                if isinstance(color, list):
                    self.msg.warning(f'{widget} with {color = }')

                widget.configure(button_hover_color=self.adjust_color(color, 40))


    def set_default_text_color(self, exclude_scope = None, scope = None):
        scope = self.master if not scope else scope
        all_widgets = self.get_widgets_from_scope([], scope.winfo_children())
        exclude_widgets = self.get_widgets_from_scope([], exclude_scope.winfo_children()) if exclude_scope else []
        complementary = self.complementaryColor(self.STANDARD_TEXT_COLOR)

        for widget in all_widgets:
            if widget not in exclude_widgets:
                try:
                    if widget.cget('text_color') != complementary:
                        widget.configure(text_color=self.STANDARD_TEXT_COLOR)
                except Exception as e:
                    continue


    def set_default_writable_content_color(self, scope = None):
        scope = self.master if not scope else scope
        widgets = self.get_widgets_from_scope([], scope.winfo_children())

        writable_widgets = [
            ctk.CTkEntry,
            ctk.CTkTextbox,
            EntryExpanding
        ]

        for widget in widgets:
            for widget_type in writable_widgets:
                if isinstance(widget, widget_type):
                    widget.configure(fg_color=self.STANDARD_WRITABLE_CONTENT_COLOR)


    def set_default_button_text_color(self, scope = None):
        scope = self.master if not scope else scope
        complementary = self.complementaryColor(self.STANDARD_BUTTON_TEXT_COLOR)
        widgets = self.get_widgets_from_scope([], scope.winfo_children())

        for widget in widgets:
            if isinstance(widget, ctk.CTkButton):
                if widget.cget('text_color') != complementary:
                    widget.configure(text_color=self.STANDARD_BUTTON_TEXT_COLOR)
            elif isinstance(widget, ctk.CTkCheckBox):
                widget.configure(checkmark_color=self.STANDARD_BUTTON_TEXT_COLOR)

    def set_ordered_frame_color(self, frame: ctk.CTkFrame):
        frame.configure(fg_color=self.STANDARD_ORDERED_FRAME_COLOR, border_color=self.STANDARD_ORDERED_FRAME_BORDER_COLOR, border_width=3)


    def complementaryColor(self, hex_code):
        if hex_code[0] == '#':
            hex_code = hex_code[1:]
        rgb = (hex_code[0:2], hex_code[2:4], hex_code[4:6])
        comp = ['%02X' % (255 - int(a, 16)) for a in rgb]
        return '#' + ''.join(comp)


    def adjust_color(self, color: str, percent: float, reference: str | None = None) -> str:
        if not color.startswith('#') or len(color) != 7:
            raise ValueError('Color has to be a hexadecimal color')

        if reference is not None:
            if not reference.startswith("#") or len(reference) != 7:
                raise ValueError('Reference color has to be a hexadecimal color')

        if percent < 0 or percent > 100:
            raise ValueError('Percentage has to be between 0 and 100')

        def hex_to_hsl(hex_color):
            r = int(hex_color[1:3], 16) / 255
            g = int(hex_color[3:5], 16) / 255
            b = int(hex_color[5:7], 16) / 255

            h, l, s = colorsys.rgb_to_hls(r, g, b)
            return h, s, l

        def hsl_to_hex(h, s, l):
            r, g, b = colorsys.hls_to_rgb(h % 1.0, l, s)

            return '#{:02X}{:02X}{:02X}'.format(
                round(r * 255),
                round(g * 255),
                round(b * 255)
            )

        h, s, l = hex_to_hsl(color)
        if reference is None:
            l -= l * (percent / 100)

            if l <= 0:
                l = min(1, percent / 100)

            return hsl_to_hex(h, s, l)

        reference_h, reference_s, reference_l = hex_to_hsl(reference)
        factor = percent / 100
        hue_difference = reference_h - h

        if hue_difference > 0.5:
            hue_difference -= 1.0
        elif hue_difference < -0.5:
            hue_difference += 1.0

        h += hue_difference * factor

        s += (reference_s - s) * factor
        l += (reference_l - l) * factor

        return hsl_to_hex(h, s, l)


    def create_entry_name(self, entry_widget: ctk.CTkEntry, name: str) -> None:
        self.ENTRY_WIDGETS[name] = entry_widget


    def get_entry_by_name(self, name: str) -> ctk.CTkEntry:
        try:
            return self.ENTRY_WIDGETS[name]
        except Exception as e:
            self.msg.error(str(e))

    def handle_entry_name_return(self, name: str, return_type: str, invalid_content: str = '', include_value: str = ''):
        content = self.get_entry_by_name(name).get()
        if not content:
            return invalid_content
        try:
            return getattr(builtins, return_type)(content)
        except Exception as e:
            return include_value if content == include_value else invalid_content


    def get_widgets_from_scope(self, result, scope_children = None):
        scope_children = self.master if not scope_children else scope_children
        for child in scope_children:
            result.append(child)
            subchildren = child.winfo_children()
            if subchildren:
                self.get_widgets_from_scope(result, subchildren)

        return result


    def disable_all_buttons_from_scope(self, scope = None):
        scope = self.master if not scope else scope
        all_widgets = self.get_widgets_from_scope([], scope.winfo_children())
        widgets_to_disable = [
            ctk.CTkButton,
            ctk.CTkSlider,
            ctk.CTkCheckBox,
            ctk.CTkEntry
        ]

        for widget in all_widgets:
            for disable_widget in widgets_to_disable:
                if isinstance(widget, disable_widget):
                    widget.configure(state=ctk.DISABLED)


    def enable_all_buttons_from_scope(self, scope = None):
        scope = self.master if not scope else scope
        all_widgets = self.get_widgets_from_scope([], scope.winfo_children())
        widgets_to_disable = [
            ctk.CTkButton,
            ctk.CTkSlider,
            ctk.CTkCheckBox,
            ctk.CTkEntry
        ]

        for widget in all_widgets:
            for disable_widget in widgets_to_disable:
                if isinstance(widget, disable_widget):
                    widget.configure(state=ctk.NORMAL)


    def get_specific_button_from_scope(self, button_text: str, scope = None) -> ctk.CTkButton | None:
        scope = self.master if not scope else scope
        all_widgets = self.get_widgets_from_scope([], scope.winfo_children())
        for widget in all_widgets:
            if isinstance(widget, ctk.CTkButton):
                if widget.cget('text').upper() == button_text.upper():
                    return widget
        return None

    def change_button_kwargs_text(self, button_text: str, scope=None, **settings):
        scope = self.master if not scope else scope

        button = self.get_specific_button_from_scope(button_text, scope)
        button.configure(**settings)

    def change_button_kwargs_widget(self, button: ctk.CTkButton, **settings):
        if button:
            button.configure(**settings)
        else:
            self.msg.warning('Button does not exist')

    def clear_scope(self, scope = None):
        scope = self.master if not scope else scope
        widgets = self.get_widgets_from_scope([], scope.winfo_children())
        for widget in widgets:
            try:
                widget.destroy()
            except Exception as e:
                continue

    def clear_visible_widgets(self, destroy: bool = True, scope = None):
        scope = self.master if not scope else scope
        widgets = self.get_widgets_from_scope([], scope.winfo_children())
        for widget in widgets:
            try:
                if widget.winfo_ismapped():
                    widget.destroy() if destroy else widget.place_forget()
            except Exception as e:
                continue

    def draw_heading_line(self, fg_color = None, relheight: float = 0.02, rely: float = 0.14, scope = None):
        scope = self.master if not scope else scope
        fg_color = self.STANDARD_FG_COLOR if not fg_color else fg_color
        border_heading_content = ctk.CTkFrame(scope, corner_radius=0, fg_color=fg_color)
        border_heading_content.place(relx=0, rely=rely, relwidth=1, relheight=relheight)


    def draw_mode_line(self, scope = None):
        scope = self.master if not scope else scope
        border_mode_site = ctk.CTkFrame(scope, corner_radius=0, fg_color=self.STANDARD_MODE_BORDER_COLOR)
        border_mode_site.place(relx=0.96, relwidth=0.05, relheight=1)


    def make_label_fit_in_frame(self, label: ctk.CTkLabel, parent_frame: ctk.CTkFrame, truncate=False, scope=None):
        scope = self.master if not scope else scope
        while not parent_frame.winfo_ismapped():
            scope.update_idletasks()

        while not label.winfo_ismapped():
            scope.update_idletasks()

        frame_x = parent_frame.winfo_rootx()
        label_x = label.winfo_rootx()
        padding_left = label_x - frame_x
        max_width = parent_frame.winfo_width() - padding_left

        original_text = label.cget("text")

        if truncate:
            if not original_text:
                return

            label.configure(text=original_text)
            label.update_idletasks()

            if label.winfo_width() <= max_width:
                return

            ellipsis = "..."
            shortened_text = ""

            for char in original_text:
                test_text = shortened_text + char + ellipsis

                label.configure(text=test_text)
                label.update_idletasks()

                if label.winfo_width() <= max_width:
                    shortened_text += char
                else:
                    break

            label.configure(text=shortened_text.rstrip() + ellipsis)
            label.update_idletasks()
            return

        paragraphs = original_text.split("\n")
        lines = []

        for paragraph in paragraphs:
            words = paragraph.split(" ")
            current_line = ""

            for word in words:
                if current_line:
                    test_line = current_line + " " + word
                else:
                    test_line = word

                test_text = "\n".join(lines + [test_line])
                label.configure(text=test_text)
                label.update_idletasks()

                if label.winfo_width() <= max_width:
                    current_line = test_line
                    continue

                if current_line:
                    lines.append(current_line)
                    current_line = ""

                label.configure(text="\n".join(lines + [word]))
                label.update_idletasks()

                if label.winfo_width() <= max_width:
                    current_line = word
                    continue

                remaining = word

                while remaining:
                    part = ""

                    for char in remaining:
                        test_part = part + char

                        label.configure(
                            text="\n".join(
                                lines + [current_line + test_part + "-"]
                            )
                        )
                        label.update_idletasks()

                        if label.winfo_width() <= max_width:
                            part = test_part
                        else:
                            break

                    if not part:
                        part = remaining[0]

                    remaining = remaining[len(part):]

                    if remaining:
                        lines.append(current_line + part + "-")
                        current_line = ""
                    else:
                        current_line += part

            if current_line:
                lines.append(current_line)

        final_text = "\n".join(lines)

        label.configure(text=final_text)
        label.update_idletasks()

