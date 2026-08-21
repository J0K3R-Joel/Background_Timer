import customtkinter as ctk
# modified code from https://stackoverflow.com/questions/66439025/auto-resizing-tkinter-entry-needs-initial-width

class EntryExpanding(ctk.CTkEntry):
    def __init__(self, master, space_count=14, start_text: str = '', *args, **kwargs):
        self.real_entry = ctk.CTkEntry.__init__(self, master, *args, **kwargs)
        self.reset = True

        self.space_count = space_count
        self.entry_value = ctk.StringVar()
        self.entry_value.trace_add('write', callback=self.callback)
        self.sizer = ctk.CTkLabel(master, textvariable=self.entry_value)

        self.expansive = ctk.CTkEntry(self.sizer, textvariable=self.entry_value)
        self.expansive.place(x=0, y=0, anchor='nw', relwidth=1, relheight=1)

        half_space_count = (self.space_count - len(start_text)) // 2
        self.expansive.insert(0, ' ' * (half_space_count) + start_text + ' ' * (half_space_count))

        self.place = self.sizer.place
        self.place_forget = self.sizer.place_forget
        self.get = self.entry_value.get


    def __shift_cursor_in_entry(self, direction: str, count: int) -> bool:
        if direction != 'left' and direction != 'right':
            print('Direction can only be "right" or "left"!')
            return False
        position = self.expansive.index(ctk.INSERT)

        multiplier = -1 if direction == 'left' else 1
        move_amount = multiplier * count

        if position - move_amount < 0:
            print('You can not move further to the left!')
            return False

        self.expansive.icursor(position + move_amount)
        return True

    def __cursor_reset_in_entry(self):
        position = self.expansive.index(ctk.INSERT)
        self.expansive.icursor(0)
        self.expansive.icursor(position)



    def callback(self, var_name, c, mode):
        text = self.entry_value.get()
        spaces_start = 0
        spaces_end = 0

        if 0 < len(text) < self.space_count:
            self.reset = True
            self.entry_value.set(text + ' ' * (self.space_count-len(text)))
        elif len(text) == 0:
            self.reset = True
            self.entry_value.set(' ' * self.space_count)
            self.sizer.configure(text=' ' * self.space_count)
        elif self.reset:
            for char in text:
                if char == ' ':
                    spaces_start += 1
                else:
                    break

            for char in text[::-1]:
                if char == ' ':
                    spaces_end += 1
                else:
                    break

            spaces_start -= 2  # so that the text isnt cut off at the left side (2 spaces need to stay)
            spaces_end -= 4  # so that the text isnt cut off at the right side (2 spaces need to stay)


            if len(text) > spaces_start + spaces_end:
                if spaces_start > 0:
                    text = text[1:]  # cut the first space off
                elif spaces_end > 1:
                    text = text[0:len(text)-1]  # cut the last space off
                else:
                    text = text + ' '
                    #self.__shift_cusror_in_entry('right', 2)
                    #self.__cursor_reset_in_entry()
                    self.reset = False

                self.entry_value.set(text)
                self.sizer.configure(text=text)







    # @TODO: wenn sich das entry updaten schauen, ob es weniger als bspw 4 leerzeichen am anfang hat, wenn schon, dann füge so viele hinzu, dass es 4 sind


if __name__ == '__main__':
    root = ctk.CTk()
    root.geometry('+700+500')

    xpando = EntryExpanding(root, start_text='hey')
    xpando.place(relx=0.5)

    ordinary = ctk.CTkEntry(root)
    ordinary.place(relx=0.5, rely=0.5)

    root.mainloop()