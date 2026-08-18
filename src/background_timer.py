import time
import customtkinter
import threading
from messageR import MessageR
from NumberPicker import NumberPicker
import pygame
import builtins

timer_app = customtkinter.CTk()
timer_app.geometry('800x400')
mode_site = customtkinter.CTkFrame(timer_app)
content_site = customtkinter.CTkFrame(timer_app)

msg = MessageR('Global')

pygame.mixer.init()
pygame.init()
pygame.mixer.music.load('..\\media\\Ringtone.mp3')

STANDARD_FG_COLOR = '#0000FF'
STANDARD_TEXT_COLOR = 'white'
STANDARD_BUTTON_TEXT_COLOR = 'white'
#@TODO fix hovering above buttons

SOUND_LOOPS = 3
TIMER_RUNNING = False
MODE_START_Y = 0.25
MODE_Y_INCREASER = 0.1
PLACEMENT_WIDGETS = []
ENTRY_WIDGETS = {}

warning_label = customtkinter.CTkLabel(content_site, text='', text_color='black', fg_color='yellow')

def show_warning_text(text: str, seconds: float | int) -> None:
    def show_text(text, seconds):
        time_now = time.time()
        warning_label.configure(text=text, font=('Arial', 20))
        warning_label.place(relx=0.5, rely=0.5, anchor='center')
        warning_label.lift()

        while time.time() - time_now < seconds:
            pass

        warning_label.place_forget()

    threading.Thread(target=show_text, args=(text, seconds,), daemon=True).start()

def set_default_fg_color():
    widgets = get_widgets_from_scope(timer_app.winfo_children(), [])
    widget_types_to_change = [
        customtkinter.CTkButton,
        customtkinter.CTkCheckBox,
        customtkinter.CTkSlider  # @TODO: is it the slider for the volume?
    ]

    for widget in widgets:
        for widget_type in widget_types_to_change:
            if isinstance(widget, widget_type):
                widget.configure(fg_color=STANDARD_FG_COLOR)

def set_default_text_color(exclude_buttons: bool = False):
    widgets = get_widgets_from_scope(timer_app.winfo_children(), [])

    if exclude_buttons:
        for widget in widgets:
            if not isinstance(widget, customtkinter.CTkButton):
                try:
                    widget.configure(text_color=STANDARD_TEXT_COLOR)
                except Exception as e:
                    continue
    else:
        for widget in widgets:
            try:
                widget.configure(text_color=STANDARD_TEXT_COLOR)
            except Exception as e:
                continue

def set_default_button_text_color():
    widgets = get_widgets_from_scope(timer_app.winfo_children(), [])


    for widget in widgets:
        if isinstance(widget, customtkinter.CTkButton):
            widget.configure(text_color=STANDARD_BUTTON_TEXT_COLOR)
        elif isinstance(widget, customtkinter.CTkCheckBox):
            widget.configure(checkmark_color=STANDARD_BUTTON_TEXT_COLOR)


def complementaryColor(hex_code):
    if hex_code[0] == '#':
        hex_code = hex_code[1:]
    rgb = (hex_code[0:2], hex_code[2:4], hex_code[4:6])
    comp = ['%02X' % (255 - int(a, 16)) for a in rgb]
    return ''.join(comp)

def create_entry_name(entry_widget: customtkinter.CTkEntry, name: str) -> None:
    ENTRY_WIDGETS[name] = entry_widget


def get_entry_by_name(name: str) -> customtkinter.CTkEntry:
    try:
        return ENTRY_WIDGETS[name]
    except Exception as e:
        msg.error(str(e))

def handle_entry_name_return(name: str, return_type: str, invalid_content: str = ''):
    content = get_entry_by_name(name).get()
    if not content:
        return invalid_content

    return getattr(builtins, return_type)(content)


