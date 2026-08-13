import time
import customtkinter
import messageR
import inspect

msg = messageR.MessageR('Global')


MODE_START_Y = 0.25
MODE_Y_INCREASER = 0.1
PLACEMENT_WIDGETS = []


def place_mode_widget(widget: customtkinter) -> None:
    curr_widget_number = len(PLACEMENT_WIDGETS)
    PLACEMENT_WIDGETS.append(curr_widget_number)

    y_cord = MODE_START_Y + MODE_Y_INCREASER * curr_widget_number
    widget.place(relx=0.5, rely=y_cord, anchor='center')


timer_app = customtkinter.CTk()
timer_app.geometry('800x400')


mode_site = customtkinter.CTkFrame(timer_app, )
mode_site.place(relx=0, rely=0, relwidth=0.2, relheight=1)
content_site = customtkinter.CTkFrame(timer_app)
content_site.place(relx=0.2, rely=0, relwidth=0.8, relheight=1)

border_mode_site = customtkinter.CTkFrame(mode_site, corner_radius=0, fg_color='#555555')
border_mode_site.place(relx=0.96, relwidth=0.04, relheight=1)


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

timer_label_content = customtkinter.CTkLabel(content_site, text='Timer')
timer_label_content.place(relx=0.5, rely=0.2, anchor='center')

timer_app.mainloop()