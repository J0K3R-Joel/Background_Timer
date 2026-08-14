import time
import customtkinter
import threading
from messageR import MessageR
from NumberPicker import NumberPicker

msg = MessageR('Global')


MODE_START_Y = 0.25
MODE_Y_INCREASER = 0.1
PLACEMENT_WIDGETS = []


def place_mode_widget(widget: customtkinter) -> None:
    curr_widget_number = len(PLACEMENT_WIDGETS)
    PLACEMENT_WIDGETS.append(curr_widget_number)

    y_cord = MODE_START_Y + MODE_Y_INCREASER * curr_widget_number
    widget.place(relx=0.5, rely=y_cord, anchor='center')

def start_timer(hours: NumberPicker, minutes: NumberPicker, seconds: NumberPicker) -> None:
    def run_timer(hours, minutes, seconds):
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
        else:
            msg.bad('Timer has ended with a problem')


    threading.Thread(target=run_timer, args=(hours, minutes, seconds,)).start()




timer_app = customtkinter.CTk()
timer_app.geometry('800x400')


mode_site = customtkinter.CTkFrame(timer_app, )
mode_site.place(relx=0, rely=0, relwidth=0.2, relheight=1)
content_site = customtkinter.CTkFrame(timer_app)
content_site.place(relx=0.2, rely=0, relwidth=0.8, relheight=1)

border_mode_site = customtkinter.CTkFrame(mode_site, corner_radius=0, fg_color='#555555')
border_mode_site.place(relx=0.96, relwidth=0.04, relheight=1)


border_heading_content = customtkinter.CTkFrame(content_site, corner_radius=0, fg_color='#1f6aa5')
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
hours_picker.place(relx=0.7, rely=0.5, anchor='center')
hours_label_content.place(relx=0.7, rely=0.1, anchor='center')
hours_frame.place(relx=0.2, rely=0.5, relwidth=0.4, anchor='center')

minutes_frame = customtkinter.CTkFrame(timer_frame)
minutes_picker = NumberPicker(minutes_frame, 0, 60)
minutes_label_content = customtkinter.CTkLabel(minutes_frame, text='Minutes', font=('Arial', 12))
minutes_picker.place(relx=0.5, rely=0.5, anchor='center')
minutes_label_content.place(relx=0.5, rely=0.1, anchor='center')
minutes_frame.place(relx=0.5, rely=0.5, relwidth=0.2, anchor='center')

seconds_frame = customtkinter.CTkFrame(timer_frame)
seconds_picker = NumberPicker(seconds_frame, 0, 60)
seconds_label_content = customtkinter.CTkLabel(seconds_frame, text='Seconds', font=('Arial', 12))
seconds_picker.place(relx=0.3, rely=0.5, anchor='center')
seconds_label_content.place(relx=0.3, rely=0.1, anchor='center')
seconds_frame.place(relx=0.8, rely=0.5, relwidth=0.4, anchor='center')

button_start_timer = customtkinter.CTkButton(
    content_site,
    text='Start',
    command=lambda: start_timer(hours=hours_picker, minutes=minutes_picker, seconds=seconds_picker)
)
button_start_timer.place(relx=0.5, rely=0.7, anchor='center')


timer_app.mainloop()