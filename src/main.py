import os
import customtkinter as ctk
import pygame
from messageR import MessageR
from util import Utility
from timeR import TimeR
from stop_watch import Stop_Watch
from alarm import Alarm

app = ctk.CTk()
app.geometry('800x400')
mode_site = ctk.CTkFrame(app)
content_site = ctk.CTkFrame(app)

top_label_content = ctk.CTkLabel(content_site, font=('Arial', 25))
TOP_LABEL_POS = {'relx': 0.5, 'rely': 0.07, 'anchor': 'center'}

msg = MessageR('Global')
utility = Utility(app)

timer_site = TimeR(content_site,
                   TOP_LABEL_POS=TOP_LABEL_POS,
                   top_label_content=top_label_content)

stop_watch_site = Stop_Watch(content_site,
                   TOP_LABEL_POS=TOP_LABEL_POS,
                   top_label_content=top_label_content)

alarm_site = Alarm(content_site,
                   TOP_LABEL_POS=TOP_LABEL_POS,
                   top_label_content=top_label_content)

pygame.mixer.init()
pygame.init()
pygame.mixer.music.load('..\\media\\Ringtone.mp3')


MODE_START_Y = 0.25
MODE_Y_INCREASER = 0.1
PLACEMENT_WIDGETS = []

def clear_page():
    utility.clear_scope(content_site)
    border_heading_content = ctk.CTkFrame(content_site, corner_radius=0, fg_color=utility.STANDARD_FG_COLOR)
    border_heading_content.place(relx=0, rely=0.14, relwidth=1, relheight=0.02)

def place_mode_widget(widget: ctk) -> None:
    curr_widget_number = len(PLACEMENT_WIDGETS)
    PLACEMENT_WIDGETS.append(curr_widget_number)

    y_cord = MODE_START_Y + MODE_Y_INCREASER * curr_widget_number
    widget.place(relx=0.5, rely=y_cord, anchor='center')

def focus_timer():
    clear_page()
    timer_site.start()

def focus_alarm():
    clear_page()

def focus_stop_watch():
    clear_page()




mode_site.place(relx=0, rely=0, relwidth=0.2, relheight=1)
content_site.place(relx=0.2, rely=0, relwidth=0.8, relheight=1)

border_mode_site = ctk.CTkFrame(mode_site, corner_radius=0, fg_color='#555555')
border_mode_site.place(relx=0.96, relwidth=0.04, relheight=1)

border_heading_content = ctk.CTkFrame(content_site, corner_radius=0, fg_color=utility.STANDARD_FG_COLOR)
border_heading_content.place(relx=0, rely=0.14, relwidth=1, relheight=0.02)


# ==================================
# ============= MODE ===============
# ==================================

# ------------- TIMER --------------
timer_button_mode = ctk.CTkButton(mode_site, text='Timer', command=focus_timer)
stop_watch_button_mode = ctk.CTkButton(mode_site, text='Stop Watch', command=focus_stop_watch)
alarm_button_mode = ctk.CTkButton(mode_site, text='Alarm', command=focus_alarm)

place_mode_widget(timer_button_mode)
place_mode_widget(stop_watch_button_mode)
place_mode_widget(alarm_button_mode)


# ==================================
# =========== Content ==============
# ==================================

# ------------- TIMER --------------

utility.set_default_fg_color()
utility.set_default_text_color()
utility.set_default_button_text_color()

stop_watch_site.start()  # start with the timer (in the future)

app.mainloop()