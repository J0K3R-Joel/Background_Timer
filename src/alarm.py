import _tkinter
import customtkinter as ctk
import pywinstyles
import pygame.mixer as mixer
from datetime import datetime, timedelta
from timing import Timing
from constants import Constants
from ExpandingEntry import EntryExpanding
from util import Utility
from number_pickR import NumberPicker
from fixed_textbox import FixedTextbox
from soundS import SoundManager
from messagR import MessageR


class Alarm(Timing):
    DEFAULT_NAMES = {
        'time': 'todays_time',
        'name': 'alarm_name',
        's_name': 'shortened_alarm_name',
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
        DEFAULT_NAMES['s_name']: list(),
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
        self.utility = Utility(self.master, self.build)
        self.sound_man = SoundManager(self.master)
        self.selected_sound = self.sound_man.get_selected_sound()
        self.invalid_sound_exists = False
        self.alarms_created = True
        self.editing_alarm_index = None
        self.ALARM_RUNNING = False
        self._alarm_after_id = None
        self._countdown_after_id = None
        self._start_button = None
        self._next_alarm_label = None
        self._fired_alarms = set()
        self._alarm_channels = {}
        self._alarm_sounds = {}
        self._last_alarm_check = None
        self._alarm_check_after_id = None
        self._window_hidden_by_alarm = False
        self._foreground_alarms_pending_disable = set()
        self.__load_config_files()


    def __load_config_files(self):
        dd = self.constants.get_default_dict()
        self.TIME_LIST: list = dd[self.DEFAULT_NAMES['time']]
        self.NAME_LIST = dd[self.DEFAULT_NAMES['name']]
        self.SHORTENED_NAME_LIST = dd[self.DEFAULT_NAMES['s_name']]
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
        self.SHORTENED_NAME_LIST = list()
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
        self.SHORTENED_NAME_LIST.append(self.NAME_LIST[0])
        self.DESC_LIST.append('Description for the Alarm')
        self.SOUND_LIST.append(None)
        self.LOOP_LIST.append(3)
        self.VOLUME_LIST.append(75)
        self.HIDDEN_LIST.append(True)
        self.ENDLESS_LIST.append(False)
        self.ENABLED_LIST.append(True)


    def __add_to_default_lists(self):
        max_name_len = 100
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

        if len(name) > max_name_len:
            self.utility.show_warning_text(f'The name can only have {max_name_len} chars. Currently: {len(name)}', 5)
            return False

        if not self.sound_man.sound_exists(self.selected_sound):
            self.utility.show_warning_text(f'The song {self.selected_sound} does not exist anymore. Add a new one!', 4)
            return False

        self.TIME_LIST.append(time_str)
        self.NAME_LIST.append(name)
        self.SHORTENED_NAME_LIST.append(name)
        self.DESC_LIST.append(description)
        self.SOUND_LIST.append(self.selected_sound)
        self.LOOP_LIST.append(loops)
        self.VOLUME_LIST.append(self.volume_var.get())
        self.HIDDEN_LIST.append(bool(self.hidden_var.get()))
        self.ENDLESS_LIST.append(bool(self.endless_var.get()))
        self.ENABLED_LIST.append(bool(self.enabled_var.get()))
        self.alarms_created = True

        self.__change_all_settings()
        if self.ALARM_RUNNING:
            self.__refresh_running_alarm()

        self.msg.info(f'Created: {time_str= } | {name= } | {description= } | {self.selected_sound= } | {loops= } | {self.volume_var.get()= } | {self.hidden_var.get()= } | {self.endless_var.get()= } | {self.enabled_var.get()= }')
        return True


    def __edit_default_lists(self, index):
        max_name_len = 100
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

        if len(name) > max_name_len:
            self.utility.show_warning_text(f'The name can only have {max_name_len} chars. Currently: {len(name)}', 4)
            return False

        if not self.sound_man.sound_exists(self.selected_sound):
            self.utility.show_warning_text(f'The song {self.selected_sound} does not exist anymore. Add a new one!', 4)
            return False

        self.TIME_LIST[index] = time_str
        self.NAME_LIST[index] = name
        self.SHORTENED_NAME_LIST[index] = name
        self.DESC_LIST[index] = description
        self.SOUND_LIST[index] = self.selected_sound
        self.LOOP_LIST[index] = loops
        self.VOLUME_LIST[index] = self.volume_var.get()
        self.HIDDEN_LIST[index] = bool(self.hidden_var.get())
        self.ENDLESS_LIST[index] = bool(self.endless_var.get())
        self.ENABLED_LIST[index] = bool(self.enabled_var.get())

        self.__change_all_settings()
        if self.ALARM_RUNNING:
            self.__refresh_running_alarm()

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
        elif setting_name == self.DEFAULT_NAMES.get('s_name'):
            new_value = self.SHORTENED_NAME_LIST
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


    def __set_sound_states(self, sound = None):
        self.selected_sound = sound if sound else self.sound_man.get_selected_sound()
        font_style = ctk.CTkFont(weight=None) if self.selected_sound else ctk.CTkFont(weight='bold')
        selected_text = f'> {self.selected_sound}' if self.selected_sound else f'None, select one first!'
        fg_color = self.utility.STANDARD_FG_COLOR if self.selected_sound else self.utility.complementaryColor(self.utility.STANDARD_FG_COLOR)
        text_color = self.utility.STANDARD_BUTTON_TEXT_COLOR if self.selected_sound else self.utility.complementaryColor(self.utility.STANDARD_BUTTON_TEXT_COLOR)

        self.selected_volume_variable_label.configure(text=selected_text, font=font_style)
        self.sound_button.configure(fg_color=fg_color, text_color=text_color)
        self.utility.make_label_fit_in_frame(self.selected_volume_variable_label, self.volume_frame, truncate=True)
        self.utility.set_default_hover_color(self.clock_volume_frame)



    def __close_sound_manager(self):
        self.utility.enable_all_buttons_from_scope(self._app)
        pywinstyles.set_opacity(self.master, value=1)
        pywinstyles.set_opacity(self.get_mode_site(), value=1)
        remove_fg_color = self.utility.adjust_color(self.cancel_button.cget('fg_color'), 50, self.utility.STANDARD_FG_COLOR)
        remove_text_color = self.utility.complementaryColor(remove_fg_color)

        self.__set_sound_states()
        self.utility.set_default_fg_color()
        self.delete_button.configure(fg_color=remove_fg_color, text_color=remove_text_color, hover_color=self.utility.adjust_color(remove_fg_color, 50))

        self.utility.set_default_hover_color()


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

        if accept_text:
            width_diff = (accept_button.winfo_width() - decline_button.winfo_width())
            accept_button.place(relx=1-choice_placement-(width_diff/1000/2))  # /1000 to make it size-wise appropiate, /2 because its centered and doesnt need to go all the way to the left (it only needs to go half way)

            fg_color = self.utility.complementaryColor(self.utility.STANDARD_FG_COLOR)
            text_color = self.utility.complementaryColor(self.utility.STANDARD_BUTTON_TEXT_COLOR)
            decline_button.configure(fg_color=fg_color, text_color=text_color)
        self.utility.set_default_hover_color(self._hidden_accept_window_frame)


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


    def __get_due_alarms(self):
        now = datetime.now()
        previous_check = self._last_alarm_check
        if previous_check is None:
            return []

        due_alarms = []
        today = now.date()

        for index, time_string in enumerate(self.TIME_LIST):
            if not bool(self.ENABLED_LIST[index]):
                continue

            hour, minute = map(int, time_string.split(':'))
            alarm_datetime = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            trigger_id = (index, today)

            if previous_check < alarm_datetime <= now and trigger_id not in self._fired_alarms:
                due_alarms.append({
                    'index': index,
                    'datetime': alarm_datetime,
                    'time': time_string,
                    'hidden': bool(self.HIDDEN_LIST[index]),
                    'name': self.NAME_LIST[index],
                    'sound': self.SOUND_LIST[index],
                    'loops': self.LOOP_LIST[index],
                    'volume': self.VOLUME_LIST[index],
                    'endless': bool(self.ENDLESS_LIST[index])
                })

        return due_alarms

    def __check_running_alarm(self):
        if not self.ALARM_RUNNING:
            return

        for alarm in self.__get_due_alarms():
            self.__trigger_alarm(alarm)

        self._last_alarm_check = datetime.now()
        self.__update_window_state()
        self.__update_next_alarm_label()
        self._alarm_check_after_id = self.master.after(500, self.__check_running_alarm)


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

            if self.ALARM_RUNNING:
                if self._alarm_after_id is not None:
                    self.master.after_cancel(self._alarm_after_id)
                    self._alarm_after_id = None

                next_alarm = self.__get_next_enabled_alarm()

                if next_alarm is None:
                    self.__stop_alarm()
                else:
                    self.__update_window_state()
                    self.__schedule_next_alarm()


    def __delete_alarm(self):
        if self.editing_alarm_index is None:
            return

        index = self.editing_alarm_index
        self._foreground_alarms_pending_disable.discard(index)
        channel = self._alarm_channels.pop(index, None)
        self._alarm_sounds.pop(index, None)
        if channel is not None:
            try:
                channel.stop()
            except Exception:
                pass

        self.TIME_LIST.pop(index)
        self.NAME_LIST.pop(index)
        self.DESC_LIST.pop(index)
        self.SOUND_LIST.pop(index)
        self.LOOP_LIST.pop(index)
        self.VOLUME_LIST.pop(index)
        self.HIDDEN_LIST.pop(index)
        self.ENDLESS_LIST.pop(index)
        self.ENABLED_LIST.pop(index)
        self.editing_alarm_index = None
        self.__change_all_settings()

        self.msg.info(f'Deleted alarm at {index = }')
        if not self.TIME_LIST:
            self.msg.info(f'No alarms anymore')
            self.alarms_created = False
            self.__set_first_default_lists()

        self.__reset_alarm_page()


    def __trigger_alarm(self, alarm):
        index = alarm['index']

        trigger_id = (index, alarm['datetime'].date())

        if trigger_id in self._fired_alarms:
            return

        self._fired_alarms.add(trigger_id)
        self._foreground_alarms_pending_disable.add(index)
        self.msg.info(f'Alarm triggered: {alarm['time']} - "{alarm['name']}"')
        self._app.deiconify()
        self._window_hidden_by_alarm = False
        self.__play_alarm_sound(alarm)

        self.__refresh_alarm_list()


    def __refresh_alarm_list(self):
        if not hasattr(self, 'list_placeable_frame'):
            return

        self.__reset_alarm_page()


    def __create_alarm_window(self):
        self.list_frame.place_forget()
        self._next_alarm_label.place_forget()
        self.utility.clear_visible_widgets()

        comp_fg_col = self.utility.complementaryColor(self.utility.STANDARD_FG_COLOR)
        comp_text_col = self.utility.complementaryColor(self.utility.STANDARD_BUTTON_TEXT_COLOR)
        remove_fg_color = self.utility.adjust_color(comp_fg_col, 50, self.utility.STANDARD_FG_COLOR)
        remove_text_color = self.utility.complementaryColor(remove_fg_color)

        self.cancel_button.configure(fg_color=comp_fg_col, text_color=comp_text_col, hover_color=self.utility.adjust_color(comp_fg_col, 50))
        self.delete_button.configure(fg_color=remove_fg_color, text_color=remove_text_color, hover_color=self.utility.adjust_color(remove_fg_color, 50))

        top_position_save = self.TOP_LABEL_POS.copy()
        top_position_save['rely'] = 1 - top_position_save['rely']
        top_position_save['relwidth'] = 0.3
        top_position_save['relx'] = 0.82

        top_position_cancel = top_position_save.copy()
        top_position_cancel['relx'] = 0.5 if self.editing_alarm_index is not None else 1 - top_position_cancel['relx']

        top_position_delete = top_position_save.copy()
        top_position_delete['relx'] = 0.18

        self.utility.draw_heading_line(relheight=0.01, rely=top_position_save['rely'] - 0.09)

        self.timer_entry_content.place(**self.TOP_LABEL_POS)
        self.cancel_button.place(**top_position_cancel)
        self.save_button.place(**top_position_save)

        if self.editing_alarm_index is not None:
            self.delete_button.place(**top_position_delete)
        else:
            self.delete_button.place_forget()


        self.new_alarm_window.place(relx=0.5, rely=0.5, relwidth=0.95, relheight=0.75, anchor='center')
        self.utility.make_label_fit_in_frame(self.selected_volume_variable_label, self.volume_frame, truncate=True)


    def __handle_switch(self, switch_var, index: int, row: ctk.CTkFrame):
        enabled = bool(switch_var.get())
        self.ENABLED_LIST[index] = enabled

        if not enabled:
            self._foreground_alarms_pending_disable.discard(index)

            channel = self._alarm_channels.pop(index, None)
            self._alarm_sounds.pop(index, None)
            if channel is not None:
                try:
                    channel.stop()
                except Exception:
                    pass

            self._fired_alarms.discard((index, datetime.now().date()))

        self.__change_setting(self.DEFAULT_NAMES['enabled'])
        fg_color = self.utility.STANDARD_ORDERED_FRAME_COLOR if enabled else 'transparent'
        text_color = self.utility.STANDARD_FG_COLOR if enabled else self.utility.STANDARD_TEXT_COLOR
        switch_text = 'Enabled' if enabled else 'Disabled'

        row.configure(fg_color=fg_color, border_color=self.utility.STANDARD_MODE_BORDER_COLOR)
        widgets = self.utility.get_widgets_from_scope([], row.winfo_children())
        for child in widgets:
            if isinstance(child, ctk.CTkSwitch):
                child.configure(text=switch_text, text_color=text_color, progress_color=text_color)

            if isinstance(child, ctk.CTkLabel):
                text = child.cget('text')

                if text.find('✓') != -1:
                    hour, minute = map(int, self.TIME_LIST[index].split(':'))
                    period = 'AM' if hour < 12 else 'PM'
                    hour = hour % 12 or 12
                    child.configure(text=f'{hour}:{minute:02d} {period}')
                elif text.find('🔔 Rung') != -1:
                    child.configure(text=self.SHORTENED_NAME_LIST[index])
                child.configure(text_color=text_color)

            if isinstance(child, ctk.CTkFrame):
                child.configure(fg_color=fg_color)

        if self.ALARM_RUNNING:
            if self._alarm_after_id is not None:
                self.master.after_cancel(self._alarm_after_id)
                self._alarm_after_id = None

            next_alarm = self.__get_next_enabled_alarm()
            if next_alarm is None:
                self.__stop_alarm()
            else:
                self.__update_window_state()
                self.__schedule_next_alarm()

        if self.ALARM_RUNNING:
            self.__refresh_running_alarm()
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
            self.SHORTENED_NAME_LIST[index],
            self.DESC_LIST[index],
            self.SOUND_LIST[index],
            self.LOOP_LIST[index],
            self.VOLUME_LIST[index],
            self.HIDDEN_LIST[index],
            self.ENDLESS_LIST[index],
            self.ENABLED_LIST[index]
        ]

        time, name, s_name, description, sound, loops, volume, hidden, endless, enabled = alarm
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
        self.__set_sound_states(sound)


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

    def __get_enabled_alarms(self):
        now = datetime.now()
        candidates = []

        for index, time_string in enumerate(self.TIME_LIST):
            if not bool(self.ENABLED_LIST[index]):
                continue

            hour, minute = map(int, time_string.split(':'))
            alarm_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)

            if alarm_time <= now:
                alarm_time += timedelta(days=1)

            candidates.append({
                'index': index,
                'datetime': alarm_time,
                'time': time_string,
                'hidden': bool(self.HIDDEN_LIST[index]),
                'name': self.NAME_LIST[index],
                'sound': self.SOUND_LIST[index],
                'loops': self.LOOP_LIST[index],
                'volume': self.VOLUME_LIST[index],
                'endless': bool(self.ENDLESS_LIST[index])
            })

        return candidates


    def __get_next_enabled_alarm(self):
        now = datetime.now()
        candidates = []

        for index, time_string in enumerate(self.TIME_LIST):
            if not bool(self.ENABLED_LIST[index]):
                continue

            hour, minute = map(int, time_string.split(':'))
            alarm_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)

            if alarm_time <= now:
                alarm_time += timedelta(days=1)

            candidates.append({
                'index': index,
                'datetime': alarm_time,
                'time': time_string,
                'hidden': bool(self.HIDDEN_LIST[index]),
                'name': self.NAME_LIST[index],
                'sound': self.SOUND_LIST[index],
                'loops': self.LOOP_LIST[index],
                'volume': self.VOLUME_LIST[index],
                'endless': bool(self.ENDLESS_LIST[index])
            })
        if not candidates:
            return None
        return min(candidates, key=lambda alarm: alarm['datetime'])


    def __format_remaining_time(self, delta):
        total_seconds = max(0, int(delta.total_seconds()))
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        if hours > 0:
            return f'{hours}h {minutes}min'

        if minutes > 0:
            return f'{minutes}min {seconds:02d}s'

        return f'{seconds}s'

    def __update_window_state(self):
        if not self.ALARM_RUNNING:
            return

        next_alarm = self.__get_next_enabled_alarm()

        if self._foreground_alarms_pending_disable:
            should_hide = False

        elif next_alarm is None:
            should_hide = False

        else:
            should_hide = bool(next_alarm['hidden'])

        if should_hide == self._window_hidden_by_alarm:
            return

        if should_hide:
            self._app.withdraw()
            self._window_hidden_by_alarm = True
        else:
            self._app.deiconify()
            self._window_hidden_by_alarm = False


    def __update_next_alarm_label(self):
        self._countdown_after_id = None
        if not self._next_alarm_label:
            return

        next_alarm = self.__get_next_enabled_alarm()

        if not next_alarm or not self.alarms_created:
            text = 'No enabled alarms'

        else:
            now = datetime.now()
            hour, minute = map(int, next_alarm['time'].split(':'))
            alarm_datetime = now.replace(hour=hour, minute=minute, second=0, microsecond=0)

            if alarm_datetime <= now:
                alarm_datetime += timedelta(days=1)

            remaining = alarm_datetime - now
            state = 'Running' if self.ALARM_RUNNING else 'Not started'
            text = f'{state}  •  Next alarm: {next_alarm["time"]} •  in {self.__format_remaining_time(remaining)}'

        try:
            self._next_alarm_label.configure(text=text)
        except _tkinter.TclError:
            pass

        self._countdown_after_id = self.master.after(1000, self.__update_next_alarm_label)


    def __refresh_running_alarm(self):
        if not self.ALARM_RUNNING:
            return

        self.__update_window_state()
        self.__update_next_alarm_label()


    def __check_valid_sounds(self):
        if not self.ALARM_RUNNING:
            return

        for alarm in self.__get_enabled_alarms():
            if not self.sound_man.sound_exists(alarm['sound']):
                self._window_hidden_by_alarm = False
                self._app.deiconify()
                self.__stop_alarm()
                text = f'There is an alarm with an invalid sound! Change it.'
                self.msg.bad(text)
                self.utility.show_warning_text(text, 3)

        self.master.after(500, self.__check_valid_sounds)


    def __start_alarm(self):
        if self.ALARM_RUNNING:
            self.__stop_alarm()
            return

        self.__change_all_settings()
        next_alarm = self.__get_next_enabled_alarm()
        text = ''

        if next_alarm is None:
            text = 'No enabled alarms.'

        if self.invalid_sound_exists:
            text = 'There is an alarm with an invalid sound! Change it before starting.'

        if text:
            self.msg.bad(text)
            self.utility.show_warning_text(text, 3)
            return

        self.ALARM_RUNNING = True
        self._fired_alarms.clear()
        self._foreground_alarms_pending_disable.clear()
        self._last_alarm_check = datetime.now()
        self.__change_on_alarm()
        self.__update_window_state()
        self.__update_next_alarm_label()
        self.__check_valid_sounds()
        self._alarm_check_after_id = self.master.after(0, self.__check_running_alarm)

        self.msg.info(f"Alarm system started. Next alarm: {next_alarm['datetime']}")


    def __change_on_alarm(self):
        if self._start_button is None:
            return

        fg_color = self.utility.complementaryColor(self.utility.STANDARD_FG_COLOR)
        text_color = self.utility.complementaryColor(self.utility.STANDARD_BUTTON_TEXT_COLOR)
        self._start_button.configure(text='Stop', command=self.__stop_alarm, fg_color=fg_color, text_color=text_color, hover_color=self.utility.adjust_color(fg_color, 40))


    def __stop_alarm(self):
        self.ALARM_RUNNING = False
        if self._alarm_check_after_id is not None:
            try:
                self.master.after_cancel(self._alarm_check_after_id)
            except Exception:
                pass

            self._alarm_check_after_id = None
        self._fired_alarms.clear()
        self._last_alarm_check = None
        self._foreground_alarms_pending_disable.clear()

        for channel in list(self._alarm_channels.values()):
            try:
                channel.stop()
            except Exception:
                pass
        self._alarm_channels.clear()
        self._alarm_sounds.clear()

        self._window_hidden_by_alarm = False
        self._app.deiconify()
        if self._start_button is not None:
            self._start_button.configure(text='Start', fg_color=self.utility.STANDARD_FG_COLOR, hover_color=self.utility.adjust_color(self.utility.STANDARD_FG_COLOR, 40), command=self.__start_alarm)
        self.utility.clear_scope(scope=self.list_placeable_frame)
        self.__create_alarm_list(None)
        self.__update_next_alarm_label()
        self.msg.info('Alarm system stopped.')


    def __schedule_next_alarm(self):
        if not self.ALARM_RUNNING:
            return

        if self._alarm_check_after_id is None:
            self._alarm_check_after_id = self.master.after(0, self.__check_running_alarm)


    def __play_alarm_sound(self, alarm):
        path = self.path_man.get_sound_path() + '\\'
        sound_file = alarm['sound']
        index = alarm['index']
        if not sound_file:
            self.msg.info(f"Alarm '{alarm['name']}' has no sound.")
            return

        try:
            previous_channel = self._alarm_channels.pop(index, None)
            self._alarm_sounds.pop(index, None)
            if previous_channel is not None:
                previous_channel.stop()

            sound = mixer.Sound(path + sound_file)
            sound.set_volume(int(alarm['volume']) / 100)
            loops = -1 if alarm['endless'] else int(alarm['loops'])
            if not alarm['endless'] and loops <= 0:
                return

            channel = sound.play(loops=loops-1)
            if channel is not None:
                self._alarm_channels[index] = channel
                self._alarm_sounds[index] = sound

            self.msg.info(f"Playing sound for alarm with name: \"{alarm['name']}\"")

        except Exception as error:
            self.msg.info(f"Could not play alarm sound: {error}")


    def __fit_alarm_names(self, index, name_label, time_label, enabled_frame, rung_text):
        self.master.update_idletasks()

        name_str: str = name_label.cget('text')
        name_str = name_str[0:len(name_str)-len(rung_text)]
        original_name = name_str

        try:
            distance = name_label.winfo_x() - time_label.winfo_x() - time_label.winfo_width()

            while True:
                if name_label.winfo_width() + name_label.winfo_x() < enabled_frame.winfo_x() - distance:
                    break

                name_str = name_str[0:len(name_str) - 1]
                name_label.configure(text=name_str + '...' + rung_text)
                self.master.update_idletasks()

            if not rung_text:
                self.SHORTENED_NAME_LIST[index] = name_str if name_str == original_name else name_str + '...'
                self.__change_setting(self.DEFAULT_NAMES['s_name'])
        except _tkinter.TclError as tclerror:
            pass


    def __create_alarm_list(self, event):
        self.alarms = list(zip(
            self.TIME_LIST,
            self.NAME_LIST,
            self.SHORTENED_NAME_LIST,
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
        self.invalid_sound_exists = False

        for alarm_index, alarm in indexed_alarms:
            t, name, s_name, desc, sound, loop, volume, hidden, endless, enabled = alarm

            switch_var = ctk.BooleanVar(value=bool(enabled))
            switch_fg_color = self.utility.STANDARD_ORDERED_FRAME_COLOR if switch_var.get() else 'transparent'
            text_color = self.utility.STANDARD_FG_COLOR if switch_var.get() else self.utility.STANDARD_TEXT_COLOR
            switch_text = 'Enabled' if switch_var.get() else 'Disabled'
            today_trigger_id = (alarm_index, datetime.now().date())
            alarm_fired = today_trigger_id in self._fired_alarms
            invalid_sound_text = ''


            if alarm_fired:
                row_fg_color = self.utility.adjust_color(self.utility.STANDARD_ORDERED_FRAME_COLOR, 35, self.utility.STANDARD_FG_COLOR)
                row_text_color = self.utility.STANDARD_FG_COLOR
                row_border_color = self.utility.STANDARD_FG_COLOR
            elif self.sound_man.sound_exists(sound):
                row_fg_color = switch_fg_color
                row_text_color = text_color
                row_border_color = self.utility.STANDARD_MODE_BORDER_COLOR
            else:
                row_fg_color = self.utility.complementaryColor(self.utility.adjust_color(self.utility.STANDARD_ORDERED_FRAME_COLOR, 35, self.utility.STANDARD_FG_COLOR))
                row_text_color = self.utility.complementaryColor(row_fg_color)
                row_border_color = self.utility.complementaryColor(self.utility.STANDARD_MODE_BORDER_COLOR)
                self.invalid_sound_exists = True
                invalid_sound_text = '<=== This alarm has an invalid sound! Change it. ===>'
                self.SOUND_LIST[alarm_index] = ''
                self.__change_setting(self.DEFAULT_NAMES['sound'])

            list_row = ctk.CTkFrame(self.list_placeable_frame, border_width=5, corner_radius=20, fg_color=row_fg_color, border_color=row_border_color)
            enabled_frame = ctk.CTkFrame(list_row, fg_color=row_fg_color)

            hour, minute = map(int, t.split(':'))
            period = 'AM' if hour < 12 else 'PM'
            hour = hour % 12 or 12
            rung_text = '🔔 Rung' if alarm_fired else ''

            name_text = s_name
            if not s_name.endswith('...'):
                name_text = s_name + '  •  ' if alarm_fired and s_name else s_name
            time_label = ctk.CTkLabel(list_row, text=f'✓ {hour}:{minute:02d} {period}' if alarm_fired else f'{hour}:{minute:02d} {period}', text_color=row_text_color)
            name_label = ctk.CTkLabel(list_row, text=f'{name_text}{rung_text}', text_color=row_text_color)
            enabled_switch = ctk.CTkSwitch(
                enabled_frame,
                text=switch_text,
                text_color=row_text_color,
                variable=switch_var,
                progress_color=row_text_color,
                command=lambda var=switch_var, index=alarm_index, row=list_row: self.__handle_switch(var, index, row)
            )
            invalid_sound_label = ctk.CTkLabel(list_row, text=invalid_sound_text, text_color=row_text_color, font=('Arial', 12))

            list_row.pack(fill='x', pady=5, ipady=30)
            time_label.pack(side='left', padx=10, anchor='center')
            name_label.place(relx=0.15, rely=0.5, anchor='w')
            invalid_sound_label.place(relx=0.5, rely=0.78, relheight=0.2, anchor='center')
            enabled_frame.place(relx=0.875, rely=0.5, relheight=0.8, relwidth=0.2, anchor='center')
            enabled_switch.place(relx=0.5, rely=0.5, anchor='center')
            self.master.after(500, lambda i=alarm_index, n=name_label, t=time_label, e=enabled_frame, r=rung_text: self.__fit_alarm_names(i, n, t, e, r))

            time_label.bind('<MouseWheel>', lambda event: self.list_canvas.yview_scroll(int(-event.delta / 120), 'units'))
            name_label.bind('<MouseWheel>', lambda event: self.list_canvas.yview_scroll(int(-event.delta / 120), 'units'))
            invalid_sound_label.bind('<MouseWheel>', lambda event: self.list_canvas.yview_scroll(int(-event.delta / 120), 'units'))
            list_row.bind('<MouseWheel>', lambda event: self.list_canvas.yview_scroll(int(-event.delta / 120), 'units'))
            enabled_frame.bind('<MouseWheel>', lambda event: self.list_canvas.yview_scroll(int(-event.delta / 120), 'units'))

            list_row.bind('<Button-1>', lambda event, index=alarm_index: self.__change_alarm(index))
            time_label.bind('<Button-1>', lambda event, index=alarm_index: self.__change_alarm(index))
            name_label.bind('<Button-1>', lambda event, index=alarm_index: self.__change_alarm(index))
            invalid_sound_label.bind('<Button-1>', lambda event, index=alarm_index: self.__change_alarm(index))

            list_row.configure(cursor='hand2')
            time_label.configure(cursor='hand2')
            name_label.configure(cursor='hand2')
            invalid_sound_label.configure(cursor='hand2')


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


    def build(self, event = None):
        rev_fg_color = self.utility.complementaryColor(self.utility.STANDARD_FG_COLOR)
        rev_text_color = self.utility.complementaryColor(self.utility.STANDARD_BUTTON_TEXT_COLOR)
        self.top_label_content.configure(text='Alarm')
        self.top_label_content.place(**self.TOP_LABEL_POS)

        self.timer_entry_content = EntryExpanding(self.master, space_count=17, start_text='Alarm     ', font=('Arial', 25))

        create_new_alarm_button = ctk.CTkButton(self.master, text='✚ Create', command=self.__create_new_alarm)
        position = self.TOP_LABEL_POS.copy()
        position['relx'] = position['rely'] * 2
        create_new_alarm_button.place(**position)
        start_button_text = 'Start' if not self.ALARM_RUNNING else 'Stop'
        start_button_color = self.utility.STANDARD_FG_COLOR if not self.ALARM_RUNNING else rev_fg_color
        start_text_color = self.utility.STANDARD_BUTTON_TEXT_COLOR if not self.ALARM_RUNNING else rev_text_color
        self._start_button = ctk.CTkButton(self.master, text=start_button_text, fg_color=start_button_color, text_color=start_text_color, command=self.__start_alarm)
        self._next_alarm_label = ctk.CTkLabel(self.master, text='', font=('Arial', 14))
        self._next_alarm_label.place(relx=0.5, rely=0.97, anchor='center')
        self.__update_next_alarm_label()

        position['relx'] = 1 - position['relx']

        no_alarm_label = ctk.CTkLabel(self.master, text='No Alarms created just yet')

        self.cancel_button = ctk.CTkButton(self.master, text='✗ Cancel', command=self.__cancel_new_alarm, font=('Arial', 20))
        self.save_button = ctk.CTkButton(self.master, text='✔ Save', command=self.__check_new_alarm, font=('Arial', 20))
        self.delete_button = ctk.CTkButton(self.master, text='🗑 Remove', command=self.__delete_alarm, font=('Arial', 20),)

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
        self.volume_slider.set(self.VOLUME_LIST[-1])

        selected_volume_title_label = ctk.CTkLabel(self.volume_frame, text=f'Selected sound:')
        font_style = ctk.CTkFont(weight=None) if self.selected_sound else ctk.CTkFont(weight='bold')
        selected_text = f'> {self.selected_sound}' if self.selected_sound else f'{self.selected_sound}, select one first!'
        fg_color = self.utility.STANDARD_FG_COLOR if self.selected_sound else rev_fg_color
        text_color = self.utility.STANDARD_BUTTON_TEXT_COLOR if self.selected_sound else rev_text_color
        self.selected_volume_variable_label = ctk.CTkLabel(self.volume_frame, text=selected_text, font=font_style)
        self.sound_button = ctk.CTkButton(self.clock_volume_frame, text='♬ Sounds', command=self.__open_sound_manager, fg_color=fg_color, text_color=text_color)

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

            if not self.list_scroll_bar.winfo_ismapped():
                self.list_scroll_bar.place(relx=0.97, rely=0, relwidth=0.03, relheight=1)
                self._start_button.place(**position)
                create_new_alarm_button.configure(fg_color=rev_fg_color, text_color=rev_text_color)
                self.__setup()

            self.__create_alarm_list(None)

        else:
            no_alarm_label.place(relx=0.5, rely=0.5, anchor='center')
            no_alarm_label.lift()
            self.__setup()

        self.utility.create_entry_name(loop_entry, 'loop')
        if self._countdown_after_id is None:
            self.__update_next_alarm_label()