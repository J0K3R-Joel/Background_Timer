import threading
import time

import customtkinter as ctk
from number_pickR import NumberPicker
from timing import Timing
from util import Utility

class Stop_Watch(Timing):
    def __init__(self, master, TOP_LABEL_POS, top_label_content: ctk.CTkLabel):
        Timing.__init__(self, master, TOP_LABEL_POS, top_label_content)
        self.utility = Utility(self.master)
        self.paused = False
        self.stopped = False

    
    def __watch_mode_active(self, start_button, pause_button, rounding_button):
        text_color = self.utility.complementaryColor(self.utility.STANDARD_BUTTON_TEXT_COLOR)
        fg_color = self.utility.complementaryColor(self.utility.STANDARD_FG_COLOR)

        self.stopped = False
        self.paused = False

        lap_label = ctk.CTkLabel(self.master, text='Laps:', font=('Arial', 16))
        lap_frame = ctk.CTkFrame(self.master, fg_color='transparent')
        center_line = ctk.CTkFrame(self.master, corner_radius=0, fg_color='#555555')

        start_button.configure(text='Stop', fg_color=fg_color, text_color=text_color, command=lambda: self.__stop_watch(start_button, pause_button, rounding_button, lap_label, lap_frame, center_line))
        pause_button.configure(text='⏸', fg_color=fg_color, text_color=text_color, command=lambda: self.__stopper(pause_button))
        rounding_button.configure(text='Round', fg_color=fg_color, text_color=text_color, command=lambda: self.__round_now(lap_frame))

        pause_button.place(relx=0.38, rely=0.46, relwidth=0.1, anchor='center')
        rounding_button.place(relx=0.62, rely=0.46, relwidth=0.1, anchor='center')
        center_line.place(relx=0, rely=0.53, relwidth=1, relheight=0.01)
        lap_label.place(relx=0.02, rely=0.55)
        lap_frame.place(relx=0.02, rely=0.62, relwidth=0.96, relheight=0.34)


    def __watch_mode_inactive(self, start_button, pause_button, rounding_button, *removable_widgets):
        start_button.configure(text='Start', fg_color=self.utility.STANDARD_FG_COLOR, text_color=self.utility.STANDARD_BUTTON_TEXT_COLOR,  command=lambda: self.__start_watch(start_button, pause_button, rounding_button))

        self.stopped = True
        self.paused = False
        pause_button.place_forget()
        rounding_button.place_forget()
        for widget in removable_widgets:
            widget.destroy()



    def __round_now(self, lap_frame):
        pass

    def __stopper(self, pause_button):
        pause_button.configure(text='▶', command=lambda: self.__continuer(pause_button))
        self.paused = True

    def __continuer(self, pause_button):
        pause_button.configure(text='⏸', command=lambda: self.__stopper(pause_button))
        self.paused = False


    def __start_watch(self, start_button: ctk.CTkButton, pause_button: ctk.CTkButton, rounding_button: ctk.CTkButton):
        self.__watch_mode_active(start_button, pause_button, rounding_button)

        def begin_now():
            sleeping = 0
            difference = 0
            waiting = 0
            last_start_time = 0
            start_time = 0
            while not self.stopped:
                if start_time:
                    last_start_time = time.time()
                while not self.paused and not self.stopped:
                    difference = (start_time - last_start_time)
                    start_time = time.time()

                    waiting = 0.01 - (start_time - last_start_time)
                    adjuster = sleeping if sleeping < 0 else 0
                    sleeping = waiting - difference - adjuster

                    print(sleeping, waiting, difference)
                    time.sleep(sleeping if sleeping > 0 else 0)
                    last_start_time = time.time()

                    millis = int(self.milliseconds_time_label.cget('text'))
                    seconds = int(self.seconds_time_label.cget('text'))
                    minutes = 0
                    millis += 1

                    if millis == 100:
                        seconds += 1
                        self.seconds_time_label.configure(text=seconds)
                        millis = 0

                    if seconds == 60:
                        minutes = int(self.minutes_time_label.cget('text'))
                        minutes += 1
                        self.minutes_time_label.configure(text=minutes)
                        seconds = 0
                        self.seconds_time_label.configure(text=seconds)

                    if minutes and minutes == 60:
                        hours = int(self.hours_time_label.cget('text'))
                        hours += 1
                        self.hours_time_label.configure(text=hours)
                        minutes = 0
                        self.minutes_time_label.configure(text=minutes)

                    self.milliseconds_time_label.configure(text=millis)



        threading.Thread(target=begin_now, daemon=True).start()



    def __stop_watch(self, start_button: ctk.CTkButton, pause_button: ctk.CTkButton, rounding_button: ctk.CTkButton, *removable_widgets):
        self.__watch_mode_inactive(start_button, pause_button, rounding_button, *removable_widgets)

        self.hours_time_label.configure(text='0')
        self.minutes_time_label.configure(text='0')
        self.seconds_time_label.configure(text='0')
        self.milliseconds_time_label.configure(text='0')

    def start(self):
        self.top_label_content.configure(text='Stop Watch')
        self.top_label_content.place(**self.TOP_LABEL_POS)

        clock_frame = ctk.CTkFrame(self.master)
        self.hours_time_label = ctk.CTkLabel(clock_frame, text='0', font=('Arial', 26))
        hour_min_sep = ctk.CTkLabel(clock_frame, text=':', font=('Arial', 26))
        self.minutes_time_label = ctk.CTkLabel(clock_frame, text='0', font=('Arial', 26))
        min_sec_sep = ctk.CTkLabel(clock_frame, text=':', font=('Arial', 26))
        self.seconds_time_label = ctk.CTkLabel(clock_frame, text='0', font=('Arial', 26))
        sec_millisec_sep = ctk.CTkLabel(clock_frame, text=':', font=('Arial', 26))
        self.milliseconds_time_label = ctk.CTkLabel(clock_frame, text='0', font=('Arial', 26))

        self.hours_time_label.place(relx=0.15, rely=0.5, anchor='center')
        hour_min_sep.place(relx=0.285, rely=0.5, anchor='center')
        self.minutes_time_label.place(relx=0.4, rely=0.5, anchor='center')
        min_sec_sep.place(relx=0.5, rely=0.5, anchor='center')
        self.seconds_time_label.place(relx=0.6, rely=0.5, anchor='center')
        sec_millisec_sep.place(relx=0.71, rely=0.5, anchor='center')
        self.milliseconds_time_label.place(relx=0.85, rely=0.5, anchor='center')

        hours_desc_label = ctk.CTkLabel(clock_frame, text='Hrs.', font=('Arial', 12))
        minutes_desc_label = ctk.CTkLabel(clock_frame, text='Mins.', font=('Arial', 12))
        sec_desc_label = ctk.CTkLabel(clock_frame, text='Secs.', font=('Arial', 12))
        millisec_desc_label = ctk.CTkLabel(clock_frame, text='Millisecs.', font=('Arial', 12))

        hours_desc_label.place(relx=0.15, rely=0.2, anchor='center')
        minutes_desc_label.place(relx=0.4, rely=0.2, anchor='center')
        sec_desc_label.place(relx=0.6, rely=0.2, anchor='center')
        millisec_desc_label.place(relx=0.85, rely=0.2, anchor='center')
        clock_frame.place(relx=0.5, rely=0.35, relheight=0.3, relwidth=0.3, anchor='center')

        pause_button = ctk.CTkButton(self.master, text='Pause')  # ▶ ⏸

        rounding_button = ctk.CTkButton(self.master, text='Round')

        start_button = ctk.CTkButton(self.master, text='Start', command= lambda: self.__start_watch(start_button, pause_button, rounding_button))
        start_button.place(relx=0.5, rely=0.46, relwidth=0.1, anchor='center')

        self.utility.hide_all_frames()
        self.utility.set_default_button_text_color()
        self.utility.set_default_fg_color()
        self.utility.set_default_button_text_color()




if __name__ == '__main__':
    app = ctk.CTk()
    app.geometry('700x400')
    top_label_content = ctk.CTkLabel(app, font=('Arial', 25))
    TOP_LABEL_POS = {'relx': 0.5, 'rely': 0.07, 'anchor': 'center'}

    watch = Stop_Watch(app, TOP_LABEL_POS, top_label_content)
    watch.start()
    app.mainloop()