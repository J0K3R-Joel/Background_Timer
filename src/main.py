import customtkinter as ctk
import pygame.mixer as mixer
from messagR import MessageR
from util import Utility
from timeR import TimeR
from stop_watch import Stop_Watch
from alarm import Alarm
import socket
import threading

INSTANCE_HOST = '127.0.0.1'
INSTANCE_PORT = 47821

def try_show_existing_instance():
    try:
        with socket.create_connection((INSTANCE_HOST, INSTANCE_PORT), timeout=0.2) as connection:
            connection.sendall(b'SHOW')

        return True
    except (ConnectionRefusedError, OSError):
        return False


if try_show_existing_instance():
    raise SystemExit

app = ctk.CTk()
app.geometry('800x400')
app.title('Background Timer')
mode_site = ctk.CTkFrame(app)
content_site = ctk.CTkFrame(app)

top_label_content = ctk.CTkLabel(content_site, font=('Arial', 25))
TOP_LABEL_POS = {'relx': 0.5, 'rely': 0.07, 'anchor': 'center'}

msg = MessageR('Global')
utility = Utility(app)

mixer.init()
mixer.music.load('.\\media\\Ringtone.mp3')


MODE_START_Y = 0.25
MODE_Y_INCREASER = 0.1
PLACEMENT_WIDGETS = []

def start_instance_server(app):
    def server():
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind((INSTANCE_HOST, INSTANCE_PORT))
            server_socket.listen(1)

            while True:
                connection, _ = server_socket.accept()
                with connection:
                    command = connection.recv(32).decode('utf-8')

                if command == 'SHOW':
                    app.after(0, show_existing_instance)

    threading.Thread(target=server, daemon=True).start()


def show_existing_instance():
    app.deiconify()
    app.lift()
    app.focus_force()


def close_application():
    if alarm_site.ALARM_RUNNING:
        app.withdraw()
        return

    app.destroy()


def clear_page() -> ctk.CTkLabel:
    global top_label_content
    utility.clear_scope(content_site)
    border_heading_content = ctk.CTkFrame(content_site, corner_radius=0, fg_color=utility.STANDARD_FG_COLOR)
    border_heading_content.place(relx=0, rely=0.14, relwidth=1, relheight=0.02)
    top_label_content = ctk.CTkLabel(content_site, font=('Arial', 22))

    return top_label_content


def place_mode_widget(widget: ctk) -> None:
    curr_widget_number = len(PLACEMENT_WIDGETS)
    PLACEMENT_WIDGETS.append(curr_widget_number)

    y_cord = MODE_START_Y + MODE_Y_INCREASER * curr_widget_number
    widget.place(relx=0.96/2, rely=y_cord, anchor='center')  # 0.96/2, because the mode line is drawn at 0.96 relx


def focus_timer():
    label = clear_page()
    timer_site.set_top_label_content(label)
    timer_site.build()

def focus_alarm():
    label = clear_page()
    alarm_site.set_top_label_content(label)
    alarm_site.build()

def focus_stop_watch():
    label = clear_page()
    stop_watch_site.set_top_label_content(label)
    stop_watch_site.build()


mode_site.place(relx=0, rely=0, relwidth=0.2, relheight=1)
content_site.place(relx=0.2, rely=0, relwidth=0.8, relheight=1)


utility.draw_mode_line(mode_site)
utility.draw_heading_line(scope=content_site)



# ==================================
# ============= MODE ===============
# ================================== 

timer_button_mode = ctk.CTkButton(mode_site, text='Timer', command=focus_timer)
stop_watch_button_mode = ctk.CTkButton(mode_site, text='Stop Watch', command=focus_stop_watch)
alarm_button_mode = ctk.CTkButton(mode_site, text='Alarm', command=focus_alarm)

place_mode_widget(timer_button_mode)
place_mode_widget(stop_watch_button_mode)
place_mode_widget(alarm_button_mode)


# ==================================
# =========== Content ==============
# ==================================

timing_args = (content_site,
               TOP_LABEL_POS,
               top_label_content,
               mode_site)

timer_site = TimeR(*timing_args, app=app)
stop_watch_site = Stop_Watch(*timing_args)
alarm_site = Alarm(*timing_args, app=app)

utility.set_default_button_text_color()
utility.set_default_fg_color()
utility.set_default_hover_color()
utility.set_default_text_color()
utility.set_default_button_text_color()

alarm_site.build()  # change this to the timer_site in the future

app.protocol("WM_DELETE_WINDOW", close_application)
app.mainloop()