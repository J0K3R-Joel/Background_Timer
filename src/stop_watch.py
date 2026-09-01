import time

import customtkinter as ctk
from timing import Timing
from util import Utility

class Stop_Watch(Timing):
    def __init__(self, *args):
        Timing.__init__(self, *args)
        self.utility = Utility(self.master)
        self.paused = False
        self.stopped = False
        self.elapsed_before_pause = 0
        self.hours_digits = 2


    def __watch_mode_active(self, start_button, pause_button, rounding_button):
        self.disable_mode_buttons()
        text_color = self.utility.complementaryColor(self.utility.STANDARD_BUTTON_TEXT_COLOR)
        fg_color = self.utility.complementaryColor(self.utility.STANDARD_FG_COLOR)

        self.stopped = False
        self.paused = False
        self.roundings = 0

        lap_label = ctk.CTkLabel(self.master, text='Laps:', font=('Arial', 16))
        center_line = ctk.CTkFrame(self.master, corner_radius=0, fg_color='#555555')

        start_button.configure(text='Stop', fg_color=fg_color, text_color=text_color, command=lambda: self.__stop_watch(start_button, pause_button, rounding_button, lap_label, center_line))
        pause_button.configure(text='⏸', fg_color=fg_color, text_color=text_color, command=lambda: self.__stopper(pause_button))
        rounding_button.configure(text='Round', fg_color=fg_color, text_color=text_color, command=self.__round_now)

        pause_button.place(relx=0.38, rely=0.46, relwidth=0.1, anchor='center')
        rounding_button.place(relx=0.62, rely=0.46, relwidth=0.1, anchor='center')
        center_line.place(relx=0, rely=0.53, relwidth=1, relheight=0.01)
        lap_label.place(relx=0.02, rely=0.55)
        self.lap_frame.place(relx=0.02, rely=0.62, relwidth=0.96, relheight=0.34)


    def __watch_mode_inactive(self, start_button, pause_button, rounding_button, *removable_widgets):
        start_button.configure(text='Start', fg_color=self.utility.STANDARD_FG_COLOR, text_color=self.utility.STANDARD_BUTTON_TEXT_COLOR,  command=lambda: self.__start_watch(start_button, pause_button, rounding_button))
        self.enable_mode_buttons()

        self.stopped = True
        self.paused = False
        self.utility.clear_scope(self.lap_placeable_frame)
        self.lap_frame.place_forget()
        self.lap_scroll_bar.place_forget()
        pause_button.place_forget()
        rounding_button.place_forget()
        for widget in removable_widgets:
            widget.destroy()


    def __pause_stopwatch(self):
        if not self.paused:
            self.elapsed_before_pause += time.perf_counter() - self.start_time
            self.paused = True


    def __resume_stopwatch(self):
        self.start_time = time.perf_counter()
        self.paused = False
        self.__update_stopwatch()


    def __round_now(self):
        if not self.lap_scroll_bar.winfo_ismapped():
            self.lap_scroll_bar.place(relx=0.97, rely=0, relwidth=0.03, relheight=1)
        hours = self.hours_time_label.cget('text')
        minutes = self.minutes_time_label.cget('text')
        seconds = self.seconds_time_label.cget('text')
        milliseconds = self.milliseconds_time_label.cget('text')

        self.roundings += 1
        time_string = ''

        if hours != '00':
            time_string += hours.lstrip('0') + 'hr :'
        if minutes != '00':
            time_string += minutes.lstrip('0') + 'min : '
        if seconds != '00':
            time_string += seconds.lstrip('0') + 'sec : '
        time_string += milliseconds + 'ms'

        lap_row = ctk.CTkFrame(self.lap_placeable_frame)
        lap_row.pack(fill='x', pady=3)

        l1 = ctk.CTkLabel(lap_row, text=f'{self.roundings}.')
        l2 = ctk.CTkLabel(lap_row, text=time_string)
        l1.pack(side='left', padx=5)
        l2.pack(side='top')

        l1.bind("<MouseWheel>", lambda event: self.lap_canvas.yview_scroll(int(-event.delta / 120),"units"))
        l2.bind("<MouseWheel>", lambda event: self.lap_canvas.yview_scroll(int(-event.delta / 120),"units"))


    def __stopper(self, pause_button):
        pause_button.configure(text='▶', command=lambda: self.__continuer(pause_button))
        self.__pause_stopwatch()


    def __continuer(self, pause_button):
        pause_button.configure(text='⏸', command=lambda: self.__stopper(pause_button))
        self.__resume_stopwatch()


    def __start_watch(self, start_button: ctk.CTkButton, pause_button: ctk.CTkButton, rounding_button: ctk.CTkButton):
        self.__watch_mode_active(start_button, pause_button, rounding_button)
        self.start_time = time.perf_counter()
        self.elapsed_before_pause = 0
        self.__update_stopwatch()


    def __update_stopwatch(self):
        if self.stopped or self.paused:
            return

        elapsed = (
                self.elapsed_before_pause
                + time.perf_counter() - self.start_time
        )

        hours = int(elapsed // 3600)
        minutes = int(elapsed // 60) % 60
        seconds = int(elapsed) % 60
        centiseconds = int(elapsed * 100) % 100

        if len(str(hours)) > self.hours_digits:
            self.hours_digits = len(str(hours))
            kwargs = self.hours_time_label.place_info()
            kwargs['relx'] = float(kwargs['relx']) - 0.01
            kwargs['y'] = float(kwargs['y'])
            kwargs['x'] = float(kwargs['y'])
            kwargs.pop('width')
            kwargs.pop('height')
            self.hours_time_label.place(**kwargs)



        self.hours_time_label.configure(text=f"{hours:02d}")
        self.minutes_time_label.configure(text=f"{minutes:02d}")
        self.seconds_time_label.configure(text=f"{seconds:02d}")
        self.milliseconds_time_label.configure(text=f"{centiseconds:02d}")

        self.master.after(10, self.__update_stopwatch)


    def __stop_watch(self, start_button: ctk.CTkButton, pause_button: ctk.CTkButton, rounding_button: ctk.CTkButton, *removable_widgets):
        self.__watch_mode_inactive(start_button, pause_button, rounding_button, *removable_widgets)

        self.hours_time_label.configure(text='00')
        self.minutes_time_label.configure(text='00')
        self.seconds_time_label.configure(text='00')
        self.milliseconds_time_label.configure(text='00')


    def start(self):
        self.top_label_content.configure(text='Stop Watch')
        self.top_label_content.place(**self.TOP_LABEL_POS)

        clock_frame = ctk.CTkFrame(self.master)
        self.hours_time_label = ctk.CTkLabel(clock_frame, text='00', font=('Arial', 26))
        hour_min_sep = ctk.CTkLabel(clock_frame, text=':', font=('Arial', 26))
        self.minutes_time_label = ctk.CTkLabel(clock_frame, text='00', font=('Arial', 26))
        min_sec_sep = ctk.CTkLabel(clock_frame, text=':', font=('Arial', 26))
        self.seconds_time_label = ctk.CTkLabel(clock_frame, text='00', font=('Arial', 26))
        sec_millisec_sep = ctk.CTkLabel(clock_frame, text=':', font=('Arial', 26))
        self.milliseconds_time_label = ctk.CTkLabel(clock_frame, text='00', font=('Arial', 26))

        self.hours_time_label.place(relx=0.125, rely=0.5, anchor='center')
        hour_min_sep.place(relx=0.25, rely=0.5, anchor='center')
        self.minutes_time_label.place(relx=0.375, rely=0.5, anchor='center')
        min_sec_sep.place(relx=0.5, rely=0.5, anchor='center')
        self.seconds_time_label.place(relx=0.625, rely=0.5, anchor='center')
        sec_millisec_sep.place(relx=0.75, rely=0.5, anchor='center')
        self.milliseconds_time_label.place(relx=0.875, rely=0.5, anchor='center')

        hours_desc_label = ctk.CTkLabel(clock_frame, text='Hrs.', font=('Arial', 12))
        minutes_desc_label = ctk.CTkLabel(clock_frame, text='Mins.', font=('Arial', 12))
        sec_desc_label = ctk.CTkLabel(clock_frame, text='Secs.', font=('Arial', 12))
        millisec_desc_label = ctk.CTkLabel(clock_frame, text='Millisecs.', font=('Arial', 12))

        hours_desc_label.place(relx=0.135, rely=0.2, anchor='center')
        minutes_desc_label.place(relx=0.38, rely=0.2, anchor='center')
        sec_desc_label.place(relx=0.625, rely=0.2, anchor='center')
        millisec_desc_label.place(relx=0.875, rely=0.2, anchor='center')
        clock_frame.place(relx=0.5, rely=0.35, relheight=0.3, relwidth=0.4, anchor='center')

        pause_button = ctk.CTkButton(self.master, text='Pause')  # ▶ ⏸

        rounding_button = ctk.CTkButton(self.master, text='Round')

        start_button = ctk.CTkButton(self.master, text='Start', command=lambda: self.__start_watch(start_button, pause_button, rounding_button))
        start_button.place(relx=0.5, rely=0.46, relwidth=0.1, anchor='center')

        self.lap_frame = ctk.CTkFrame(self.master, fg_color='transparent')
        self.lap_frame_canvas = ctk.CTkFrame(self.lap_frame, border_width=2, border_color=self.utility.STANDARD_TEXT_COLOR)
        self.lap_canvas = ctk.CTkCanvas(self.lap_frame_canvas, background=self.utility.STANDARD_BACKGROUND_COLOR, highlightthickness=0, borderwidth=0)
        self.lap_scroll_bar = ctk.CTkScrollbar(self.lap_frame, orientation='vertical', command=self.lap_canvas.yview)
        self.lap_placeable_frame = ctk.CTkFrame(self.lap_canvas)
        self.lap_canvas.configure(yscrollcommand=self.lap_scroll_bar.set)
        window = self.lap_canvas.create_window((0, 0), window=self.lap_placeable_frame, anchor='nw')
        self.lap_placeable_frame.bind("<Configure>", lambda e: self.lap_canvas.configure(scrollregion=self.lap_canvas.bbox("all")))
        self.lap_canvas.bind('<Configure>', lambda event: self.lap_canvas.itemconfigure(window, width=event.width))
        self.lap_placeable_frame.bind("<MouseWheel>", lambda event: self.lap_canvas.yview_scroll(int(-event.delta / 120), "units"))
        self.lap_frame_canvas.place(relx=0, rely=0, relwidth=0.97, relheight=1)
        self.lap_canvas.place(relx=0.01, rely=0.05, relwidth=0.98, relheight=0.9)


        self.utility.hide_all_frames()
        self.utility.set_default_button_text_color()
        self.utility.set_default_fg_color()
        self.utility.set_default_button_text_color()




if __name__ == '__main__':
    app = ctk.CTk()
    app.geometry('700x400')
    top_label_content = ctk.CTkLabel(app, font=('Arial', 25))
    TOP_LABEL_POS = {'relx': 0.5, 'rely': 0.07, 'anchor': 'center'}
    example_frame = ctk.CTkFrame(app)

    watch = Stop_Watch(app, TOP_LABEL_POS, top_label_content, example_frame)
    watch.start()
    app.mainloop()