import customtkinter as ctk
import pygame
import threading
import time
from ExpandingEntry import EntryExpanding
from number_pickR import NumberPicker
from messageR import MessageR
from util import Utility
from fileR import FileR
from pathR import PathR

class TimeR():
    def __init__(self, master, TOP_LABEL_POS: dict, top_label_content: ctk.CTkLabel):
        self.master = master
        self.TOP_LABEL_POS = TOP_LABEL_POS
        self.top_label_content = top_label_content

        self.ENDLESS_LOOP = False
        self.SOUND_LOOPS = 3
        self.SOUND_VOLUME = 10
        self.TIMER_RUNNING = False
        self.NUMBERPICKERS = {}
        self.paths = PathR()
        self.utility = Utility(self.master)
        self.file_man = FileR(self.paths.get_base_path_timer())
        self.msg = MessageR('TimeR')

    def __endless_loop(self):
        self.ENDLESS_LOOP = True if self.endless_var.get() else False
        loop_entry = self.utility.get_entry_by_name('loop')
        if self.ENDLESS_LOOP:
            loop_entry.set('∞')
            loop_entry.configure(state=ctk.DISABLED)
        else:
            loop_entry.configure(state=ctk.NORMAL)
            loop_entry.set(f'{self.SOUND_LOOPS}')

    def __change_on_timer(self):
        self.utility.disable_all_buttons_from_scope(self.master)

        fg_color = f'#{self.utility.complementaryColor(self.utility.STANDARD_FG_COLOR)}'
        text_color = f'#{self.utility.complementaryColor(self.utility.STANDARD_BUTTON_TEXT_COLOR)}'
        self.utility.change_button_kwargs('Start', command=self.__stop_timer, state=ctk.NORMAL, text='Stop', fg_color=fg_color, text_color=text_color)

        timer_entry = self.utility.get_entry_by_name('timer')
        timer_content = timer_entry.get().strip()
        timer_text = timer_content if timer_content else 'Timer'
        self.top_label_content.configure(text=timer_text)
        timer_entry.place_forget()
        self.top_label_content.place(**self.TOP_LABEL_POS)

    def __change_off_timer(self):
        self.utility.enable_all_buttons_from_scope()
        self.utility.change_button_kwargs('Stop', command=self.__start_timer, text='Start', fg_color=self.utility.STANDARD_FG_COLOR, text_color=self.utility.STANDARD_BUTTON_TEXT_COLOR)

        timer_entry = self.utility.get_entry_by_name('timer')
        timer_entry.set(self.top_label_content.cget('text'))
        self.top_label_content.place_forget()
        timer_entry.place(**self.TOP_LABEL_POS)

    def __stop_timer(self):
        self.TIMER_RUNNING = False
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()

    def __start_timer(self) -> None:
        loops = self.utility.handle_entry_name_return('loop', 'int', 'invalid', '∞')
        print(f'{loops = }')
        volume = self.SOUND_VOLUME / 100
        if loops == 'invalid':
            self.utility.show_warning_text('The loop count has to be a number!', 4)
            return

        if isinstance(loops, int) and not loops >= 0:
            self.utility.show_warning_text('The timer can not have negative loops!', 4)
            return

        def run_timer(hours, minutes, seconds, loops, volume):
            try:
                self.__change_on_timer()
                hours.block_mouse()
                minutes.block_mouse()
                seconds.block_mouse()
                self.msg.info('Timer has started!')
                self.TIMER_RUNNING = True
                while self.TIMER_RUNNING:
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
                        self.msg.good('Timer ended successfully!')
                        break
                    time.sleep(1)

                if self.TIMER_RUNNING:
                    self.SOUND_LOOPS = loops
                    threading.Thread(target=self.__play_sound, args=(self.SOUND_LOOPS, volume,), daemon=True).start()

                while self.TIMER_RUNNING:
                    continue
            except Exception as e:
                self.msg.bad('Timer has ended with a problem: ' + str(e))
            finally:
                self.__change_off_timer()
                hours.unblock_mouse()
                minutes.unblock_mouse()
                seconds.unblock_mouse()
                self.TIMER_RUNNING = False

        hours = self.NUMBERPICKERS['hour']
        minutes = self.NUMBERPICKERS['minute']
        seconds = self.NUMBERPICKERS['second']
        threading.Thread(target=run_timer, args=(hours, minutes, seconds, loops, volume,), daemon=True).start()

    def __play_sound(self, loops: int, volume: float) -> None:
        pygame.mixer.music.set_volume(volume)
        self.msg.info('Sound playing')
        if isinstance(loops, str):
            while self.TIMER_RUNNING:
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    continue
        else:
            for i in range(loops):
                if self.TIMER_RUNNING:
                    pygame.mixer.music.play()
                    while pygame.mixer.music.get_busy():
                        continue

        self.msg.info('Sound ended')

    def __hide_timer(self):
        pass

    def __hide_all_frames(self):
        widgets = self.utility.get_widgets_from_scope([], self.master.winfo_children())
        for widget in widgets:
            if isinstance(widget, ctk.CTkFrame):
                if not isinstance(widget.cget('fg_color'), str) or widget.cget('fg_color')[0] != '#':
                    widget.configure(fg_color='transparent')

    def __set_volume(self, value):
        self.SOUND_VOLUME = value
        self.volume_value_label.configure(text=f'{int(self.SOUND_VOLUME)}%')

    def __save_timer(self):
        self.file_man.writer('test_file.txt', 'w', 'this is a simple test file')

    def __create_numberpickers(self, hours: NumberPicker, minutes: NumberPicker, seconds: NumberPicker):
        self.NUMBERPICKERS['hour'] = hours
        self.NUMBERPICKERS['minute'] = minutes
        self.NUMBERPICKERS['second'] = seconds


    def start(self):
        timer_entry_content = EntryExpanding(self.master, space_count=16, start_text='Timer',  placeholder_text='Timer', font=('Arial', 25))
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

        hide_checkbox = ctk.CTkCheckBox(self.master, text='Hide Timer', command=self.__hide_timer)
        hide_checkbox.select()
        hide_checkbox.place(relx=0.05, rely=0.75)

        loop_frame = ctk.CTkFrame(self.master)
        loop_label = ctk.CTkLabel(loop_frame, text='Loop Count:')
        loop_entry = ctk.CTkEntry(loop_frame, placeholder_text=f'{self.SOUND_LOOPS}')
        loop_entry.set(f'{self.SOUND_LOOPS}')
        loop_label.place(relx=0, relwidth=0.4)
        loop_entry.place(relx=0.4, relwidth=0.6)
        loop_frame.place(relx=0.65, rely=0.75, relheight=0.1)

        volume_frame = ctk.CTkFrame(self.master)
        volume_label = ctk.CTkLabel(volume_frame, text='Volume')
        volume_slider = ctk.CTkSlider(volume_frame, orientation='vertical', scroll_step=0, from_=0, to=100, number_of_steps=100, command=self.__set_volume)
        self.volume_value_label = ctk.CTkLabel(volume_frame, text=f'{self.SOUND_VOLUME}%')
        volume_slider.set(self.SOUND_VOLUME)
        volume_label.place(relx=0.2, rely=0.45, anchor='center')
        volume_slider.place(relx=0.5, rely=0.5, relheight=0.8, anchor='center')
        self.volume_value_label.place(relx=0.5, rely=0.03, anchor='center')
        volume_frame.place(relx=0.95, rely=0.45, relheight=0.53, relwidth=0.2, anchor='center')

        self.endless_var = ctk.StringVar(value='')
        endless_loop_checkbox = ctk.CTkCheckBox(self.master, text='Endless Loop', command=self.__endless_loop, variable=self.endless_var, onvalue='endless', offvalue='')
        endless_loop_checkbox.place(relx=0.05, rely=0.825)

        save_timer_button = ctk.CTkButton(self.master, text='Save ✔', command=self.__save_timer, font=('Arial', 18))
        save_timer_button.place(relx=0.745, rely=0.875)

        self.utility.create_entry_name(timer_entry_content, 'timer')
        self.utility.create_entry_name(loop_entry, 'loop')

        self.__hide_all_frames()