import os
import shutil
import time

import pygame
import customtkinter as ctk

from tkinter import filedialog, messagebox
from mutagen import File as MutagenFile
from messagR import MessageR
from pathR import PathR
from fileR import FileR
from constants import Constants


class SoundManager(ctk.CTkToplevel):
    SOUND_EXTENSIONS = {
        ".wav",
        ".mp3",
        ".ogg",
        ".flac",
        ".mod",
        ".xm",
        ".s3m",
        ".it",
        ".mid",
        ".midi",
    }

    DEFAULT_CONSTANTS = {
        "sound_order": {}
    }

    def __init__(self, parent):
        super().__init__(parent)

        self.parent = parent
        self.msg = MessageR(self.__class__.__name__)
        self.path_man = PathR(self.__class__.__name__)
        self.file_man = FileR(self.path_man.get_config_path())
        self.sound_folder = self.path_man.get_sound_path()
        self.constants = Constants(self)

        self.sound_config_file = self.path_man.get_config_file_path()

        self.sound_config = {"sounds": {}}
        self.__load_saved_configs()

        self.title("Sound Manager")
        self.geometry("650x620")
        self.minsize(550, 500)
        self.transient(parent)

        self.protocol("WM_DELETE_WINDOW", self.__close_window)

        os.makedirs(self.sound_folder, exist_ok=True)

        self.sounds = []
        self.selected_index = -1
        self.selected_sound = None
        self.loaded_sound = None

        self.current_position = 0.0
        self.pending_position = 0.0
        self.sound_duration = 0.0

        self.is_paused = False
        self.timeline_dragging = False
        self.play_start_time = None

        self.__initialize_pygame()
        self.__create_widgets()
        self.__load_sounds()

        self.__update_timeline()
        self.after(100, self.__focus_sound_list)


    def __load_saved_configs(self):
        dd = self.constants.get_default_dict()
        self.SOUND_ORDER = dd["sound_order"]


    def __change_setting(self, setting_name: str):
        if setting_name == "sound_order":
            new_value = self.SOUND_ORDER
        else:
            raise NotImplementedError(
                f"{setting_name} does not exist"
            )

        self.constants.change_element(
            setting_name,
            new_value
        )


    def __initialize_pygame(self):
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
        except pygame.error as error:
            messagebox.showerror("Audio Error", f"Could not initialize pygame.mixer:\n\n{error}")
            self.msg.error(f"Could not initialize pygame.mixer:\n\n{error}")


    def __create_widgets(self):
        title = ctk.CTkLabel(self, text="Sound Manager", font=ctk.CTkFont(size=24, weight="bold"))
        title.pack(pady=(20, 5))

        folder_label = ctk.CTkLabel(self, text=f"Folder: {self.sound_folder}", text_color="gray")
        folder_label.pack(pady=(0, 15))

        self.sound_list = ctk.CTkScrollableFrame(self, width=500, height=220)
        self.sound_list.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        self.bind("<Up>", self.__select_previous)
        self.bind("<Down>", self.__select_next)
        self.bind("<Left>", self.__seek_backward)
        self.bind("<Right>", self.__seek_forward)
        self.bind("<Return>", self.__confirm_selection)
        self.bind("<KP_Enter>", self.__confirm_selection)
        self.bind("<space>", self.__play_selected)

        self.status_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=14))
        self.status_label.pack(pady=(0, 8))

        timeline_frame = ctk.CTkFrame(self)
        timeline_frame.pack(fill="x", padx=20, pady=(0, 5))

        self.current_time_label = ctk.CTkLabel(timeline_frame, text="00:00", width=50)
        self.current_time_label.pack(side="left", padx=(10, 5))

        self.timeline = ctk.CTkSlider(timeline_frame, from_=0, to=1, command=self.__timeline_changed)
        self.timeline.pack(side="left", fill="x", expand=True, padx=5)

        self.timeline.bind("<Button-1>", self.__timeline_mouse_down)
        self.timeline.bind("<ButtonRelease-1>", self.__timeline_mouse_up)

        self.duration_label = ctk.CTkLabel(timeline_frame, text="00:00", width=50)
        self.duration_label.pack(side="right", padx=(5, 10))

        volume_frame = ctk.CTkFrame(self)
        volume_frame.pack(fill="x", padx=20, pady=5)

        volume_label = ctk.CTkLabel(volume_frame, text="Volume:")
        volume_label.pack(side="left", padx=(15, 5))

        self.volume_value_label = ctk.CTkLabel(volume_frame, text="100%", width=45)
        self.volume_value_label.pack(side="right", padx=10)

        self.volume_slider = ctk.CTkSlider(volume_frame, from_=0, to=100, command=self.__change_volume)
        self.volume_slider.pack(side="left", fill="x", expand=True, padx=10)
        self.volume_slider.set(100)

        playback_frame = ctk.CTkFrame(self)
        playback_frame.pack(fill="x", padx=20, pady=10)

        self.play_button = ctk.CTkButton(playback_frame, text="▶ Play", command=self.__play_selected)
        self.play_button.pack(side="left", expand=True, fill="x", padx=(10, 5), pady=10)

        self.stop_button = ctk.CTkButton(playback_frame, text="■ Stop", command=self.__stop_sound)
        self.stop_button.pack(side="left", expand=True, fill="x", padx=5, pady=10)

        self.delete_button = ctk.CTkButton(playback_frame, text="🗑 Delete", fg_color="#a83232", hover_color="#c43c3c", command=self.__delete_selected)
        self.delete_button.pack(side="left", expand=True, fill="x", padx=(5, 10), pady=10)

        self.confirm_button = ctk.CTkButton(self, text="✓ Confirm Selection", height=40, command=self.__confirm_selection)
        self.confirm_button.pack(padx=20, pady=(10, 5), fill="x")

        self.add_button = ctk.CTkButton(self, text="＋ Add Sound", command=self.__add_sound, height=40)
        self.add_button.pack(fill="x", padx=20, pady=(0, 10))


    def __get_selected_sound(self):
        return self.selected_sound


    def __load_sounds(self):
        self.__stop_sound()
        self.sounds = []

        try:
            files = os.listdir(self.sound_folder)
        except OSError as error:
            messagebox.showerror("Error", f"Could not read the sound folder:\n\n{error}", parent=self)
            self.msg.error(f"Could not read the sound folder:\n\n{error}")
            return

        for filename in files:
            full_path = os.path.join(self.sound_folder, filename)

            if not os.path.isfile(full_path):
                continue

            extension = os.path.splitext(filename)[1].lower()
            if extension in self.SOUND_EXTENSIONS:
                self.sounds.append(filename)

        self.__cleanup_sound_order()
        self.sounds.sort(key=lambda filename: self.SOUND_ORDER.get(filename, 0), reverse=True)

        self.selected_index = -1
        self.__update_sound_list()
        self.__reset_timeline()


    def __update_sound_list(self):
        for widget in self.sound_list.winfo_children():
            widget.destroy()

        if not self.sounds:
            empty_label = ctk.CTkLabel(self.sound_list, text="No sounds available.", font=ctk.CTkFont(size=16), text_color="gray")
            empty_label.pack(expand=True, pady=80)
            self.status_label.configure(text="No sounds available.")
            return

        self.status_label.configure(text=f"{len(self.sounds)} sound(s) available")
        for index, filename in enumerate(self.sounds):
            fg_color = ("gray70", "gray30") if index == self.selected_index else "transparent"

            button = ctk.CTkButton(self.sound_list, text=filename, anchor="w", fg_color=fg_color, hover_color=("gray75", "gray25"), text_color=("black", "white"), command=lambda i=index: self.__select_sound(i),)
            button.pack(fill="x", padx=5, pady=2)

            button.bind("<Double-Button-1>", lambda event, i=index: self.__confirm_sound(i))


    def __confirm_sound(self, index):
        self.__select_sound(index)
        self.__confirm_selection()
        return "break"


    def __select_sound(self, index):
        if not self.sounds:
            return

        if index < 0 or index >= len(self.sounds):
            return

        if index == self.selected_index:
            return

        if self.loaded_sound is not None and self.loaded_sound != self.sounds[index]:
            self.__stop_sound()

        self.selected_index = index
        filename = self.sounds[index]
        self.status_label.configure(text=f"Selected: {filename}")
        self.__update_selection_visual()

        self.current_position = 0.0
        self.pending_position = 0.0

        self.__load_duration(filename)
        self.timeline.set(0)
        self.current_time_label.configure(text="00:00")


    def __confirm_selection(self, event=None):
        if not self.sounds:
            return "break"

        if self.selected_index == -1:
            messagebox.showinfo("No Selection", "Please select a sound first.", parent=self)
            self.msg.warning("Please select a sound first.")
            return "break"

        self.selected_sound = self.sounds[self.selected_index]

        print(f"Selected sound: {self.selected_sound}")

        self.__stop_sound()
        self.parent.sound_manager = None
        self.destroy()
        self.msg.info(f'Selected sound: "{self.selected_sound}"')

        return "break"


    def __update_selection_visual(self):
        children = self.sound_list.winfo_children()

        for index, widget in enumerate(children):
            if index == self.selected_index:
                widget.configure(fg_color=("gray70", "gray30"))
            else:
                widget.configure(fg_color="transparent")


    def __focus_sound_list(self):
        self.focus_set()
        if self.sounds and self.selected_index == -1:
            self.__select_sound(0)


    def __select_previous(self, event=None):
        if not self.sounds:
            return "break"

        new_index = 0 if self.selected_index == -1 else max(0, self.selected_index - 1)

        self.__select_sound(new_index)
        return "break"


    def __select_next(self, event=None):
        if not self.sounds:
            return "break"

        new_index = 0 if self.selected_index == -1 else min(len(self.sounds) - 1, self.selected_index + 1)
        self.__select_sound(new_index)
        return "break"


    def __seek_backward(self, event=None):
        if self.sound_duration <= 0:
            return "break"

        self.__seek_to(max(0.0, self.current_position - 5))
        return "break"


    def __seek_forward(self, event=None):
        if self.sound_duration <= 0:
            return "break"

        self.__seek_to(min(self.sound_duration, self.current_position + 5))
        return "break"


    def __load_duration(self, filename):
        self.sound_duration = 0.0
        path = os.path.join(self.sound_folder, filename)

        try:
            audio = MutagenFile(path)

            if audio is not None and audio.info:
                self.sound_duration = float(audio.info.length)
        except Exception:
            self.sound_duration = 0.0

        if self.sound_duration > 0:
            self.timeline.configure(from_=0, to=self.sound_duration)
            self.duration_label.configure(text=self.__format_time(self.sound_duration))
        else:
            self.timeline.configure(from_=0, to=1)
            self.duration_label.configure(text="--:--")


    def __play_selected(self, event=None):
        if not self.sounds:
            return "break"

        if self.selected_index == -1:
            self.__select_sound(0)

        filename = self.sounds[self.selected_index]
        path = os.path.join(self.sound_folder, filename)
        try:
            # Resume a paused sound.
            if self.is_paused and self.loaded_sound == filename:
                pygame.mixer.music.unpause()

                self.is_paused = False
                self.play_start_time = time.monotonic()

                self.play_button.configure(text="⏸ Pause")
                self.status_label.configure(text=f"▶ Playing: {filename}")
                self.msg.info(f'Stopped sound playing: "{filename}"')
                return "break"

            # Pause the currently playing sound.
            if self.loaded_sound == filename and pygame.mixer.music.get_busy():
                pygame.mixer.music.pause()

                if self.play_start_time is not None:
                    self.current_position += time.monotonic() - self.play_start_time

                self.current_position = max(0.0, min(self.current_position, self.sound_duration))
                self.pending_position = self.current_position
                self.play_start_time = None
                self.is_paused = True

                self.timeline.set(self.current_position)
                self.current_time_label.configure(text=self.__format_time(self.current_position))
                self.play_button.configure(text="▶ Resume")
                self.status_label.configure(text=f"⏸ Paused: {filename}")

                self.msg.info(f'Running sound stopped: "{filename}"')
                return "break"

            # Load and start a new sound.
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()
            pygame.mixer.music.load(path)

            pygame.mixer.music.set_volume(self.volume_slider.get() / 100)

            self.loaded_sound = filename
            self.is_paused = False

            start_position = self.pending_position

            if self.sound_duration > 0:
                start_position = max(0, min(start_position, self.sound_duration))
            else:
                start_position = 0

            pygame.mixer.music.play()

            if start_position > 0:
                try:
                    pygame.mixer.music.set_pos(start_position)
                except pygame.error:
                    pass

            self.current_position = start_position
            self.pending_position = start_position
            self.play_start_time = time.monotonic()

            self.timeline.set(start_position)
            self.current_time_label.configure(text=self.__format_time(start_position))
            self.play_button.configure(text="⏸ Pause")
            self.status_label.configure(text=f"▶ Playing: {filename}")
            self.msg.info(f'New sound playing: "{filename}"')
        except pygame.error as error:
            self.loaded_sound = None
            self.is_paused = False
            self.play_button.configure(text="▶ Play")

            messagebox.showerror("Playback Error", f"Could not play the file:\n\n{filename}\n\nError:\n{error}", parent=self)
            self.msg.error(f"Could not play the file:\n\n{filename}\n\nError:\n{error}")
        return "break"

    def __stop_sound(self):
        try:
            if pygame.mixer.get_init():
                if pygame.mixer.get_busy():
                    filename = self.sounds[self.selected_index]
                    self.msg.info(f'Stopped sound: "{filename}"')
                pygame.mixer.music.stop()
                pygame.mixer.music.unload()
        except pygame.error:
            pass
        except IndexError:
            pass

        self.loaded_sound = None
        self.is_paused = False
        self.play_start_time = None
        self.current_position = 0.0
        self.pending_position = 0.0

        if hasattr(self, "play_button"):
            self.play_button.configure(text="▶ Play")

        if hasattr(self, "timeline"):
            self.timeline.set(0)

        if hasattr(self, "current_time_label"):
            self.current_time_label.configure(text="00:00")


    def __update_timeline(self):
        try:
            if self.loaded_sound is not None and not self.is_paused and self.play_start_time is not None:
                elapsed = time.monotonic() - self.play_start_time
                position = self.current_position + elapsed

                if self.sound_duration > 0 and position >= self.sound_duration:
                    position = self.sound_duration
                    self.timeline.set(position)
                    self.current_time_label.configure(text=self.__format_time(position))
                    self.current_position = position
                    self.pending_position = position
                    self.loaded_sound = None
                    self.is_paused = False
                    self.play_start_time = None

                    self.play_button.configure(text="▶ Play")
                    self.status_label.configure(text="Playback finished")

                elif not self.timeline_dragging:
                    self.timeline.set(position)
                    self.current_time_label.configure(text=self.__format_time(position))

        except Exception:
            pass

        self.after(50, self.__update_timeline)


    def __timeline_mouse_down(self, event):
        if self.sound_duration <= 0:
            return "break"

        self.timeline_dragging = True
        self.__seek_from_mouse(event)

        return "break"


    def __timeline_mouse_up(self, event):
        if self.sound_duration <= 0:
            return "break"

        self.__seek_from_mouse(event)
        self.timeline_dragging = False

        return "break"


    def __timeline_changed(self, value):
        if not self.timeline_dragging:
            return

        try:
            position = float(value)
            self.current_position = position
            self.pending_position = position
            self.current_time_label.configure(text=self.__format_time(position))
        except (ValueError, TypeError):
            pass


    def __seek_from_mouse(self, event):
        if self.sound_duration <= 0:
            return

        width = self.timeline.winfo_width()
        if width <= 0:
            return

        padding = 10
        usable_width = width - (padding * 2)
        if usable_width <= 0:
            return

        x = event.x - padding
        x = max(0, min(usable_width, x))
        ratio = x / usable_width
        position = ratio * self.sound_duration
        self.__seek_to(position)


    def __seek_to(self, position):
        if self.sound_duration <= 0:
            return

        position = max(0.0, min(float(position), self.sound_duration))
        self.current_position = position
        self.pending_position = position
        filename = self.loaded_sound

        if filename is None:
            self.timeline.set(position)
            self.current_time_label.configure(text=self.__format_time(position))
            return

        path = os.path.join(self.sound_folder, filename)
        was_paused = self.is_paused

        try:
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(self.volume_slider.get() / 100)
            pygame.mixer.music.play()

            extension = os.path.splitext(filename)[1].lower()

            try:
                if extension == ".mp3":
                    pygame.mixer.music.rewind()

                    if position > 0:
                        pygame.mixer.music.set_pos(position)
                elif position > 0:
                    pygame.mixer.music.set_pos(position)
            except pygame.error:
                pass

            if was_paused:
                pygame.mixer.music.pause()
                self.is_paused = True
                self.play_start_time = None
                self.play_button.configure(text="▶ Resume")
            else:
                self.is_paused = False
                self.play_start_time = time.monotonic()
                self.play_button.configure(text="⏸ Pause")

            self.timeline.set(position)
            self.current_time_label.configure(text=self.__format_time(position))

        except pygame.error as error:
            self.status_label.configure(text=f"Seek error: {error}")


    @staticmethod
    def __format_time(seconds):
        seconds = max(0, int(seconds))
        minutes = seconds // 60
        remaining_seconds = seconds % 60
        hours = minutes // 60
        minutes %= 60

        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{remaining_seconds:02d}"

        return f"{minutes:02d}:{remaining_seconds:02d}"


    def __reset_timeline(self):
        self.sound_duration = 0.0
        self.timeline.configure(from_=0, to=1)
        self.timeline.set(0)
        self.current_time_label.configure(text="00:00")
        self.duration_label.configure(text="00:00")


    def __change_volume(self, value):
        volume = float(value)
        self.volume_value_label.configure(text=f"{round(volume)}%")

        try:
            if pygame.mixer.get_init():
                pygame.mixer.music.set_volume(volume / 100)
        except pygame.error:
            pass


    def __add_sound(self):
        filetypes = [
            (
                "Audio Files",
                "*.wav *.mp3 *.ogg *.flac "
                "*.mod *.xm *.s3m *.it *.mid *.midi",
            ),
            ("All Files", "*.*"),
        ]

        selected_file = filedialog.askopenfilename(parent=self, title="Select Sound", filetypes=filetypes)
        if not selected_file:
            return

        extension = os.path.splitext(selected_file)[1].lower()
        if extension not in self.SOUND_EXTENSIONS:
            messagebox.showwarning("Unsupported Format", "This file does not have a supported audio file extension.", parent=self)
            self.msg.bad("This file does not have a supported audio file extension.")
            return

        filename = os.path.basename(selected_file)
        destination = os.path.join(self.sound_folder, filename)

        if os.path.exists(destination):
            overwrite = messagebox.askyesno("File Already Exists", f"The file\n\n{filename}\n\nalready exists. Do you want to replace it?", parent=self)

            if not overwrite:
                return

        try:
            shutil.copy2(selected_file, destination)
        except OSError as error:
            messagebox.showerror("Error", f"Could not copy the file:\n\n{error}", parent=self)
            self.msg.error(f"Could not copy the file:\n\n{error}")
            return

        self.SOUND_ORDER[filename] = time.time()
        self.__change_setting("sound_order")

        self.__load_sounds()

        if filename in self.sounds:
            index = self.sounds.index(filename)
            self.__select_sound(index)

        self.status_label.configure(text=f"Added: {filename}")
        self.msg.info(f'Added sound: "{filename}"')


    def __delete_selected(self):
        if not self.sounds:
            return

        if self.selected_index == -1:
            messagebox.showinfo("No Selection", "Please select a sound first.", parent=self)
            self.msg.warning("Please select a sound first.")
            return

        filename = self.sounds[self.selected_index]
        answer = messagebox.askyesno("Delete sound", f"Do you really want to delete this sound?\n\n{filename}", parent=self)

        if not answer:
            return
        path = os.path.join(self.sound_folder, filename)

        try:
            if pygame.mixer.get_init():
                pygame.mixer.music.stop()
                pygame.mixer.music.unload()
        except pygame.error:
            pass

        self.loaded_sound = None
        self.is_paused = False
        self.play_button.configure(text="▶ Play")

        try:
            os.remove(path)
        except PermissionError:
            messagebox.showerror("File In Use", f"The file could not be deleted:\n\n{filename}\n\nIt is still being used by another process.", parent=self)
            self.msg.error(f"The file could not be deleted:\n\n{filename}\n\nIt is still being used by another process.")
            return
        except OSError as error:
            messagebox.showerror("Error", f"Could not delete the file:\n\n{error}", parent=self)
            self.msg.error(f"Could not delete the file:\n\n{error}")
            return

        if filename in self.SOUND_ORDER:
            del self.SOUND_ORDER[filename]
        self.__change_setting("sound_order")

        old_index = self.selected_index
        self.__load_sounds()
        if self.sounds:
            new_index = min(old_index, len(self.sounds) - 1)
            self.__select_sound(new_index)

        self.status_label.configure(text=f"Deleted: {filename}")
        self.msg.info(f'Deleted sound: "{filename}"')

    def __cleanup_sound_order(self):
        changed = False

        for filename in list(self.SOUND_ORDER.keys()):
            path = os.path.join(
                self.sound_folder,
                filename
            )

            if not os.path.isfile(path):
                del self.SOUND_ORDER[filename]
                changed = True

        if changed:
            self.__change_setting("sound_order")

    def __close_window(self):
        self.__stop_sound()
        self.parent.sound_manager = None
        self.destroy()


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("My Program")
        self.geometry("500x350")
        self.sound_manager = None

        title = ctk.CTkLabel(self, text="Test Program", font=ctk.CTkFont(size=28, weight="bold"))
        title.pack(pady=50)

        sound_button = ctk.CTkButton(self, text="Manage Sounds", height=50, command=self.__open_sound_manager)
        sound_button.pack(padx=50, fill="x")

    def __open_sound_manager(self):
        if self.sound_manager is not None:
            try:
                if self.sound_manager.winfo_exists():
                    self.sound_manager.focus()
                    self.sound_manager.lift()
                    return
            except Exception:
                pass

        self.sound_manager = SoundManager(self)


if __name__ == "__main__":
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")

    app = App()
    app.mainloop()
