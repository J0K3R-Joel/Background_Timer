import customtkinter as ctk
import pywinstyles
import pygame.mixer as mixer
import threading
import time
from datetime import datetime, timedelta
from ExpandingEntry import EntryExpanding
from circular_progress_bar import CircularProgressBar
from number_pickR import NumberPicker
from messagR import MessageR
from util import Utility
from timing import Timing
from constants import Constants
from soundS import SoundManager

class TimeR(Timing):
    DEFAULT_NAMES = {
        'volume': 'sound_volume',
        'loop': 'sound_loop',
        'endless': 'endless_loop',
        'hidden': 'timer_hidden'

    }

    DEFAULT_CONSTANTS = {
        DEFAULT_NAMES['volume']: 75,
        DEFAULT_NAMES['loop']: 3,
        DEFAULT_NAMES['endless']: False,
        DEFAULT_NAMES['hidden']: True
    }


    def __init__(self, *args, app):
        Timing.__init__(self, *args)
        self._app = app
        self.constants = Constants(self)
        self.TIMER_RUNNING = False
        self._timer_after_id = None
        self._sound_after_id = None
        self._timer_overtime = False
        self._timer_elapsed = 0
        self._sound_loops_remaining = 0
        self.NUMBERPICKERS = {}
        self.utility = Utility(self.master)
        self.sound_man = SoundManager(self.master)
        self.selected_sound = self.sound_man.get_selected_sound()
        self.msg = MessageR(self.__class__.__name__)
        self.__load_saved_configs()


    def __load_saved_configs(self):
        dd = self.constants.get_default_dict()
        self.ENDLESS_LOOP = dd[self.DEFAULT_NAMES['endless']]
        self.SOUND_LOOPS = dd[self.DEFAULT_NAMES['loop']]
        self.SOUND_VOLUME = dd[self.DEFAULT_NAMES['volume']]
        self.HIDDEN_TIMER = dd[self.DEFAULT_NAMES['hidden']]


    def __change_setting(self, setting_name: str):
        if setting_name == self.DEFAULT_NAMES.get('volume'):
            new_value = self.SOUND_VOLUME
        elif setting_name == self.DEFAULT_NAMES.get('endless'):
            new_value = self.ENDLESS_LOOP
        elif setting_name == self.DEFAULT_NAMES.get('loop'):
            new_value = self.SOUND_LOOPS
        elif setting_name == self.DEFAULT_NAMES.get('hidden'):
            new_value = self.HIDDEN_TIMER
        else:
            raise NotImplementedError(setting_name, ' does not exist')

        self.constants.change_element(setting_name, new_value)


    def __change_on_timer(self):
        self.utility.disable_all_buttons_from_scope(self.master)
        self.disable_mode_buttons()

        fg_color = self.utility.complementaryColor(self.utility.STANDARD_FG_COLOR)
        text_color = self.utility.complementaryColor(self.utility.STANDARD_BUTTON_TEXT_COLOR)
        self.utility.change_button_kwargs_text('Start', command=self.__stop_timer, state=ctk.NORMAL, text='Stop', fg_color=fg_color, text_color=text_color)

        timer_entry = self.utility.get_entry_by_name('timer')
        timer_content = timer_entry.get().strip()
        timer_text = timer_content if timer_content else 'Timer'
        timer_entry.place_forget()
        self.top_label_content.configure(text=timer_text)
        self.top_label_content.place(**self.TOP_LABEL_POS)
        self.master.update_idletasks()

        if self.top_label_content.winfo_width() > self.master.winfo_width():
            last_half_text = timer_text[len(timer_text) // 2:]
            space_index = last_half_text.find(' ')

            if space_index != -1:
                last_half_text = last_half_text[0:space_index] + '\n' + last_half_text[space_index:]
                timer_text = timer_text[0:len(timer_text) // 2] + last_half_text
                self.top_label_content.configure(text=timer_text)

            while self.top_label_content.winfo_width() > self.master.winfo_width():
                timer_text = timer_text[0:len(timer_text)-1]  # -1 to remove the last char
                self.top_label_content.configure(text=timer_text + '...')
                self.master.update_idletasks()



        hours = self.NUMBERPICKERS['hour']
        minutes = self.NUMBERPICKERS['minute']
        seconds = self.NUMBERPICKERS['second']
        duration = ''
        if hours.get() != 0:
            duration += f'{hours.get()}hr, '
        if minutes.get() != 0:
            duration += f'{minutes.get()}min, '
        if seconds.get() != 0:
            duration += f'{seconds.get()}sec, '

        duration = duration[0:len(duration)-2]  # -2 to cut the ", " off
        self.duration_label.configure(text=duration)

        time_now = datetime.now()
        future_time = time_now + timedelta(hours=hours.get(), minutes=minutes.get(), seconds=seconds.get())
        time_format = '%H:%M:%S' if seconds.get() else '%H:%M'
        self.current_time_label.configure(text=f'from: {time_now.strftime(time_format)}')
        self.future_time_label.configure(text=f'until: {future_time.strftime(time_format)}')

        self.__handle_progress_bar_shown(hours, minutes, seconds)
        if self.HIDDEN_TIMER:
            self._app.withdraw()
        self.utility.set_default_hover_color()


    def __handle_progress_bar_shown(self, hours, minutes, seconds):
        real_seconds = hours.get() * 60 * 60 + minutes.get() * 60 + seconds.get()
        self.progress_bar.set_max_value(real_seconds)
        self.progress_bar.place(relx=0.15, rely=0.395, anchor='center')


    def __handle_progress_bar_hidden(self):
        self.progress_bar.place_forget()


    def __change_off_timer(self):
        self.utility.enable_all_buttons_from_scope()
        self.enable_mode_buttons()

        button = self.utility.get_specific_button_from_scope('Stop') if not None else self.utility.get_specific_button_from_scope('Start')
        self.utility.change_button_kwargs_widget(button, command=self.__start_timer, text='Start', fg_color=self.utility.STANDARD_FG_COLOR, text_color=self.utility.STANDARD_BUTTON_TEXT_COLOR)

        timer_entry = self.utility.get_entry_by_name('timer')
        timer_entry.set(self.top_label_content.cget('text'))
        self.top_label_content.place_forget()
        timer_entry.place(**self.TOP_LABEL_POS)

        self.duration_label.configure(text='')
        self.current_time_label.configure(text='')
        self.future_time_label.configure(text='')

        self.__handle_progress_bar_hidden()
        self.utility.set_default_hover_color()


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
        self.utility.set_default_hover_color(self._hidden_accept_window_frame)



    def __accept_hidden_accept_window(self):
        self._hidden_accept_window_frame.destroy()
        self.utility.enable_all_buttons_from_scope(self._app)
        pywinstyles.set_opacity(self.master, value=1)
        pywinstyles.set_opacity(self.get_mode_site(), value=1)
        self.__run_timer()


    def __decline_hidden_accept_window(self):
        self._hidden_accept_window_frame.destroy()
        self.utility.enable_all_buttons_from_scope(self._app)
        pywinstyles.set_opacity(self.master, value=1)
        pywinstyles.set_opacity(self.get_mode_site(), value=1)


    def __check_valid_timer(self) -> bool:
        loops = self.utility.handle_entry_name_return('loop', 'int', 'invalid', '∞')
        hours = self.NUMBERPICKERS['hour']
        minutes = self.NUMBERPICKERS['minute']
        seconds = self.NUMBERPICKERS['second']

        if loops == 'invalid':
            self.utility.show_warning_text('The loop count has to be a number!', 4)
            return False

        if isinstance(loops, int) and not loops >= 0:
            self.utility.show_warning_text('The timer can not have negative loops!', 4)
            return False

        if hours.get() == 0 and minutes.get() == 0 and seconds.get() == 0:
            self.utility.show_warning_text('Set a time before starting the Timer', 2)
            return False

        self.SOUND_LOOPS = loops
        self.__change_setting(self.DEFAULT_NAMES['loop'])
        return True

    def __stop_timer(self):
        self.NUMBERPICKERS['hour'].set(0)
        self.NUMBERPICKERS['minute'].set(0)
        self.NUMBERPICKERS['second'].set(0)

        self.__finish_timer()


    def __start_timer(self) -> None:
        if self.HIDDEN_TIMER:
            self.__show_hidden_accept_window()
        else:
            self.__run_timer()

    def __timer_tick(self):
        if not self.TIMER_RUNNING:
            return

        try:
            hours = self.NUMBERPICKERS['hour']
            minutes = self.NUMBERPICKERS['minute']
            seconds = self.NUMBERPICKERS['second']

            if self._timer_overtime:
                if seconds.get() < seconds.get_max():
                    seconds.set(seconds.get() + 1)

                else:
                    seconds.set(0)

                    if minutes.get() < minutes.get_max():
                        minutes.set(minutes.get() + 1)

                    else:
                        minutes.set(0)

                        if hours.get() < hours.get_max():
                            hours.set(hours.get() + 1)

                self._timer_after_id = self.master.after(1000, self.__timer_tick)
                return

            self._timer_elapsed += 1
            self.progress_bar.set_value(self._timer_elapsed)

            already_set = False

            if hours.get() != 0 and minutes.get() == 0 and seconds.get() == 0:
                hours.decrease()
                minutes.set(minutes.get_max())
                seconds.set(seconds.get_max())
                already_set = True

            if not already_set and minutes.get() != 0 and seconds.get() == 0:
                minutes.decrease()
                seconds.set(seconds.get_max())
                already_set = True

            if not already_set and (hours.get() != 0 or minutes.get() != 0 or seconds.get() != 0):
                seconds.decrease()

            if hours.get() == 0 and minutes.get() == 0 and seconds.get() == 0:
                self.msg.end()

                self.__start_overtime()

                if self.HIDDEN_TIMER:
                    self._app.deiconify()

                if self.selected_sound:
                    self.__play_sound()

            self._timer_after_id = self.master.after(1000, self.__timer_tick)

        except Exception as e:
            self.msg.bad('Timer has ended with a problem: ' + str(e))
            self.__finish_timer()


    def __finish_timer(self):
        self.TIMER_RUNNING = False
        self._timer_overtime = False
        self.overtime_sign_label.place_forget()
        self.__set_numberpicker_color(self.utility.STANDARD_TEXT_COLOR)

        if self._timer_after_id is not None:
            self.master.after_cancel(self._timer_after_id)
            self._timer_after_id = None

        if self._sound_after_id is not None:
            self.master.after_cancel(self._sound_after_id)
            self._sound_after_id = None

        if mixer.music.get_busy():
            mixer.music.stop()

        self.__change_off_timer()

        for picker in self.NUMBERPICKERS.values():
            picker.unblock_mouse()

        self.msg.info('Stopped completely')


    def __run_timer(self):
        if self.TIMER_RUNNING:
            return

        if not self.__check_valid_timer():
            return

        hours = self.NUMBERPICKERS['hour']
        minutes = self.NUMBERPICKERS['minute']
        seconds = self.NUMBERPICKERS['second']

        try:
            self.__change_on_timer()

            hours.block_mouse()
            minutes.block_mouse()
            seconds.block_mouse()

            self.msg.start()
            self.TIMER_RUNNING = True
            self._timer_elapsed = 0
            self._sound_loops_remaining = (None if isinstance(self.SOUND_LOOPS, str) else self.SOUND_LOOPS)

            self.__timer_tick()

        except Exception as e:
            self.msg.bad('Timer has ended with a problem: ' + str(e))
            self.__finish_timer()

    def __play_sound(self) -> None:
        mixer.music.set_volume(self.SOUND_VOLUME / 100)

        self.msg.info('Sound playing')

        self._sound_loops_remaining = (
            None if isinstance(self.SOUND_LOOPS, str)
            else self.SOUND_LOOPS
        )

        if self._sound_loops_remaining == 0:
            self.msg.info('Sound ended')
            return

        mixer.music.play()

        self._sound_after_id = self.master.after(
            100,
            self.__check_sound
        )

    def __check_sound(self):
        if not self.TIMER_RUNNING:
            return

        if mixer.music.get_busy():
            self._sound_after_id = self.master.after(100, self.__check_sound)
            return

        if self._sound_loops_remaining is None:
            mixer.music.play()
        elif self._sound_loops_remaining > 1:
            self._sound_loops_remaining -= 1
            mixer.music.play()
        else:
            self.msg.info('Sound ended')
            return

        self._sound_after_id = self.master.after(100, self.__check_sound)


    def __set_numberpicker_color(self, color):
        def change_color(widget):
            try:
                widget.configure(text_color=color)
            except Exception:
                pass

            for child in widget.winfo_children():
                change_color(child)

        for picker in self.NUMBERPICKERS.values():
            change_color(picker)

    def __start_overtime(self):
        self._timer_overtime = True
        self.overtime_sign_label.place(relx=0.3, rely=0.45, anchor='center')
        self.__set_numberpicker_color(self.utility.STANDARD_FG_COLOR)


    def __close_sound_manager(self):
        self.utility.enable_all_buttons_from_scope(self._app)
        pywinstyles.set_opacity(self.master, value=1)
        pywinstyles.set_opacity(self.get_mode_site(), value=1)

        self.selected_sound = self.sound_man.get_selected_sound()
        if self.selected_sound:
            path = self.path_man.get_sound_path() + '\\'
            mixer.music.load(path + self.selected_sound)
        font_style = ctk.CTkFont(weight=None) if self.selected_sound else ctk.CTkFont(weight='bold')
        selected_text = f'> {self.selected_sound}' if self.selected_sound else f'{self.selected_sound}, select one first!'
        fg_color = self.utility.STANDARD_FG_COLOR if self.selected_sound else self.utility.complementaryColor(self.utility.STANDARD_FG_COLOR)
        text_color = self.utility.STANDARD_BUTTON_TEXT_COLOR if self.selected_sound else self.utility.complementaryColor(self.utility.STANDARD_BUTTON_TEXT_COLOR)


        self.selected_volume_variable_label.configure(text=selected_text, font=font_style)
        self.sound_button.configure(fg_color=fg_color, text_color=text_color)
        self.utility.make_label_fit_in_frame(self.selected_volume_variable_label, self.volume_frame, truncate=True)
        self.utility.set_default_fg_color()
        self.utility.set_default_hover_color()
        self.overtime_sign_label.configure(text_color=self.utility.STANDARD_FG_COLOR)


    def __open_sound_manager(self):
        self.utility.disable_all_buttons_from_scope(self._app)
        pywinstyles.set_opacity(self.master, value=0.1)
        pywinstyles.set_opacity(self.get_mode_site(), value=0.2)

        self.sound_man = SoundManager(self.master)
        self.sound_man.start(self.__close_sound_manager)


    def __hide_timer(self):
        self.HIDDEN_TIMER = True if self.hidden_var.get() else False
        self.__change_setting(self.DEFAULT_NAMES['hidden'])


    def __endless_loop(self):
        self.ENDLESS_LOOP = True if self.endless_var.get() else False
        self.__change_setting(self.DEFAULT_NAMES['endless'])
        loop_entry = self.utility.get_entry_by_name('loop')
        if self.ENDLESS_LOOP:
            loop_entry.set('∞')
            loop_entry.configure(state=ctk.DISABLED)
        else:
            loop_entry.configure(state=ctk.NORMAL)
            amount = 3 if self.loop_var.get() == '∞' and self.SOUND_LOOPS == '∞' else self.SOUND_LOOPS
            loop_entry.set(f'{amount}')


    def __set_volume(self, value):
        self.SOUND_VOLUME = value
        self.__change_setting(self.DEFAULT_NAMES['volume'])
        self.volume_value_label.configure(text=f'Amplification: {int(self.volume_var.get())}%')


    def __create_numberpickers(self, hours: NumberPicker, minutes: NumberPicker, seconds: NumberPicker):
        self.NUMBERPICKERS['hour'] = hours
        self.NUMBERPICKERS['minute'] = minutes
        self.NUMBERPICKERS['second'] = seconds


    def __setup(self):
        self.utility.hide_all_frames()
        self.utility.set_default_button_text_color()
        self.utility.set_default_fg_color()
        self.utility.set_default_hover_color()
        self.utility.set_default_text_color()
        self.utility.set_default_writable_content_color()
        self.utility.set_default_button_text_color()
        self.utility.set_ordered_frame_color(self.settings_frame)
        self.utility.set_ordered_frame_color(self.volume_frame)


    def build(self):
        self.top_label_content.place_forget()
        rev_fg_color = self.utility.complementaryColor(self.utility.STANDARD_FG_COLOR)
        rev_text_color = self.utility.complementaryColor(self.utility.STANDARD_BUTTON_TEXT_COLOR)
        timer_entry_content = EntryExpanding(self.master, space_count=16, start_text='Timer     ',  placeholder_text='Timer', font=('Arial', 25))
        timer_entry_content.place(**self.TOP_LABEL_POS)

        timer_frame = ctk.CTkFrame(self.master)
        timer_frame.place(relx=0.5, rely=0.4, relwidth=0.5, relheight=0.45, anchor='center')

        hours_frame = ctk.CTkFrame(timer_frame)
        hours_picker = NumberPicker(hours_frame, 0, 99)
        hours_label_content = ctk.CTkLabel(hours_frame, text='Hours', font=('Arial', 12))
        hours_picker.place(relx=0.7, rely=0.45, anchor='center')
        hours_label_content.place(relx=0.7, rely=0.1, anchor='center')
        hours_frame.place(relx=0.2, rely=0.5, relwidth=0.4, anchor='center')

        minutes_frame = ctk.CTkFrame(timer_frame)
        minutes_picker = NumberPicker(minutes_frame, 0, 59)
        minutes_label_content = ctk.CTkLabel(minutes_frame, text='Minutes', font=('Arial', 12))
        minutes_picker.place(relx=0.5, rely=0.45, anchor='center')
        minutes_label_content.place(relx=0.5, rely=0.1, anchor='center')
        minutes_frame.place(relx=0.5, rely=0.5, relwidth=0.2, anchor='center')

        seconds_frame = ctk.CTkFrame(timer_frame)
        seconds_picker = NumberPicker(seconds_frame, 0, 59)
        seconds_label_content = ctk.CTkLabel(seconds_frame, text='Seconds', font=('Arial', 12))
        seconds_picker.place(relx=0.3, rely=0.45, anchor='center')
        seconds_label_content.place(relx=0.3, rely=0.1, anchor='center')
        seconds_frame.place(relx=0.8, rely=0.5, relwidth=0.4, anchor='center')
        self.__create_numberpickers(hours_picker, minutes_picker, seconds_picker)

        self.overtime_sign_label = ctk.CTkLabel(hours_frame, text='−', font=('Arial', 25, 'bold'))
        self.overtime_sign_label.place_forget()

        button_start_timer = ctk.CTkButton(self.master, text='Start', command=self.__start_timer)
        button_start_timer.place(relx=0.5, rely=0.6, anchor='center')

        self.settings_frame = ctk.CTkFrame(self.master)
        options_title = ctk.CTkLabel(self.settings_frame, text='⚙ Options', font=('Arial', 20, 'bold'))

        options_title.place(relx=0.03, rely=0.25, anchor='w')
        options_separator = ctk.CTkFrame(self.settings_frame, height=2, fg_color=self.utility.STANDARD_MODE_BORDER_COLOR)
        options_separator.place(relx=0.03, rely=0.42, relwidth=0.94)
        settings_separator = ctk.CTkFrame(self.settings_frame, width=2, fg_color=self.utility.STANDARD_MODE_BORDER_COLOR)
        settings_separator.place(relx=0.625, rely=0.7, relheight=0.3, anchor='center')

        self.hidden_var = ctk.StringVar(value='hidden') if self.HIDDEN_TIMER else ctk.StringVar(value='')
        hidden_checkbox = ctk.CTkCheckBox(self.settings_frame, text='Hide Timer', command=self.__hide_timer, variable=self.hidden_var, onvalue='hidden', offvalue='')
        self.endless_var = ctk.StringVar(value='endless') if self.ENDLESS_LOOP else ctk.StringVar(value='')
        endless_checkbox = ctk.CTkCheckBox(self.settings_frame, text='Endless Loop', command=self.__endless_loop, variable=self.endless_var, onvalue='endless', offvalue='')
        hidden_checkbox.place(relx=0.05, rely=0.7, anchor='w')
        endless_checkbox.place(relx=0.32, rely=0.7, anchor='w')

        loop_frame = ctk.CTkFrame(self.settings_frame, fg_color='transparent')
        loop_label = ctk.CTkLabel(loop_frame, text='Loop Count:')
        loop_start_text = '∞' if self.ENDLESS_LOOP else self.SOUND_LOOPS
        loop_start_text = 3 if self.SOUND_LOOPS == '∞' and not self.ENDLESS_LOOP else loop_start_text  # standard amount if it shouldnt be endless, but the last loop value was endless
        self.loop_var = ctk.StringVar(value=loop_start_text)
        loop_start_state = ctk.DISABLED if self.ENDLESS_LOOP else ctk.NORMAL
        loop_entry = ctk.CTkEntry(loop_frame, textvariable=self.loop_var)
        loop_entry.configure(state=loop_start_state)
        loop_separator = ctk.CTkFrame(self.settings_frame, width=2, fg_color=self.utility.STANDARD_MODE_BORDER_COLOR)
        loop_separator.place(relx=0.65, rely=0.43, relheight=0.40, relwidth=0.002)
        loop_label.place(relx=0.1, rely=0.5, anchor='w')
        loop_entry.place(relx=0.75, rely=0.5, relwidth=0.5, anchor='center')
        loop_frame.place(relx=0.805, rely=0.7, relheight=0.5, anchor='center')

        settings_separator.lift()
        options_separator.lift()
        self.settings_frame.place(relx=0.5, rely=0.8, relwidth=0.98, relheight=0.2, anchor='center')

        self.volume_frame = ctk.CTkFrame(self.master)
        volume_title = ctk.CTkLabel(self.volume_frame, text='🔊 Volume', font=('Arial', 20, 'bold'))
        self.volume_var = ctk.IntVar(value=self.SOUND_VOLUME)
        self.volume_slider = ctk.CTkSlider(self.volume_frame, orientation='horizontal', scroll_step=0, from_=0, to=100, number_of_steps=100, variable=self.volume_var, command=self.__set_volume)
        self.volume_value_label = ctk.CTkLabel(self.volume_frame, text=f'Amplification: {int(self.volume_var.get())}%')
        self.volume_slider.set(self.SOUND_VOLUME)

        if self.selected_sound:
            path = self.path_man.get_sound_path() + '\\'
            mixer.music.load(path + self.selected_sound)

        selected_volume_title_label = ctk.CTkLabel(self.volume_frame, text=f'Selected sound:')
        font_style = ctk.CTkFont(weight=None) if self.selected_sound else ctk.CTkFont(weight='bold')
        selected_text = f'> {self.selected_sound}' if self.selected_sound else f'{self.selected_sound}, select one first!'
        fg_color = self.utility.STANDARD_FG_COLOR if self.selected_sound else rev_fg_color
        text_color = self.utility.STANDARD_BUTTON_TEXT_COLOR if self.selected_sound else rev_text_color
        self.selected_volume_variable_label = ctk.CTkLabel(self.volume_frame, text=selected_text, font=font_style)
        self.sound_button = ctk.CTkButton(self.volume_frame, text='♬ Sounds', command=self.__open_sound_manager, fg_color=fg_color, text_color=text_color)

        volume_title.place(relx=0.05, rely=0.1, anchor='w')
        self.volume_value_label.place(relx=0.5, rely=0.27, anchor='center')
        self.volume_slider.place(relx=0.5, rely=0.39, relwidth=0.82, anchor='center')
        selected_volume_title_label.place(relx=0.05, rely=0.78, anchor='w')
        self.selected_volume_variable_label.place(relx=0.05, rely=0.9, anchor='w')
        self.sound_button.place(relx=0.5, rely=0.58, anchor='center')
        self.volume_frame.place(relx=0.71, rely=0.18, relwidth=0.28, relheight=0.5)

        #save_timer_button = ctk.CTkButton(self.master, text='Save ✔', command=self.__save_timer, font=('Arial', 18))
        #save_timer_button.place(relx=0.745, rely=0.875)

        self.duration_label = ctk.CTkLabel(self.master, text='')
        self.duration_label.place(relx=0.15, rely=0.2, anchor='center')

        self.current_time_label = ctk.CTkLabel(self.master, text='')
        self.current_time_label.place(relx=0.15, rely=0.59, anchor='center')

        self.future_time_label = ctk.CTkLabel(self.master, text='')
        self.future_time_label.place(relx=0.15, rely=0.65, anchor='center')

        self.progress_bar = CircularProgressBar(self.master,
                                                progress_color=self.utility.STANDARD_FG_COLOR,
                                                background_color=self.utility.STANDARD_BACKGROUND_COLOR,
                                                text_color=self.utility.STANDARD_TEXT_COLOR,
                                                size=175,
                                                thickness=15,
                                                )

        self.utility.create_entry_name(timer_entry_content, 'timer')
        self.utility.create_entry_name(loop_entry, 'loop')
        self.__setup()
        self.overtime_sign_label.configure(text_color=self.utility.STANDARD_FG_COLOR)
        self.utility.make_label_fit_in_frame(self.selected_volume_variable_label, self.volume_frame, truncate=True)