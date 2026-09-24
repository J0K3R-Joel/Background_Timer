import customtkinter as ctk
from timing import Timing
from constants import Constants
from ExpandingEntry import EntryExpanding
from util import Utility
from number_pickR import NumberPicker
import pywinstyles
from fixed_textbox import FixedTextbox
from soundS import SoundManager
from messagR import MessageR


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
        self.msg = MessageR(self.__class__.__name__)
        self.constants = Constants(self)
        self.utility = Utility(self.master)
        self.sound_man = SoundManager(self.master)
        self.selected_sound = self.sound_man.get_selected_sound()
        self.alarms_created = True
        self.editing_alarm_index = None
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
        name = self.timer_entry_content.get().strip() if self.timer_entry_content.get().strip() != 'Alarm' else ''
        description = self.description_textbox.get("1.0", "end-1c")

        if loops == 'invalid':
            self.utility.show_warning_text('The loop count has to be a number!', 4)
            return False

        if isinstance(loops, int) and loops < 0:
            self.utility.show_warning_text('The alarm can not have negative loops!', 4)
            return False

        self.TIME_LIST.append(time_str)
        self.NAME_LIST.append(name)
        self.DESC_LIST.append(description)
        self.SOUND_LIST.append(self.selected_sound)
        self.LOOP_LIST.append(loops)
        self.VOLUME_LIST.append(self.volume_var.get())
        self.HIDDEN_LIST.append(bool(self.hidden_var.get()))
        self.ENDLESS_LIST.append(bool(self.endless_var.get()))
        self.ENABLED_LIST.append(bool(self.enabled_var.get()))
        self.alarms_created = True

        #self.__change_all_settings()
        self.msg.info(f'Created: {time_str= } | {name= } | {description= } | {self.selected_sound= } | {loops= } | {self.volume_var.get()= } | {self.hidden_var.get()= } | {self.endless_var.get()= } | {self.enabled_var.get()= }')

        return True

    def __edit_default_lists(self, index):
        time_str = f'{self.hour_picker.get():02d}:{self.minute_picker.get():02d}'
        loops = self.utility.handle_entry_name_return('loop', 'int', 'invalid', '∞')
        name = self.timer_entry_content.get().strip()
        description = self.description_textbox.get("1.0", "end-1c")

        if loops == 'invalid':
            self.utility.show_warning_text('The loop count has to be a number!', 4)
            return False

        if isinstance(loops, int) and loops < 0:
            self.utility.show_warning_text('The alarm can not have negative loops!', 4)
            return False

        self.TIME_LIST[index] = time_str
        self.NAME_LIST[index] = name
        self.DESC_LIST[index] = description
        self.SOUND_LIST[index] = self.selected_sound
        self.LOOP_LIST[index] = loops
        self.VOLUME_LIST[index] = self.volume_var.get()
        self.HIDDEN_LIST[index] = bool(self.hidden_var.get())
        self.ENDLESS_LIST[index] = bool(self.endless_var.get())
        self.ENABLED_LIST[index] = bool(self.enabled_var.get())

        #self.__change_all_settings()
        self.msg.info(f'Edited {index=}: {time_str= } | {name= } | {description= } | {self.selected_sound= } | {loops= } | {self.volume_var.get()= } | {self.hidden_var.get()= } | {self.endless_var.get()= } | {self.enabled_var.get()= }')

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
        fg_color = self.utility.STANDARD_FG_COLOR if self.selected_sound else self.utility.complementaryColor(self.utility.STANDARD_FG_COLOR)
        text_color = self.utility.STANDARD_BUTTON_TEXT_COLOR if self.selected_sound else self.utility.complementaryColor(self.utility.STANDARD_BUTTON_TEXT_COLOR)

        self.utility.clear_scope()
        top_label_content = ctk.CTkLabel(self.master, text='Alarm', font=('Arial', 25))
        self.set_top_label_content(top_label_content)
        self.utility.draw_heading_line()
        self.build()
        self.sound_button.configure(fg_color=fg_color, text_color=text_color)


    def __open_sound_manager(self):
        self.utility.disable_all_buttons_from_scope(self._app)
        pywinstyles.set_opacity(self.master, value=0.1)
        pywinstyles.set_opacity(self.get_mode_site(), value=0.2)

        self.sound_man = SoundManager(self.master)
        self.sound_man.start(self.__close_sound_manager)

    def __close_sound_manager(self):
        self.utility.enable_all_buttons_from_scope(self._app)
        pywinstyles.set_opacity(self.master, value=1)
        pywinstyles.set_opacity(self.get_mode_site(), value=1)

        self.selected_sound = self.sound_man.get_selected_sound()
        font_style = ctk.CTkFont(weight=None) if self.selected_sound else ctk.CTkFont(weight='bold')
        selected_text = f'> {self.selected_sound}' if self.selected_sound else f'{self.selected_sound}, select one first!'
        fg_color = self.utility.STANDARD_FG_COLOR if self.selected_sound else self.utility.complementaryColor(self.utility.STANDARD_FG_COLOR)
        text_color = self.utility.STANDARD_BUTTON_TEXT_COLOR if self.selected_sound else self.utility.complementaryColor(self.utility.STANDARD_BUTTON_TEXT_COLOR)

        self.selected_volume_variable_label.configure(text=selected_text, font=font_style)
        self.sound_button.configure(fg_color=fg_color, text_color=text_color)
        self.utility.make_label_fit_in_frame(self.selected_volume_variable_label, self.volume_frame, truncate=True)


    def __show_hidden_accept_window(self, header_text: str, body_text: str, accept_text: str | None, decline_text: str):
        self.utility.disable_all_buttons_from_scope(self._app)
        pywinstyles.set_opacity(self.master, value=0.1)
        pywinstyles.set_opacity(self.get_mode_site(), value=0.2)
        choice_placement = 0.25 if accept_text else 0.5

        self._hidden_accept_window_frame = ctk.CTkFrame(self._app, fg_color='transparent', border_width=3, border_color=self.utility.complementaryColor(self.utility.STANDARD_BACKGROUND_COLOR))
        information_header_label = ctk.CTkLabel(self._hidden_accept_window_frame, text=header_text, font=('Arial', 18))
        information_text_label = ctk.CTkLabel(self._hidden_accept_window_frame, justify='left', text=body_text)

        if accept_text:
            accept_button = ctk.CTkButton(self._hidden_accept_window_frame, text=accept_text, command=self.__accept_hidden_accept_window)
            accept_button.place(relx=1-choice_placement, rely=0.9, anchor='center')
        decline_button = ctk.CTkButton(self._hidden_accept_window_frame, text=decline_text, command=self.__decline_hidden_accept_window)


        information_header_label.place(relx=0.5, rely=0.1, anchor='center')
        information_text_label.place(relx=0.02, rely=0.4, anchor='w')
        decline_button.place(relx=choice_placement, rely=0.9, anchor='center')
        self._hidden_accept_window_frame.place(relx=0.6, rely=0.5, relwidth=0.65, relheight=0.5, anchor='center')

        self.utility.make_label_fit_in_frame(information_text_label, self._hidden_accept_window_frame)
        self.utility.set_default_button_text_color(self._hidden_accept_window_frame)
        self.utility.set_default_fg_color(self._hidden_accept_window_frame)
        self.utility.set_default_button_text_color(self._hidden_accept_window_frame)

        if accept_text:
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
        show_window = self.hidden_var.get() or not self.selected_sound

        if show_window:
            if not self.selected_sound:
                self.__show_hidden_accept_window(header_text='No sound is selected!',
                                                 body_text=f'Please select a sound first by using the "{self.sound_button.cget('text')}" button!',
                                                 accept_text=None,
                                                 decline_text='I will select a sound')
            elif self.hidden_var.get():
                self.__show_hidden_accept_window(header_text='The "Hide Alarm" checkbox is selected!',
                                                 body_text='This might set all alarms in the background and you will not be able to change or stop it again. If there is one "not hidden" alarm enabled, then all Alarms are visible and can be modified. The enitre window will move to the foreground again, when the time of the nearest alarm is over. Only then you can modify the alarms again!',
                                                 accept_text="I don't need to stop/modify the alarm",
                                                 decline_text='I want to stop/modify the alarm')
        else:
            self.__save_new_alarm()


    def __cancel_new_alarm(self):
        self.__reset_alarm_page()


    def __save_new_alarm(self):
        if self.editing_alarm_index is not None:
            worked = self.__edit_default_lists(self.editing_alarm_index)

        else:
            if not self.alarms_created:
                self.__reset_all_default_lists()

            worked = self.__add_to_default_lists()
            if not worked:
                if not self.alarms_created:
                    self.__reset_all_default_lists()
                    self.__set_first_default_lists()
        if worked:
            self.editing_alarm_index = None
            self.__reset_alarm_page()

    def __create_alarm_window(self):
        self.list_frame.place_forget()
        self.utility.clear_visible_widgets()

        comp_fg_col = self.utility.complementaryColor(self.utility.STANDARD_FG_COLOR)
        comp_text_col = self.utility.complementaryColor(self.utility.STANDARD_BUTTON_TEXT_COLOR)
        self.cancel_button.configure(fg_color=comp_fg_col, text_color=comp_text_col)

        top_position_save = self.TOP_LABEL_POS.copy()
        top_position_save['rely'] = 1 - top_position_save['rely']
        top_position_save['relwidth'] = 0.4

        top_position_cancel = top_position_save.copy()
        top_position_save['relx'] = 0.75
        top_position_cancel['relx'] = 1 - top_position_save['relx']

        self.utility.draw_heading_line(relheight=0.01, rely=top_position_save['rely'] - 0.09)

        self.timer_entry_content.place(**self.TOP_LABEL_POS)
        self.cancel_button.place(**top_position_cancel)
        self.save_button.place(**top_position_save)

        self.new_alarm_window.place(relx=0.5, rely=0.5, relwidth=0.95, relheight=0.75, anchor='center')
        self.utility.make_label_fit_in_frame(self.selected_volume_variable_label, self.volume_frame, truncate=True)
        self.__setup()


    def __handle_switch(self, switch_var, index: int, row: ctk.CTkFrame):
        enabled = bool(switch_var.get())
        self.ENABLED_LIST[index] = enabled
        #self.__change_setting(self.DEFAULT_NAMES['enabled'])
        fg_color = self.utility.STANDARD_ORDERED_FRAME_COLOR if enabled else 'transparent'
        text_color = self.utility.STANDARD_FG_COLOR if enabled else self.utility.STANDARD_TEXT_COLOR
        switch_text = 'Enabled' if enabled else 'Disabled'

        row.configure(fg_color=fg_color)
        widgets = self.utility.get_widgets_from_scope([], row.winfo_children())
        for child in widgets:
            if isinstance(child, ctk.CTkSwitch):
                child.configure(text=switch_text, text_color=text_color)
            if isinstance(child, ctk.CTkLabel):
                child.configure(text_color=text_color)
            if isinstance(child, ctk.CTkFrame):
                child.configure(fg_color=fg_color)

        self.msg.info(f'Alarm {index}: enabled={enabled}')


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

    def __change_alarm(self, index):
        self.editing_alarm_index = index

        alarm = [
            self.TIME_LIST[index],
            self.NAME_LIST[index],
            self.DESC_LIST[index],
            self.SOUND_LIST[index],
            self.LOOP_LIST[index],
            self.VOLUME_LIST[index],
            self.HIDDEN_LIST[index],
            self.ENDLESS_LIST[index],
            self.ENABLED_LIST[index]
        ]

        time, name, description, sound, loops, volume, hidden, endless, enabled = alarm
        hour, minute = time.split(':')

        self.hour_picker.set(int(hour))
        self.minute_picker.set(int(minute))
        self.timer_entry_content.set(' ' * 4 + name)
        self.description_textbox.delete('1.0', 'end-1c')
        self.description_textbox.insert('1.0', description)
        self.selected_sound = sound
        self.selected_volume_variable_label.configure(text=f'> {sound}' if sound else 'No sound selected')
        self.loop_var.set(loops)
        self.volume_var.set(volume)
        self.volume_slider.set(volume)
        self.__set_volume(volume)
        self.hidden_var.set(bool(hidden))
        self.endless_var.set(bool(endless))
        self.enabled_var.set(bool(enabled))

        self.cancel_button.configure(text='✗ Cancel')
        self.save_button.configure(text='✔ Save Changes')

        self.__create_alarm_window()

    def __create_new_alarm(self):
        self.editing_alarm_index = None
        self.cancel_button.configure(text='✗ Cancel')
        self.save_button.configure(text='✔ Save')

        self.__create_alarm_window()


    def __set_volume(self, value):
        # self.volume_var is already equal to value
        self.volume_value_label.configure(text=f'Amplification: {int(self.volume_var.get())}%')

    def __time_to_minutes(self, time_string):
        hour, minute = map(int, time_string.split(':'))
        return hour * 60 + minute


    def __start_alarm(self):
        # @TODO save the alarms here again
        self.msg.info('Starting')

    def __setup(self):
        self.utility.hide_all_frames()
        self.utility.set_ordered_frame_color(self.clock_volume_frame)
        self.utility.set_ordered_frame_color(self.description_frame)
        self.utility.set_ordered_frame_color(self.settings_frame)
        self.utility.set_default_fg_color()
        self.utility.set_default_hover_color()
        self.utility.set_default_text_color(self.list_frame)
        self.utility.set_default_writable_content_color()
        self.utility.set_default_button_text_color()


    def build(self):
            rev_fg_color = self.utility.complementaryColor(self.utility.STANDARD_FG_COLOR)
            rev_text_color = self.utility.complementaryColor(self.utility.STANDARD_BUTTON_TEXT_COLOR)
            self.top_label_content.configure(text='Alarm')
            self.top_label_content.place(**self.TOP_LABEL_POS)

            self.timer_entry_content = EntryExpanding(self.master, space_count=17, start_text='Alarm     ', font=('Arial', 25))

            create_new_alarm_button = ctk.CTkButton(self.master, text='✚ Create', command=self.__create_new_alarm)
            position = self.TOP_LABEL_POS.copy()
            position['relx'] = position['rely'] * 2
            create_new_alarm_button.place(**position)

            start_button = ctk.CTkButton(self.master, text='Start', command=self.__start_alarm)
            position['relx'] = 1 - position['relx']

            no_alarm_label = ctk.CTkLabel(self.master, text='No Alarms created just yet')

            self.cancel_button = ctk.CTkButton(self.master, text='✗ Cancel', command=self.__cancel_new_alarm, font=('Arial', 20))
            self.save_button = ctk.CTkButton(self.master, text='✔ Save', command=self.__check_new_alarm, font=('Arial', 20))

            self.new_alarm_window = ctk.CTkFrame(self.master)

            self.clock_volume_frame = ctk.CTkFrame(self.new_alarm_window)
            clock_frame = ctk.CTkFrame(self.clock_volume_frame)
            time_title = ctk.CTkLabel(clock_frame, text='◷ Time', font=('Arial', 20, 'bold'))
            hour_label = ctk.CTkLabel(clock_frame, text='Hour')
            minute_label = ctk.CTkLabel(clock_frame, text='Minute')
            self.hour_picker = NumberPicker(clock_frame, 0, 23)
            self.minute_picker = NumberPicker(clock_frame, 0, 59)
            seperator = ctk.CTkLabel(clock_frame, text=':', font=('Arial', 28))

            time_title.place(relx=0.08, rely=0.07, anchor='w')
            hour_label.place(relx=0.25, rely=0.22, anchor='center')
            minute_label.place(relx=0.75, rely=0.22, anchor='center')
            self.hour_picker.place(relx=0.25, rely=0.57, anchor='center')
            self.minute_picker.place(relx=0.75, rely=0.57, anchor='center')
            seperator.place(relx=0.5, rely=0.57, anchor='center')
            clock_frame.place(relx=0.02, rely=0.05, relwidth=0.43, relheight=0.9)

            time_volume_separator = ctk.CTkFrame(self.clock_volume_frame, width=2, fg_color=self.utility.STANDARD_MODE_BORDER_COLOR)
            time_volume_separator.place(relx=0.472, rely=0.05, relheight=0.9)

            self.volume_frame = ctk.CTkFrame(self.clock_volume_frame)
            volume_title = ctk.CTkLabel(self.volume_frame, text='🔊 Volume', font=('Arial', 20, 'bold'))
            self.volume_var = ctk.IntVar(value=self.VOLUME_LIST[-1])
            self.volume_slider = ctk.CTkSlider(self.volume_frame, orientation='horizontal', scroll_step=0, from_=0, to=100, number_of_steps=100, variable=self.volume_var, command=self.__set_volume)
            self.volume_value_label = ctk.CTkLabel(self.volume_frame, text=f'Amplification: {int(self.volume_var.get())}%')
            selected_volume_title_label = ctk.CTkLabel(self.volume_frame, text=f'Selected sound:')
            font_style = ctk.CTkFont(weight=None) if self.selected_sound else ctk.CTkFont(weight='bold')
            selected_text = f'> {self.selected_sound}' if self.selected_sound else f'{self.selected_sound}, select one first!'
            fg_color = self.utility.STANDARD_FG_COLOR if self.selected_sound else rev_fg_color
            text_color = self.utility.STANDARD_BUTTON_TEXT_COLOR if self.selected_sound else rev_text_color
            self.selected_volume_variable_label = ctk.CTkLabel(self.volume_frame, text=selected_text, font=font_style)
            self.sound_button = ctk.CTkButton(self.clock_volume_frame, text='♬ Sounds', command=self.__open_sound_manager, fg_color=fg_color, text_color=text_color)
            self.volume_slider.set(self.VOLUME_LIST[-1])
            volume_title.place(relx=0.07, rely=0.07, anchor='w')
            self.volume_value_label.place(relx=0.5, rely=0.22, anchor='center')
            self.volume_slider.place(relx=0.5, rely=0.36, relwidth=0.82, anchor='center')
            selected_volume_title_label.place(relx=0.07, rely=0.75, anchor='w')
            self.selected_volume_variable_label.place(relx=0.07, rely=0.9, anchor='w')
            self.volume_frame.place(relx=0.48, rely=0.05, relwidth=0.5, relheight=0.9)
            self.sound_button.place(relx=0.72, rely=0.55, anchor='center')

            time_volume_separator.lift()
            self.clock_volume_frame.place(relx=0.724, rely=0.35, relwidth=0.5571, relheight=0.6, anchor='center')

            self.description_frame = ctk.CTkFrame(self.new_alarm_window)
            description_label = ctk.CTkLabel(self.description_frame, text='▤  Description', font=('Arial', 20, 'bold'))
            self.description_textbox = FixedTextbox(self.description_frame, 200, 110, text='No description', fg_color=self.utility.STANDARD_WRITABLE_CONTENT_COLOR, border_width=3, border_color=self.utility.STANDARD_MODE_BORDER_COLOR)

            description_label.place(relx=0.07, rely=0.12, anchor='w')
            self.description_textbox.place(relx=0.5, rely=0.55, relwidth=0.88, anchor='center')
            self.description_frame.place(relx=0.22, rely=0.35, relwidth=0.44, relheight=0.6, anchor='center')

            self.settings_frame = ctk.CTkFrame(self.new_alarm_window)
            options_title = ctk.CTkLabel(self.settings_frame, text='⚙ Options', font=('Arial', 20, 'bold'))

            options_title.place(relx=0.03, rely=0.25, anchor='w')
            options_separator = ctk.CTkFrame(self.settings_frame, height=2, fg_color=self.utility.STANDARD_MODE_BORDER_COLOR)
            options_separator.place(relx=0.03, rely=0.42, relwidth=0.94)
            settings_separator = ctk.CTkFrame(self.settings_frame, width=2, fg_color=self.utility.STANDARD_MODE_BORDER_COLOR)
            settings_separator.place(relx=0.625, rely=0.7, relheight=0.3, anchor='center')

            self.hidden_var = ctk.BooleanVar(value=bool(self.HIDDEN_LIST[-1]))
            hidden_checkbox = ctk.CTkCheckBox(self.settings_frame, text='Hidden', variable=self.hidden_var)
            self.endless_var = ctk.BooleanVar(value=bool(self.ENDLESS_LIST[-1]))
            endless_checkbox = ctk.CTkCheckBox(self.settings_frame, text='Endless', command=self.__handle_endless_checkbox, variable=self.endless_var)
            self.enabled_var = ctk.BooleanVar(value=bool(self.ENABLED_LIST[-1]))
            enabled_checkbox = ctk.CTkCheckBox(self.settings_frame, text='Enable', command=self.__handle_enable_checkbox, variable=self.enabled_var)
            enabled_checkbox.place(relx=0.03, rely=0.7, anchor='w')
            hidden_checkbox.place(relx=0.24, rely=0.7, anchor='w')
            endless_checkbox.place(relx=0.45, rely=0.7, anchor='w')

            loop_frame = ctk.CTkFrame(self.settings_frame, fg_color='transparent')
            loop_label = ctk.CTkLabel(loop_frame, text='Loop Count:')
            loop_start_text = '∞' if self.ENDLESS_LIST[-1] else self.LOOP_LIST[-1]
            loop_start_text = 3 if self.LOOP_LIST[-1] == '∞' and not self.ENDLESS_LIST[-1] else loop_start_text
            self.loop_var = ctk.StringVar(value=loop_start_text)
            loop_start_state = ctk.DISABLED if self.ENDLESS_LIST[-1] else ctk.NORMAL
            loop_entry = ctk.CTkEntry(loop_frame, textvariable=self.loop_var)
            loop_entry.configure(state=loop_start_state)
            loop_separator = ctk.CTkFrame(self.settings_frame, width=2, fg_color=self.utility.STANDARD_MODE_BORDER_COLOR)
            loop_separator.place(relx=0.65, rely=0.43, relheight=0.40, relwidth=0.002)
            loop_label.place(relx=0.1, rely=0.5, anchor='w')
            loop_entry.place(relx=0.75, rely=0.5, relwidth=0.5, anchor='center')
            loop_frame.place(relx=0.805, rely=0.7, relheight=0.5, anchor='center')

            settings_separator.lift()
            options_separator.lift()
            self.settings_frame.place(relx=0.5, rely=0.8, relwidth=1, relheight=0.27, anchor='center')

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

                self.alarms = list(zip(
                    self.TIME_LIST,
                    self.NAME_LIST,
                    self.DESC_LIST,
                    self.SOUND_LIST,
                    self.LOOP_LIST,
                    self.VOLUME_LIST,
                    self.HIDDEN_LIST,
                    self.ENDLESS_LIST,
                    self.ENABLED_LIST
                ))

                indexed_alarms = list(enumerate(self.alarms))

                indexed_alarms.sort(key=lambda item: self.__time_to_minutes(item[1][0]))

                for alarm_index, alarm in indexed_alarms:
                    time, name, desc, sound, loop, volume, hidden, endless, enabled = alarm

                    if not self.list_scroll_bar.winfo_ismapped():
                        self.list_scroll_bar.place(relx=0.97, rely=0, relwidth=0.03, relheight=1)
                        start_button.place(**position)
                        create_new_alarm_button.configure(fg_color=rev_fg_color, text_color=rev_text_color)


                    switch_var = ctk.BooleanVar(value=bool(enabled))
                    switch_fg_color = self.utility.STANDARD_ORDERED_FRAME_COLOR if switch_var.get() else 'transparent'
                    text_color = self.utility.STANDARD_FG_COLOR if switch_var.get() else self.utility.STANDARD_TEXT_COLOR
                    switch_text = 'Enabled' if switch_var.get() else 'Disabled'

                    list_row = ctk.CTkFrame(self.list_placeable_frame, border_width=5, corner_radius=20, fg_color=switch_fg_color)
                    list_row.pack(fill='x', pady=5, ipady=30)
                    enabled_frame = ctk.CTkFrame(list_row, fg_color=switch_fg_color)

                    hour, minute = map(int, time.split(':'))
                    period = 'AM' if hour < 12 else 'PM'
                    hour = hour % 12 or 12

                    time_label = ctk.CTkLabel(list_row, text=f'{hour}:{minute:02d} {period}', text_color=text_color)
                    name_label = ctk.CTkLabel(list_row, text=name, text_color=text_color)
                    enabled_switch = ctk.CTkSwitch(
                        enabled_frame,
                        text=switch_text,
                        text_color=text_color,
                        variable=switch_var,
                        command=lambda var=switch_var, index=alarm_index, row=list_row: self.__handle_switch(var, index, row)
                    )


                    time_label.pack(side='left', padx=10, anchor='center')
                    name_label.place(relx=0.15, rely=0.5, anchor='w')
                    enabled_frame.place(relx=0.875, rely=0.5, relheight=0.8, relwidth=0.2, anchor='center')
                    enabled_switch.place(relx=0.5, rely=0.5, anchor='center')


                    while not name_label.winfo_ismapped():
                        self.master.update_idletasks()

                    name_str: str = name
                    distance = name_label.winfo_x() - time_label.winfo_x() - time_label.winfo_width()

                    while True:
                        if name_label.winfo_width() + name_label.winfo_x() < enabled_frame.winfo_x() - distance:
                            break
                        name_str = name_str[0:len(name_str)-1]
                        name_label.configure(text=name_str + '...')
                        self.master.update_idletasks()


                    time_label.bind('<MouseWheel>', lambda event: self.list_canvas.yview_scroll(int(-event.delta / 120), 'units'))
                    name_label.bind('<MouseWheel>', lambda event: self.list_canvas.yview_scroll(int(-event.delta / 120), 'units'))
                    list_row.bind('<MouseWheel>', lambda event: self.list_canvas.yview_scroll(int(-event.delta / 120), 'units'))
                    enabled_frame.bind('<MouseWheel>', lambda event: self.list_canvas.yview_scroll(int(-event.delta / 120), 'units'))

                    list_row.bind('<Button-1>', lambda event, index=alarm_index: self.__change_alarm(index))
                    time_label.bind('<Button-1>', lambda event, index=alarm_index: self.__change_alarm(index))
                    name_label.bind('<Button-1>', lambda event, index=alarm_index: self.__change_alarm(index))

                    list_row.configure(cursor='hand2')
                    time_label.configure(cursor='hand2')
                    name_label.configure(cursor='hand2')

            else:
                no_alarm_label.place(relx=0.5, rely=0.5, anchor='center')
                no_alarm_label.lift()

            self.utility.create_entry_name(loop_entry, 'loop')
            self.__setup()