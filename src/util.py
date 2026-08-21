import time
import os
import threading
import customtkinter as ctk
import builtins
from messageR import MessageR

class Utility():
    def __init__(self, master):
        self.master = master
        self.STANDARD_FG_COLOR = '#1f6aa5'
        self.STANDARD_TEXT_COLOR = '#FFFFFF'
        self.STANDARD_BUTTON_TEXT_COLOR = '#FFFFFF'
        #@TODO fix hovering above buttons
        self.ENTRY_WIDGETS = {}
        self.msg = MessageR('Utility')


    def show_warning_text(self, text: str, seconds: float | int,  scope = None) -> None:
        scope = self.master if scope == None else scope

        def show_text(scope, text, seconds):
            warning_label = ctk.CTkLabel(scope, text='', text_color='black', fg_color='yellow')
            time_now = time.time()
            warning_label.configure(text=text, font=('Arial', 20), text_color='black')
            warning_label.place(relx=0.5, rely=0.5, anchor='center')
            warning_label.lift()

            while time.time() - time_now < seconds:
                pass

            warning_label.place_forget()

        threading.Thread(target=show_text, args=(scope, text, seconds,), daemon=True).start()




    def set_default_fg_color(self, scope = None):
        scope = self.master if scope == None else scope

        widgets = self.get_widgets_from_scope(scope.winfo_children(), [])
        widget_types_to_change = [
            ctk.CTkButton,
            ctk.CTkCheckBox
        ]

        for widget in widgets:
            for widget_type in widget_types_to_change:
                if isinstance(widget, widget_type):
                    widget.configure(fg_color=self.STANDARD_FG_COLOR)
                elif isinstance(widget, ctk.CTkSlider):
                    widget.configure(button_color=self.STANDARD_FG_COLOR, progress_color=self.STANDARD_FG_COLOR)

    def set_default_text_color(self, exclude_buttons: bool = False, scope = None):
        scope = self.master if scope == None else scope
        widgets = self.get_widgets_from_scope(scope.winfo_children(), [])

        if exclude_buttons:
            for widget in widgets:
                if not isinstance(widget, ctk.CTkButton):
                    try:
                        widget.configure(text_color=self.STANDARD_TEXT_COLOR)
                    except Exception as e:
                        continue
        else:
            for widget in widgets:
                try:
                    widget.configure(text_color=self.STANDARD_TEXT_COLOR)
                except Exception as e:
                    continue

    def set_default_button_text_color(self, scope = None):
        scope = self.master if scope == None else scope

        widgets = self.get_widgets_from_scope(scope.winfo_children(), [])

        for widget in widgets:
            if isinstance(widget, ctk.CTkButton):
                widget.configure(text_color=self.STANDARD_BUTTON_TEXT_COLOR)
            elif isinstance(widget, ctk.CTkCheckBox):
                widget.configure(checkmark_color=self.STANDARD_BUTTON_TEXT_COLOR)


    def complementaryColor(self, hex_code):
        if hex_code[0] == '#':
            hex_code = hex_code[1:]
        rgb = (hex_code[0:2], hex_code[2:4], hex_code[4:6])
        comp = ['%02X' % (255 - int(a, 16)) for a in rgb]
        return ''.join(comp)

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


    def get_widgets_from_scope(self, result, scope = None):
        scope = self.master if scope == None else scope

        for child in scope:
            result.append(child)
            subchildren = child.winfo_children()
            if subchildren:
                self.get_widgets_from_scope(result, subchildren)

        return result


    def disable_all_buttons_from_scope(self, scope = None):
        scope = self.master if scope == None else scope

        all_widgets = self.get_widgets_from_scope(scope.winfo_children(), [])
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
        scope = self.master if scope == None else scope

        all_widgets = self.get_widgets_from_scope(scope.winfo_children(), [])
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


    def get_specific_button_from_scope(self, button_text: str, scope = None):
        scope = self.master if scope == None else scope

        all_widgets = self.get_widgets_from_scope(scope.winfo_children(), [])
        for widget in all_widgets:
            if isinstance(widget, ctk.CTkButton):
                if widget.cget('text').upper() == button_text.upper():
                    return widget

    def change_button_kwargs(self, button_text: str, scope=None, **kwargs):
        scope = self.master if scope == None else scope

        button = self.get_specific_button_from_scope(scope, button_text)
        button.configure(**kwargs)