def place_mode_widget(widget: customtkinter) -> None:
    curr_widget_number = len(PLACEMENT_WIDGETS)
    PLACEMENT_WIDGETS.append(curr_widget_number)

    y_cord = MODE_START_Y + MODE_Y_INCREASER * curr_widget_number
    widget.place(relx=0.5, rely=y_cord, anchor='center')

def get_widgets_from_scope(scope, result):
    for child in scope:
        result.append(child)
        subchildren = child.winfo_children()
        if subchildren:
            get_widgets_from_scope(subchildren, result)

    return result


def disable_all_buttons_from_scope(scope):
    all_widgets = get_widgets_from_scope(scope.winfo_children(), [])
    for widget in all_widgets:
        if isinstance(widget, customtkinter.CTkButton):
            widget.configure(state=customtkinter.DISABLED)


def enable_all_buttons_from_scope(scope):
    all_widgets = get_widgets_from_scope(scope.winfo_children(), [])
    for widget in all_widgets:
        if isinstance(widget, customtkinter.CTkButton):
            widget.configure(state=customtkinter.NORMAL)


def get_specific_button_from_scope(scope, button_text: str):
    all_widgets = get_widgets_from_scope(scope.winfo_children(), [])
    for widget in all_widgets:
        if isinstance(widget, customtkinter.CTkButton):
            if widget.cget('text').upper() == button_text.upper():
                return widget

def change_button_kwargs(scope, button_text: str, **kwargs):
    button = get_specific_button_from_scope(scope, button_text)
    button.configure(**kwargs)



def change_on_timer():
    disable_all_buttons_from_scope(content_site)
    fg_color = f'#{complementaryColor(STANDARD_FG_COLOR)}'
    text_color = f''  #@TODO change text color to complimentary
    change_button_kwargs(content_site, 'Start', state=customtkinter.NORMAL, text='Stop', fg_color=fg_color)


def change_off_timer():
    enable_all_buttons_from_scope(content_site)
    change_button_kwargs(content_site, 'Stop', text='Start', fg_color=STANDARD_FG_COLOR)


def start_timer(hours: NumberPicker, minutes: NumberPicker, seconds: NumberPicker) -> None:
    loops = handle_entry_name_return('loop', 'int', 'empty')
    if loops == 'empty':
        show_warning_text('Please insert a loop count!', 4)
        return

    if not loops >= 0:
        show_warning_text('The timer can not have negative loops!', 4)
        return

    def run_timer(hours, minutes, seconds, loops):
        global SOUND_LOOPS, TIMER_RUNNING
        try:
            change_on_timer()
            msg.info('Timer has started!')
            while True:
                if hours.get() != 0 and minutes.get() == 0 and seconds.get() == 0:
                    hours.decrease()
                    minutes.set(minutes.get_max() - 1)
                    seconds.set(seconds.get_max() - 1)
                if hours.get() != 0 or minutes.get() != 0 or seconds.get() != 0:
                    seconds.decrease()
                if minutes.get() != 0 and seconds.get() == 0:
                    seconds.set(seconds.get_max() - 1)
                    minutes.decrease()
                if hours.get() == 0 and minutes.get() == 0 and seconds.get() == 0:
                    msg.good('Timer ended successfully!')
                    break
                time.sleep(1)

            SOUND_LOOPS = loops
            play_sound(SOUND_LOOPS)
        except Exception as e:
            msg.bad('Timer has ended with a problem: ' + str(e))
        finally:
            change_off_timer()
            TIMER_RUNNING = False

    threading.Thread(target=run_timer, args=(hours, minutes, seconds, loops,)).start()


def play_sound(loops:int) -> None:
    i = 0
    print(f'{loops = }')
    while i < 1:
        pygame.mixer.music.set_volume(10)
        pygame.mixer.music.play(loops=loops, start=0.0)
        i += 1
    msg.info('Sound ended')


mode_site.place(relx=0, rely=0, relwidth=0.2, relheight=1)
content_site.place(relx=0.2, rely=0, relwidth=0.8, relheight=1)

