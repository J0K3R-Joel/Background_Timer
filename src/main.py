import customtkinter as ctk
import pygame.mixer as mixer
from messagR import MessageR
from util import Utility
from timeR import TimeR
from stop_watch import Stop_Watch
from alarm import Alarm
import socket
import threading

INSTANCE_HOST = "127.0.0.1"
INSTANCE_PORT = 47821


def try_show_existing_instance():
    try:
        with socket.create_connection(
                (INSTANCE_HOST, INSTANCE_PORT),
                timeout=0.2
        ) as connection:
            connection.sendall(b"SHOW")

        return True

    except (ConnectionRefusedError, OSError):
        return False


if try_show_existing_instance():
    raise SystemExit

app = ctk.CTk()
app.geometry("800x400")
app.title("Background Timer")

mode_site = ctk.CTkFrame(app)
content_site = ctk.CTkFrame(app)

TOP_LABEL_POS = {
    "relx": 0.5,
    "rely": 0.07,
    "anchor": "center"
}

top_label_content = ctk.CTkLabel(content_site, font=("Arial", 25))

msg = MessageR("Global")
utility = Utility(app)

mixer.init()

MODE_START_Y = 0.25
MODE_Y_INCREASER = 0.1

ACTIVE_BORDER_WIDTH = 1
INACTIVE_BORDER_WIDTH = 0

MODE_BUTTONS = {}
MODES = {}
active_mode = None


def show_existing_instance():
    app.deiconify()
    app.lift()
    app.focus_force()


def start_instance_server(app):
    def server():
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind((INSTANCE_HOST, INSTANCE_PORT))
            server_socket.listen(1)

            while True:
                connection, _ = server_socket.accept()

                with connection:
                    command = connection.recv(32).decode("utf-8")

                if command == "SHOW":
                    app.after(0, show_existing_instance)

    threading.Thread(target=server, daemon=True).start()


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
    top_label_content = ctk.CTkLabel(content_site, font=("Arial", 22))

    return top_label_content


def place_mode_widget(widget, index):
    y_cord = MODE_START_Y + MODE_Y_INCREASER * index
    widget.place(relx=0.96 / 2, rely=y_cord, anchor="center")


def set_border_mode_button(active_mode_name):
    for mode_name, button in MODE_BUTTONS.items():
        border_width = ACTIVE_BORDER_WIDTH if mode_name == active_mode_name else INACTIVE_BORDER_WIDTH
        button.configure(border_width=border_width, border_color=utility.STANDARD_TEXT_COLOR)


def focus_mode(mode_name):
    global active_mode

    mode = MODES[mode_name]
    label = clear_page()
    utility.set_build_callable(mode["site"].build)
    mode["site"].set_top_label_content(label)
    mode["site"].build()
    active_mode = mode_name
    set_border_mode_button(active_mode)


def register_mode(mode_name, site):
    if mode_name in MODES:
        raise ValueError(f"The mode '{mode_name}' already exists.")

    MODES[mode_name] = {"site": site}
    button = ctk.CTkButton(mode_site, text=mode_name, command=lambda name=mode_name: focus_mode(name))
    MODE_BUTTONS[mode_name] = button
    place_mode_widget(button, len(MODE_BUTTONS) - 1)


mode_site.place(relx=0, rely=0, relwidth=0.2, relheight=1)
content_site.place(relx=0.2, rely=0, relwidth=0.8, relheight=1)

utility.draw_mode_line(mode_site)
utility.draw_heading_line(scope=content_site)

theme_button = utility.create_theme_button(image_path="images/farbkreis.png", scope=mode_site, size=(36, 36))
theme_button.place(relx=0.5, rely=0.1, anchor="center")

# ==================================
# ========== Content Sites =========
# ==================================

timing_args = (
    content_site,
    TOP_LABEL_POS,
    top_label_content,
    mode_site
)

timer_site = TimeR(*timing_args, app=app)
stop_watch_site = Stop_Watch(*timing_args)
alarm_site = Alarm(*timing_args, app=app)

register_mode("Alarm", alarm_site)
register_mode("Timer", timer_site)
register_mode("Stop Watch", stop_watch_site)

utility.set_default_button_text_color()
utility.set_default_fg_color()
utility.set_default_hover_color()
utility.set_default_text_color()
utility.set_default_button_text_color()

theme_button.configure(fg_color='transparent')
theme_button.configure(hover_color=utility.complementaryColor(utility.STANDARD_BACKGROUND_COLOR))

app.protocol("WM_DELETE_WINDOW", close_application)

focus_mode("Alarm")
start_instance_server(app)
app.mainloop()
