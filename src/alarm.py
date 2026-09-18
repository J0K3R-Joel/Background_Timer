import customtkinter as ctk
from timing import Timing
from constants import Constants
from ExpandingEntry import EntryExpanding
from util import Utility
from number_pickR import NumberPicker
import pywinstyles
from fixed_textbox import FixedTextbox


class Alarm(Timing):
    DEFAULT_NAMES = {
        'time': 'todays_time',
        'name': 'alarm_name',
        'desc': 'description',
        'sound': 'alarm_sound',
        'loop': 'loop_count',
        'volume': 'alarm_volume',
        'hidden': 'alarm_hidden',
        'endless': 'endless_loop',
        'enabled': 'timer_active'
    }

    DEFAULT_CONSTANTS = {
        DEFAULT_NAMES['time']: list(),
        DEFAULT_NAMES['name']: list(),
        DEFAULT_NAMES['desc']: list(),
        DEFAULT_NAMES['sound']: list(),
        DEFAULT_NAMES['loop']: list(),
        DEFAULT_NAMES['volume']: list(),
        DEFAULT_NAMES['hidden']: list(),
        DEFAULT_NAMES['endless']: list(),
        DEFAULT_NAMES['enabled']: list()
    }

    def __init__(self, *args, app):
        Timing.__init__(self, *args)
        self._app = app
        self.constants = Constants(self)
        self.utility = Utility(self.master)
        self.alarms_created = True
        self.__load_config_files()

    def __load_config_files(self):
        dd = self.constants.get_default_dict()
        self.TIME_LIST: list = dd[self.DEFAULT_NAMES['time']]
        self.NAME_LIST = dd[self.DEFAULT_NAMES['name']]
        self.DESC_LIST = dd[self.DEFAULT_NAMES['desc']]
        self.SOUND_LIST = dd[self.DEFAULT_NAMES['sound']]
        self.LOOP_LIST = dd[self.DEFAULT_NAMES['loop']]
        self.VOLUME_LIST = dd[self.DEFAULT_NAMES['volume']]
        self.HIDDEN_LIST = dd[self.DEFAULT_NAMES['hidden']]
        self.ENDLESS_LIST = dd[self.DEFAULT_NAMES['endless']]
        self.ENABLED_LIST = dd[self.DEFAULT_NAMES['enabled']]

        if not self.TIME_LIST:
            self.__set_first_default_lists()

    def __reset_all_default_lists(self):
        self.TIME_LIST = list()
        self.NAME_LIST = list()
        self.DESC_LIST = list()
        self.SOUND_LIST = list()
        self.LOOP_LIST = list()
        self.VOLUME_LIST = list()
        self.HIDDEN_LIST = list()
        self.ENDLESS_LIST = list()
        self.ENABLED_LIST = list()

    def __set_first_default_lists(self):
        self.alarms_created = False
        self.TIME_LIST.append('12:00')
        self.NAME_LIST.append('Alarm')
        self.DESC_LIST.append('Description for the Alarm')
        # self.SOUND_LIST.append()
        self.LOOP_LIST.append(3)
        self.VOLUME_LIST.append(75)
        self.HIDDEN_LIST.append(True)
        self.ENDLESS_LIST.append(False)
        self.ENABLED_LIST.append(True)

    def __add_to_default_lists(self):
        time_str = f'{self.hour_picker.get():02d}:{self.minute_picker.get():02d}'
        loops = self.utility.handle_entry_name_return('loop', 'int', 'invalid', '∞')
        name = self.timer_entry_content.get().strip()
        description = self.description_textbox.get("1.0", "end-1c")

        if loops == 'invalid':
            self.utility.show_warning_text('The loop count has to be a number!', 4)
            return False

        if isinstance(loops, int) and not loops >= 0:
            self.utility.show_warning_text('The alarm can not have negative loops!', 4)
            return False

        self.TIME_LIST.append(time_str)
        self.NAME_LIST.append(name)
        self.DESC_LIST.append(description)
        self.LOOP_LIST.append(loops)
        self.VOLUME_LIST.append(self.volume_var.get())
        self.HIDDEN_LIST.append(self.hidden_var.get())
        self.ENDLESS_LIST.append(self.endless_var.get())
        self.ENABLED_LIST.append(self.enabled_var.get())
        self.alarms_created = True
        return True

    def __change_all_settings(self):
        for short, long in self.DEFAULT_NAMES.items():
            self.__change_setting(long)

    def __change_setting(self, setting_name: str):
        if setting_name == self.DEFAULT_NAMES.get('time'):
            new_value = self.TIME_LIST
        elif setting_name == self.DEFAULT_NAMES.get('name'):
            new_value = self.NAME_LIST
        elif setting_name == self.DEFAULT_NAMES.get('desc'):
            new_value = self.DESC_LIST
        elif setting_name == self.DEFAULT_NAMES.get('sound'):
            new_value = self.SOUND_LIST
        elif setting_name == self.DEFAULT_NAMES.get('loop'):
            new_value = self.LOOP_LIST
        elif setting_name == self.DEFAULT_NAMES.get('volume'):
            new_value = self.VOLUME_LIST
        elif setting_name == self.DEFAULT_NAMES.get('hidden'):
            new_value = self.HIDDEN_LIST
        elif setting_name == self.DEFAULT_NAMES.get('endless'):
            new_value = self.ENDLESS_LIST
        elif setting_name == self.DEFAULT_NAMES.get('enabled'):
            new_value = self.ENABLED_LIST
        else:
            raise NotImplementedError(setting_name, ' does not exist')

        self.constants.change_element(setting_name, new_value)

    def __reset_alarm_page(self):
        self.utility.clear_scope()
        top_label_content = ctk.CTkLabel(self.master, text='Alarm', font=('Arial', 25))
        self.set_top_label_content(top_label_content)
        self.utility.draw_heading_line()
        self.build()


    def __show_hidden_accept_window(self):
        self.utility.disable_all_buttons_from_scope(self._app)
        pywinstyles.set_opacity(self.master, value=0.1)
        pywinstyles.set_opacity(self.get_mode_site(), value=0.2)

        self._hidden_accept_window_frame = ctk.CTkFrame(self._app, fg_color='transparent', border_width=3, border_color=self.utility.complementaryColor(self.utility.STANDARD_BACKGROUND_COLOR))
        information_header_label = ctk.CTkLabel(self._hidden_accept_window_frame, text='The "Hide Timer" checkbox is selected!', font=('Arial', 18))
        information_text_label = ctk.CTkLabel(self._hidden_accept_window_frame, justify='left', text='This will set the timer in the background and you will not be able to change or stop it again. This window will move to the foreground again, when the time is over. Only then you can modify the timer again!')
        accept_button = ctk.CTkButton(self._hidden_accept_window_frame, text="I don't need to stop/modify the timer", command=self.__accept_hidden_accept_window)
        decline_button = ctk.CTkButton(self._hidden_accept_window_frame, text="I want to stop/modify the timer", command=self.__decline_hidden_accept_window)

        choice_placement = 0.25

        information_header_label.place(relx=0.5, rely=0.1, anchor='center')
        information_text_label.place(relx=0.02, rely=0.4, anchor='w')
        accept_button.place(relx=1-choice_placement, rely=0.9, anchor='center')
        decline_button.place(relx=choice_placement, rely=0.9, anchor='center')
        self._hidden_accept_window_frame.place(relx=0.6, rely=0.5, relwidth=0.65, relheight=0.5, anchor='center')

        self.utility.make_label_fit_in_frame(information_text_label, self._hidden_accept_window_frame)
        self.utility.set_default_button_text_color(self._hidden_accept_window_frame)
        self.utility.set_default_fg_color(self._hidden_accept_window_frame)
        self.utility.set_default_button_text_color(self._hidden_accept_window_frame)

        width_diff = (accept_button.winfo_width() - decline_button.winfo_width())
        accept_button.place(relx=1-choice_placement-(width_diff/1000/2))  # /1000 to make it size-wise appropiate, /2 because its centered and doesnt need to go all the way to the left (it only needs to go half way)

        fg_color = self.utility.complementaryColor(self.utility.STANDARD_FG_COLOR)
        text_color = self.utility.complementaryColor(self.utility.STANDARD_BUTTON_TEXT_COLOR)
        decline_button.configure(fg_color=fg_color, text_color=text_color)

    def __accept_hidden_accept_window(self):
        self._hidden_accept_window_frame.destroy()
        self.utility.enable_all_buttons_from_scope(self._app)
        pywinstyles.set_opacity(self.master, value=1)
        pywinstyles.set_opacity(self.get_mode_site(), value=1)
        self.__save_new_alarm()


    def __decline_hidden_accept_window(self):
        self._hidden_accept_window_frame.destroy()
        self.utility.enable_all_buttons_from_scope(self._app)
        pywinstyles.set_opacity(self.master, value=1)
        pywinstyles.set_opacity(self.get_mode_site(), value=1)

    def __check_new_alarm(self):
        if self.hidden_var.get():
            self.__show_hidden_accept_window()
        else:
            self.__save_new_alarm()


    def __cancel_new_alarm(self):
        self.__reset_alarm_page()

    def __save_new_alarm(self):
        if not self.alarms_created:
            self.__reset_all_default_lists()

        worked = self.__add_to_default_lists()
        if not worked:
            if not self.alarms_created:
                self.__reset_all_default_lists()
                self.__set_first_default_lists()
        else:
            self.__reset_alarm_page()

    def __create_alarm_window(self):
        self.utility.clear_visible_widgets()
        self.utility.draw_heading_line(fg_color=self.utility.STANDARD_MODE_BORDER_COLOR, relheight=0.01)

        comp_fg_col = self.utility.complementaryColor(self.utility.STANDARD_FG_COLOR)
        comp_text_col = self.utility.complementaryColor(self.utility.STANDARD_BUTTON_TEXT_COLOR)
        self.cancel_button.configure(fg_color=comp_fg_col, text_color=comp_text_col)

        top_position_save = self.TOP_LABEL_POS.copy()
        top_position_save['rely'] = 1 - top_position_save['rely']
        top_position_cancel = top_position_save.copy()
        top_position_save['relx'] = top_position_save['rely'] - (1 - top_position_save['rely'])
        top_position_cancel['relx'] = 1 - top_position_save['relx']

        self.utility.draw_heading_line(relheight=0.01, rely=top_position_save['rely']-0.09)

        self.timer_entry_content.place(**self.TOP_LABEL_POS)
        self.cancel_button.place(**top_position_cancel)
        self.save_button.place(**top_position_save)
        self.new_alarm_window.place(relx=0.5, rely=0.5, relwidth=0.95, relheight=0.75, anchor='center')
        self.volume_frame.place(relx=0.95, rely=0.45, relheight=0.53, relwidth=0.2, anchor='center')
        self.description_frame.place(relx=0.2, rely=0.345, relheight=0.4, anchor='center')

    def __handle_switch(self, switch_var):
        print(switch_var.get())

    def __handle_enable_checkbox(self):
        print(self.enabled_var.get())

    def __handle_endless_checkbox(self):
        endless = True if self.endless_var.get() else False
        loop_entry = self.utility.get_entry_by_name('loop')
        if endless:
            loop_entry.set('∞')
            loop_entry.configure(state=ctk.DISABLED)
        else:
            loop_entry.configure(state=ctk.NORMAL)
            amount = 3 if self.loop_var.get() == '∞' else self.LOOP_LIST[-1]
            loop_entry.set(f'{amount}')

    def __set_volume(self, value):
        # self.volume_var is already equal to value
        self.volume_value_label.configure(text=f'{int(self.volume_var.get())}%')

    def __time_to_minutes(self, time_string):
        hour, minute = map(int, time_string.split(':'))
        return hour * 60 + minute

    def build(self):
            self.top_label_content.configure(text='Alarm')
            self.top_label_content.place(**self.TOP_LABEL_POS)

            self.timer_entry_content = EntryExpanding(self.master, space_count=17, start_text='Alarm     ', font=('Arial', 25))

            create_new_alarm_button = ctk.CTkButton(self.master, text='✚ Create', command=self.__create_alarm_window)
            position = self.TOP_LABEL_POS.copy()
            position['relx'] = position['rely'] * 2
            create_new_alarm_button.place(**position)

            no_alarm_label = ctk.CTkLabel(self.master, text='No Alarms created just yet')

            self.cancel_button = ctk.CTkButton(self.master, text='✗ Cancel', command=self.__cancel_new_alarm)
            self.save_button = ctk.CTkButton(self.master, text='✔ Save', command=self.__check_new_alarm)

            self.new_alarm_window = ctk.CTkFrame(self.master)

            clock_frame = ctk.CTkFrame(self.new_alarm_window)
            hour_label = ctk.CTkLabel(clock_frame, text='Hour')
            minute_label = ctk.CTkLabel(clock_frame, text='Minute')
            self.hour_picker = NumberPicker(clock_frame, 0, 23)
            self.minute_picker = NumberPicker(clock_frame, 0, 59)
            seperator = ctk.CTkLabel(clock_frame, text=':', font=("Arial", 28))
            self.hour_picker.place(relx=0.3, rely=0.5, anchor='center')
            hour_label.place(relx=0.3, rely=0.2, anchor='center')
            self.minute_picker.place(relx=0.7, rely=0.5, anchor='center')
            minute_label.place(relx=0.7, rely=0.2, anchor='center')
            seperator.place(relx=0.5, rely=0.5, anchor='center')
            clock_frame.place(relx=0.5, rely=0.3, anchor='center')

            self.description_frame = ctk.CTkFrame(self.master)
            description_label = ctk.CTkLabel(self.description_frame, text='Description')
            self.description_textbox = FixedTextbox(self.description_frame, 200, 130, text='No description', fg_color=self.utility.STANDARD_WRITABLE_CONTENT_COLOR, border_width=3, border_color=self.utility.STANDARD_MODE_BORDER_COLOR)

            description_label.place(relx=0.5, rely=0.15, anchor='center')
            self.description_textbox.place(relx=0.5, rely=0.6, anchor='center')

            self.volume_frame = ctk.CTkFrame(self.master)
            volume_label = ctk.CTkLabel(self.volume_frame, text='Volume')
            self.volume_var = ctk.IntVar(value=self.VOLUME_LIST[-1])
            volume_slider = ctk.CTkSlider(self.volume_frame, orientation='vertical', scroll_step=0, from_=0, to=100, number_of_steps=100, variable=self.volume_var, command=self.__set_volume)
            self.volume_value_label = ctk.CTkLabel(self.volume_frame, text=f'{int(self.volume_var.get())}%')
            volume_slider.set(self.VOLUME_LIST[-1])
            volume_label.place(relx=0.2, rely=0.45, anchor='center')
            volume_slider.place(relx=0.5, rely=0.5, relheight=0.8, anchor='center')
            self.volume_value_label.place(relx=0.5, rely=0.03, anchor='center')

            settings_frame = ctk.CTkFrame(self.new_alarm_window)
            'sound'
            loop_frame = ctk.CTkFrame(settings_frame)
            loop_label = ctk.CTkLabel(loop_frame, text='Loop Count:')
            loop_start_text = '∞' if self.ENDLESS_LIST[-1] else self.LOOP_LIST[-1]
            loop_start_text = 3 if self.LOOP_LIST[-1] == '∞' and not self.ENDLESS_LIST[-1] else loop_start_text  # standard amount if it shouldnt be endless, but the last loop value was endless
            self.loop_var = ctk.StringVar(value=loop_start_text)
            loop_start_state = ctk.DISABLED if self.ENDLESS_LIST[-1] else ctk.NORMAL
            loop_entry = ctk.CTkEntry(loop_frame, textvariable=self.loop_var)
            loop_entry.configure(state=loop_start_state)
            self.hidden_var = ctk.StringVar(value='enabled') if self.HIDDEN_LIST[-1] else ctk.StringVar(value='')
            hidden_checkbox = ctk.CTkCheckBox(settings_frame, text='Hidden', variable=self.hidden_var, onvalue='enabled', offvalue='')
            self.endless_var = ctk.StringVar(value='enabled') if self.ENDLESS_LIST[-1] else ctk.StringVar(value='')
            endless_checkbox = ctk.CTkCheckBox(settings_frame, text='Endless', command=self.__handle_endless_checkbox, variable=self.endless_var, onvalue='enabled', offvalue='')
            self.enabled_var = ctk.StringVar(value='enabled') if self.HIDDEN_LIST[-1] else ctk.StringVar(value='')
            enabled_checkbox = ctk.CTkCheckBox(settings_frame, text='Enable', command=self.__handle_enable_checkbox, variable=self.enabled_var, onvalue='enabled', offvalue='')
            enabled_checkbox.place(relx=0.1, rely=0.2, anchor='center')
            endless_checkbox.place(relx=0.1, rely=0.7, anchor='center')
            hidden_checkbox.place(relx=0.4, rely=0.2, anchor='center')
            loop_label.place(relx=0, relwidth=0.4)
            loop_entry.place(relx=0.4, relwidth=0.6)
            loop_frame.place(relx=0.8, rely=0.7, relheight=0.4, anchor='center')
            settings_frame.place(relx=0.5, rely=0.8, relwidth=0.95, relheight=0.25, anchor='center')

            self.list_frame = ctk.CTkFrame(self.master)
            self.list_frame_canvas = ctk.CTkFrame(self.list_frame)
            self.list_canvas = ctk.CTkCanvas(self.list_frame_canvas, background=self.utility.STANDARD_BACKGROUND_COLOR, highlightthickness=0, borderwidth=0)
            self.list_scroll_bar = ctk.CTkScrollbar(self.list_frame, orientation='vertical', command=self.list_canvas.yview)
            self.list_placeable_frame = ctk.CTkFrame(self.list_canvas)
            self.list_canvas.configure(yscrollcommand=self.list_scroll_bar.set)
            window = self.list_canvas.create_window((0, 0), window=self.list_placeable_frame, anchor='nw')
            self.list_placeable_frame.bind("<Configure>", lambda e: self.list_canvas.configure(scrollregion=self.list_canvas.bbox("all")))
            self.list_canvas.bind('<Configure>', lambda event: self.list_canvas.itemconfigure(window, width=event.width))
            self.list_placeable_frame.bind("<MouseWheel>", lambda event: self.list_canvas.yview_scroll(int(-event.delta / 120), "units"))
            self.list_frame_canvas.place(relx=0, rely=0, relwidth=0.97, relheight=1)
            self.list_canvas.place(relx=0.01, rely=0.05, relwidth=0.98, relheight=0.9)
            self.list_frame.place(relx=0.02, rely=0.2, relwidth=0.96, relheight=0.75)

            if self.alarms_created:
                if no_alarm_label.winfo_ismapped():
                    no_alarm_label.place_forget()

                alarms = list(zip(self.TIME_LIST,
                                    self.NAME_LIST,
                                    self.DESC_LIST,
                                    self.SOUND_LIST,
                                    self.LOOP_LIST,
                                    self.VOLUME_LIST,
                                    self.HIDDEN_LIST,
                                    self.ENDLESS_LIST,
                                    self.ENABLED_LIST))

                alarms.sort(key=lambda alarm: self.__time_to_minutes(alarm[0]))

                for alarm in alarms:
                    time, name, desc, sound, loop, volume, hidden, endless, enabled = alarm

                    if not self.list_scroll_bar.winfo_ismapped():
                        self.list_scroll_bar.place(relx=0.97, rely=0, relwidth=0.03, relheight=1)


                    enabled_value = 'enabled' if enabled else 'disabled'
                    switch_var = ctk.StringVar(value=enabled_value)

                    list_row = ctk.CTkFrame(self.list_placeable_frame, border_width=5, corner_radius=20)
                    list_row.pack(fill='x', pady=5, ipady=30)

                    hour, minute = map(int, time.split(':'))
                    period = 'AM' if hour < 12 else 'PM'
                    hour = hour % 12 or 12

                    time_label = ctk.CTkLabel(list_row, text=f'{hour}:{minute:02d} {period}')
                    name_label = ctk.CTkLabel(list_row, text=name)
                    enabled_switch = ctk.CTkSwitch(list_row,
                                                   text='Enabled',
                                                   variable=switch_var,
                                                   onvalue='enabled',
                                                   offvalue='disabled',
                                                   command=lambda var=switch_var: self.__handle_switch(var))


                    time_label.pack(side='left', padx=10, anchor='center')
                    name_label.place(relx=0.15, rely=0.5, anchor='w')
                    enabled_switch.place(relx=0.9, rely=0.5, anchor='center')


                    while not name_label.winfo_ismapped():
                        self.master.update_idletasks()

                    name_str: str = name
                    distance = name_label.winfo_x() - time_label.winfo_x() - time_label.winfo_width()

                    while True:
                        if name_label.winfo_width() + name_label.winfo_x() < enabled_switch.winfo_x() - distance:
                            break
                        name_str = name_str[0:len(name_str)-1]
                        name_label.configure(text=name_str + '...')
                        self.master.update_idletasks()


                    time_label.bind("<MouseWheel>", lambda event: self.list_canvas.yview_scroll(int(-event.delta / 120), "units"))
                    name_label.bind("<MouseWheel>", lambda event: self.list_canvas.yview_scroll(int(-event.delta / 120), "units"))
                    list_row.bind("<MouseWheel>", lambda event: self.list_canvas.yview_scroll(int(-event.delta / 120), "units"))

            else:
                no_alarm_label.place(relx=0.5, rely=0.5, anchor='center')
                no_alarm_label.lift()

            self.utility.create_entry_name(loop_entry, 'loop')

            self.utility.hide_all_frames()
            self.utility.set_default_button_text_color()
            self.utility.set_default_fg_color()
            self.utility.set_default_text_color()
            self.utility.set_default_writable_content_color()
            self.utility.set_default_button_text_color()


