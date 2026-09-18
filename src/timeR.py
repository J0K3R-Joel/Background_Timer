import customtkinter as ctk
import pywinstyles
import pygame.mixer as mixer
import threading
import time
from datetime import datetime, timedelta
from ExpandingEntry import EntryExpanding
from circular_progress_bar import CircularProgressBar
from number_pickR import NumberPicker
from messageR import MessageR
from util import Utility
from timing import Timing
from constants import Constants

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
        self.NUMBERPICKERS = {}
        self.utility = Utility(self.master)
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
        if self.top_label_content.winfo_width() > self.master.winfo_width():
            last_half_text = timer_text[len(timer_text) // 2:]
            space_index = last_half_text.find(' ')
            if space_index != -1:
                last_half_text = last_half_text[0:space_index] + '\n' + last_half_text[space_index:]
                timer_text = timer_text[0:len(timer_text) // 2] + last_half_text
                self.top_label_content.configure(text=timer_text)
            original_length = len(timer_text)

            while self.top_label_content.winfo_width() > self.master.winfo_width():
                timer_text = timer_text[0:len(timer_text)-1]  # -1 to remove the last char
                self.top_label_content.configure(text=timer_text)
                self.master.update_idletasks()

            if len(timer_text) < original_length:
                timer_text = timer_text[0:len(timer_text)-2]  # -2 because the 3 dots that get added are approximately 2 "normal" char wide
                timer_text += '...'

        self.top_label_content.configure(text=timer_text)

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
        threading.Thread(target=self.__run_timer).start()


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
        self.TIMER_RUNNING = False
        if mixer.music.get_busy():
            mixer.music.stop()
        hours = self.NUMBERPICKERS['hour']
        minutes = self.NUMBERPICKERS['minute']
        seconds = self.NUMBERPICKERS['second']
        hours.set(0)
        minutes.set(0)
        seconds.set(0)


    def __start_timer(self) -> None:
        if self.HIDDEN_TIMER:
            self.__show_hidden_accept_window()
        else:
            threading.Thread(target=self.__run_timer).start()


    def __run_timer(self):
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
            already_set = False
            i = 0

            while self.TIMER_RUNNING:
                i += 1
                self.progress_bar.set_value(i)
                if hours.get() != 0 and minutes.get() == 0 and seconds.get() == 0:
                    hours.decrease()
                    minutes.set(minutes.get_max())
                    seconds.set(seconds.get_max())
                    already_set = True
                if not already_set and (minutes.get() != 0 and seconds.get() == 0):
                    minutes.decrease()
                    seconds.set(seconds.get_max())
                    already_set = True
                if not already_set and (hours.get() != 0 or minutes.get() != 0 or seconds.get() != 0):
                    seconds.decrease()
                if hours.get() == 0 and minutes.get() == 0 and seconds.get() == 0:
                    self.msg.end()
                    break
                if already_set:
                    already_set = False
                time.sleep(1)

            if self.HIDDEN_TIMER:
                self._app.deiconify()
            self.__play_sound()

        except Exception as e:
            self.msg.bad('Timer has ended with a problem: ' + str(e))
        finally:
            self.TIMER_RUNNING = False
            self.__change_off_timer()
            hours.unblock_mouse()
            minutes.unblock_mouse()
            seconds.unblock_mouse()


    def __play_sound(self) -> None:
        mixer.music.set_volume(self.SOUND_VOLUME/100)
        self.msg.info('Sound playing')
        if isinstance(self.SOUND_LOOPS, str):  # endless loop
            while self.TIMER_RUNNING:
                mixer.music.play()
                while mixer.music.get_busy():
                    self.master.update_idletasks()
        else:
            for i in range(self.SOUND_LOOPS):
                if self.TIMER_RUNNING:
                    mixer.music.play()
                    while mixer.music.get_busy():
                        self.master.update_idletasks()
                else:
                    break

        self.msg.info('Sound ended')


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
            print(f'{self.SOUND_LOOPS = }')
            amount = 3 if self.loop_var.get() == '∞' and self.SOUND_LOOPS == '∞' else self.SOUND_LOOPS
            loop_entry.set(f'{amount}')


    def __set_volume(self, value):
        self.SOUND_VOLUME = value
        self.__change_setting(self.DEFAULT_NAMES['volume'])
        self.volume_value_label.configure(text=f'{int(self.SOUND_VOLUME)}%')


    def __create_numberpickers(self, hours: NumberPicker, minutes: NumberPicker, seconds: NumberPicker):
        self.NUMBERPICKERS['hour'] = hours
        self.NUMBERPICKERS['minute'] = minutes
        self.NUMBERPICKERS['second'] = seconds


    def build(self):
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

        button_start_timer = ctk.CTkButton(self.master, text='Start', command=self.__start_timer)
        button_start_timer.place(relx=0.5, rely=0.6, anchor='center')

        self.hidden_var = ctk.StringVar(value='hidden') if self.HIDDEN_TIMER else ctk.StringVar(value='')
        hide_checkbox = ctk.CTkCheckBox(self.master, text='Hide Timer', command=self.__hide_timer, variable=self.hidden_var, onvalue='hidden', offvalue='')
        hide_checkbox.place(relx=0.05, rely=0.75)

        loop_frame = ctk.CTkFrame(self.master)
        loop_label = ctk.CTkLabel(loop_frame, text='Loop Count:')

        loop_start_text = '∞' if self.ENDLESS_LOOP else self.SOUND_LOOPS
        loop_start_text = 3 if self.SOUND_LOOPS == '∞' and not self.ENDLESS_LOOP else loop_start_text  # standard amount if it shouldnt be endless, but the last loop value was endless
        self.loop_var = ctk.StringVar(value=loop_start_text)
        loop_start_state = ctk.DISABLED if self.ENDLESS_LOOP else ctk.NORMAL
        loop_entry = ctk.CTkEntry(loop_frame, textvariable=self.loop_var)
        loop_entry.configure(state=loop_start_state)
        loop_label.place(relx=0, relwidth=0.4)
        loop_entry.place(relx=0.4, relwidth=0.6)
        loop_frame.place(relx=0.65, rely=0.75, relheight=0.1)

        volume_frame = ctk.CTkFrame(self.master)
        volume_label = ctk.CTkLabel(volume_frame, text='Volume')
        volume_slider = ctk.CTkSlider(volume_frame, orientation='vertical', scroll_step=0, from_=0, to=100, number_of_steps=100, command=self.__set_volume)
        self.volume_value_label = ctk.CTkLabel(volume_frame, text=f'{int(self.SOUND_VOLUME)}%')
        volume_slider.set(self.SOUND_VOLUME)
        volume_label.place(relx=0.2, rely=0.45, anchor='center')
        volume_slider.place(relx=0.5, rely=0.5, relheight=0.8, anchor='center')
        self.volume_value_label.place(relx=0.5, rely=0.03, anchor='center')
        volume_frame.place(relx=0.95, rely=0.45, relheight=0.53, relwidth=0.2, anchor='center')

        self.endless_var = ctk.StringVar(value='endless') if self.ENDLESS_LOOP else ctk.StringVar(value='')
        endless_loop_checkbox = ctk.CTkCheckBox(self.master, text='Endless Loop', command=self.__endless_loop, variable=self.endless_var, onvalue='endless', offvalue='')
        endless_loop_checkbox.place(relx=0.05, rely=0.825)

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

        self.utility.hide_all_frames()
        self.utility.set_default_button_text_color()
        self.utility.set_default_fg_color()
        self.utility.set_default_text_color()
        self.utility.set_default_writable_content_color()
        self.utility.set_default_button_text_color()
