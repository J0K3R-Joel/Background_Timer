import time
import customtkinter


timer_app = customtkinter.CTk()
timer_app.geometry("800x1200")

content_site = customtkinter.CTkFrame(timer_app)
mode_site = customtkinter.CTkFrame(timer_app)


# ==================================
# ============= MODE ===============
# ==================================

timer_button_mode = customtkinter.CTkButton(mode_site, text="Timer")




timer_label_content = customtkinter.CTkLabel(content_site, text="Timer")