border_mode_site = customtkinter.CTkFrame(mode_site, corner_radius=0, fg_color='#555555')
border_mode_site.place(relx=0.96, relwidth=0.04, relheight=1)


border_heading_content = customtkinter.CTkFrame(content_site, corner_radius=0, fg_color=STANDARD_FG_COLOR)
border_heading_content.place(relx=0, rely=0.14, relwidth=1, relheight=0.02)


# ==================================
# ============= MODE ===============
# ==================================

# ------------- TIMER --------------
timer_button_mode = customtkinter.CTkButton(mode_site, text='Timer')
stop_watch_button_mode = customtkinter.CTkButton(mode_site, text='Stop Watch')


place_mode_widget(timer_button_mode)
place_mode_widget(stop_watch_button_mode)


# ==================================
# =========== Content ==============
# ==================================

# ------------- TIMER --------------

timer_label_content = customtkinter.CTkLabel(content_site, text='Timer', font=('Arial', 25))
timer_label_content.place(relx=0.5, rely=0.07, anchor='center')

timer_frame = customtkinter.CTkFrame(content_site)
timer_frame.place(relx=0.5, rely=0.4, relwidth=0.5, relheight=0.45, anchor='center')

hours_frame = customtkinter.CTkFrame(timer_frame)
hours_picker = NumberPicker(hours_frame, 0, 99)
hours_label_content = customtkinter.CTkLabel(hours_frame, text='Hours', font=('Arial', 12))
hours_picker.place(relx=0.7, rely=0.45, anchor='center')
hours_label_content.place(relx=0.7, rely=0.1, anchor='center')
hours_frame.place(relx=0.2, rely=0.5, relwidth=0.4, anchor='center')

minutes_frame = customtkinter.CTkFrame(timer_frame)
minutes_picker = NumberPicker(minutes_frame, 0, 60)
minutes_label_content = customtkinter.CTkLabel(minutes_frame, text='Minutes', font=('Arial', 12))
minutes_picker.place(relx=0.5, rely=0.45, anchor='center')
minutes_label_content.place(relx=0.5, rely=0.1, anchor='center')
minutes_frame.place(relx=0.5, rely=0.5, relwidth=0.2, anchor='center')

seconds_frame = customtkinter.CTkFrame(timer_frame)
seconds_picker = NumberPicker(seconds_frame, 0, 60)
seconds_label_content = customtkinter.CTkLabel(seconds_frame, text='Seconds', font=('Arial', 12))
seconds_picker.place(relx=0.3, rely=0.45, anchor='center')
seconds_label_content.place(relx=0.3, rely=0.1, anchor='center')
seconds_frame.place(relx=0.8, rely=0.5, relwidth=0.4, anchor='center')

button_start_timer = customtkinter.CTkButton(content_site, text='Start', command=lambda: start_timer(hours=hours_picker, minutes=minutes_picker, seconds=seconds_picker))
button_start_timer.place(relx=0.5, rely=0.6, anchor='center')

hide_checkbox = customtkinter.CTkCheckBox(content_site, text='hide timer')
hide_checkbox.select()
hide_checkbox.place(relx=0.05, rely=0.75)

loop_frame = customtkinter.CTkFrame(content_site, fg_color='transparent')
loop_label = customtkinter.CTkLabel(loop_frame, text='Loop count:')
loop_entry = customtkinter.CTkEntry(loop_frame, placeholder_text=f'{SOUND_LOOPS}')
loop_entry.set('3')
loop_label.place(relx=0, relwidth=0.4)
loop_entry.place(relx=0.4, relwidth=0.6)
loop_frame.place(relx=0.65, rely=0.75, relheight=0.1)
create_entry_name(loop_entry, 'loop')

set_default_fg_color()
set_default_text_color()
set_default_button_text_color()
timer_app.mainloop()