import tkinter as tk
from PIL import Image, ImageTk
import threading
import time
import pygame
import json
import os

# ===== Initialize pygame mixer =====
pygame.mixer.init()

# ===== Colors & Fonts =====
PRIMARY_COLOR = "#173c80"
BUTTON_COLOR = "#4E6EF2"
BUTTON_HOVER = "#5C7BFF"
TEXT_COLOR = "white"
FONT_NAME = "Press Start 2P"
EYE_COLORS = ["blue", "green", "brown", "gray", "red"]

EYE_QUOTES = [
    "Ocean",
    "Olive",
    "Almond",
    "Cloudy",
    "incase you're a vampire",
]

CONFIG_FILE = "config.json"

stop_event = threading.Event()


def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    else:
        return {"eye_color": "blue"}

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f)

config = load_config()


def show_popup(root):
    if stop_event.is_set():
        return

    popup = tk.Toplevel()
    popup.title("Eye Care")
    popup.configure(bg=PRIMARY_COLOR)
    popup.attributes("-topmost", True)

    w, h = 400, 250
    x = (popup.winfo_screenwidth() // 2) - (w // 2)
    y = (popup.winfo_screenheight() // 2) - (h // 2)
    popup.geometry(f"{w}x{h}+{x}+{y}")


    closed_eye = Image.open(f"images/closed.png")
    closed_eye = closed_eye.resize((100, 100))
    closed_photo = ImageTk.PhotoImage(closed_eye)

    eye_label = tk.Label(popup, image=closed_photo, bg="#173c80")
    eye_label.image = closed_photo
    eye_label.pack(pady=10)

    tk.Label(popup, text="🔔 Close your eyes!", font=(FONT_NAME, 10),
            bg=PRIMARY_COLOR, fg="white").pack(pady=10)

    countdown_label = tk.Label(popup, text="20", font=(FONT_NAME, 14), bg=PRIMARY_COLOR, fg="white")
    countdown_label.pack(pady=10)

    def countdown(seconds):
        if stop_event.is_set():
            popup.destroy()
            return
        if seconds >= 0:
            countdown_label.config(text=str(seconds))
            popup.after(1000, countdown, seconds - 1)
        else:
            pygame.mixer.Sound("Resources/blip.mp3").play()
            popup.destroy()

    countdown(3)

def eye_care_loop(root, interval=10):
    stop_event.clear()
    elapsed = 0
    while not stop_event.is_set():
        time.sleep(0.1)
        elapsed += 0.1
        if elapsed >= interval:
            elapsed = 0
            if stop_event.is_set():
                break
            root.after(0, show_popup, root)


def create_app():
    root = tk.Tk()
    root.title("Ya3yoni")
    root.configure(bg=PRIMARY_COLOR)
    root.geometry("400x300")
    
    app_running = False
    current_eye_color = tk.StringVar(value=config.get("eye_color", "blue"))
    
    # ===== MAIN FRAME =====
    main_frame = tk.Frame(root, bg=PRIMARY_COLOR)
    main_frame.pack(fill="both", expand=True)

    eye_img = Image.open(f"images/{current_eye_color.get()}.png").resize((100,100))
    eye_photo = ImageTk.PhotoImage(eye_img)
    eye_label = tk.Label(main_frame, image=eye_photo, bg=PRIMARY_COLOR)
    eye_label.image = eye_photo
    eye_label.pack(pady=10)

    def update_main_eye_image():
        img = Image.open(f"images/{current_eye_color.get()}.png").resize((100,100))
        photo = ImageTk.PhotoImage(img)
        eye_label.config(image=photo)
        eye_label.image = photo

    # ===== START/STOP Button =====
    def start_app():
        nonlocal app_running
        if not app_running:
            pygame.mixer.Sound("Resources/computer-mouse-click.mp3").play()
            app_running = True
            start_button.config(text="STOP")
            
            status_label.config(text="")   
            status_label.fixed = None        
            
            stop_event.clear()
            threading.Thread(
                target=lambda: eye_care_loop(root, interval=10), 
                daemon=True
            ).start()
            root.iconify()

        else:
            pygame.mixer.Sound("Resources/computer-mouse-click.mp3").play()
            app_running = False
            start_button.config(text="START")

            stop_event.set()
            root.deiconify()

            stop_click_message()


    start_button = tk.Button(
        main_frame, 
        text="START", 
        font=(FONT_NAME, 6),
        bg=BUTTON_COLOR, 
        fg=TEXT_COLOR, 
        activebackground=BUTTON_HOVER,
        activeforeground=TEXT_COLOR, 
        bd=3,               
        relief="raised",    
        command=start_app
    )
    start_button.pack(pady=10)

    status_label = tk.Label(main_frame, text="", fg="white", bg=PRIMARY_COLOR, font=(FONT_NAME, 6))
    status_label.pack(pady=5)
    status_label.fixed = None  

    def stop_hover_enter(event):
        if app_running: 
            status_label.config(text="Don't you dare click it!")
            
    def stop_hover_leave(event):
        if status_label.fixed is None:
            status_label.config(text="")

    def stop_click_message():
        status_label.config(text="You'll come back crying soon..")
        status_label.fixed = "You'll come back crying soon.."

    start_button.bind("<Enter>", stop_hover_enter)
    start_button.bind("<Leave>", stop_hover_leave)


    # ===== SETTINGS FRAME =====
    settings_frame = tk.Frame(root, bg=PRIMARY_COLOR)
    
    def back_to_main_from_settings():
        pygame.mixer.Sound("Resources/computer-mouse-click.mp3").play()
        settings_frame.pack_forget()
        main_frame.pack(fill="both", expand=True)

    back_button_settings = tk.Button(settings_frame, text="← Back", font=(FONT_NAME, 6),
                            bg=PRIMARY_COLOR, fg=TEXT_COLOR, bd=0,
                            activebackground=PRIMARY_COLOR, command=back_to_main_from_settings)
    back_button_settings.pack(anchor="nw", padx=5, pady=5)

    tk.Label(settings_frame, text="Select your eye color:", font=(FONT_NAME,7),
            bg=PRIMARY_COLOR, fg=TEXT_COLOR).pack(pady=10)

    index = EYE_COLORS.index(current_eye_color.get())
    eye_img_settings = Image.open(f"images/{EYE_COLORS[index]}.png").resize((100,100))
    eye_photo_settings = ImageTk.PhotoImage(eye_img_settings)
    eye_label_settings = tk.Label(settings_frame, image=eye_photo_settings, bg=PRIMARY_COLOR)
    eye_label_settings.image = eye_photo_settings
    eye_label_settings.pack(pady=5)

    eye_color_text = tk.StringVar(value=EYE_QUOTES[index])
    tk.Label(settings_frame, textvariable=eye_color_text, font=(FONT_NAME,6),
            bg=PRIMARY_COLOR, fg=TEXT_COLOR).pack(pady=10)

    def update_eye_image(i):
        nonlocal index, eye_photo_settings
        index = i % len(EYE_COLORS)
        img = Image.open(f"images/{EYE_COLORS[index]}.png").resize((100,100))
        photo = ImageTk.PhotoImage(img)
        eye_label_settings.config(image=photo)
        eye_label_settings.image = photo
        current_eye_color.set(EYE_COLORS[index])
        eye_color_text.set(EYE_QUOTES[index])

    def next_pic():
        pygame.mixer.Sound("Resources/select-sound.mp3").play()
        update_eye_image(index+1)
    def prev_pic():
        pygame.mixer.Sound("Resources/select-sound.mp3").play()
        update_eye_image(index-1)

    nav_frame = tk.Frame(settings_frame, bg=PRIMARY_COLOR)
    nav_frame.pack(pady=5)
    tk.Button(nav_frame, text="⬅ Prev", font=(FONT_NAME,6),
            bg=BUTTON_COLOR, fg=TEXT_COLOR, command=prev_pic).pack(side="left", padx=10)
    tk.Button(nav_frame, text="Next ➡", font=(FONT_NAME,6),
            bg=BUTTON_COLOR, fg=TEXT_COLOR, command=next_pic).pack(side="right", padx=10)

    # ===== Back & Save buttons (Settings) =====
    def save_settings():
        pygame.mixer.Sound("Resources/save.mp3").play()
        update_main_eye_image()
        config["eye_color"] = current_eye_color.get()
        save_config(config)

    save_button_settings = tk.Button(settings_frame, text="💾 Save", font=(FONT_NAME,6),
                            bg="#364B73", fg="white", command=save_settings)
    save_button_settings.pack(pady=5)

    # ===== INFO FRAME =====
    info_frame = tk.Frame(root, bg=PRIMARY_COLOR)
    
    def back_to_main_from_info():
        pygame.mixer.Sound("Resources/computer-mouse-click.mp3").play()
        if info_channel is not None:
            info_channel.stop()
        info_frame.pack_forget()
        main_frame.pack(fill="both", expand=True)


    back_button_info = tk.Button(info_frame, text="← Back", font=(FONT_NAME,6),
                            bg=PRIMARY_COLOR, fg=TEXT_COLOR, bd=0,
                            activebackground=PRIMARY_COLOR, command=back_to_main_from_info)
    back_button_info.pack(anchor="nw", padx=5, pady=5)

    tk.Label(info_frame, text="Ya3yoni", font=(FONT_NAME,12),
            bg=PRIMARY_COLOR, fg=TEXT_COLOR).pack(pady=10)
    tk.Label(info_frame, text="Version 1.0", font=(FONT_NAME,8),
            bg=PRIMARY_COLOR, fg=TEXT_COLOR).pack(pady=5)

    tk.Label(
        info_frame,
        text="- this app was made for your deadly brain that forgets to blink, playing staring contests with your computer.\n\nAnd no, those 20 seconds of closing your eyes still won’t finish the task you’ve been avoiding until the deadline… but at least your eyes won’t suffer for it.\n\nSo here I am solving a problem you didn’t even know you had.\n\nyou’re welcome\n\nCredits: Arwa Mohamed", 
        justify="left",
        wraplength=250, 
        font=(FONT_NAME, 8),
        bg=PRIMARY_COLOR, 
        fg=TEXT_COLOR
    ).pack(pady=(10, 5))

    info_sound = pygame.mixer.Sound("Resources/beat-effect.mp3")
    info_channel = None

    def open_info():
        pygame.mixer.Sound("Resources/computer-mouse-click.mp3").play()
        nonlocal info_channel
        main_frame.pack_forget()
        info_frame.pack(fill="both", expand=True)
        info_channel = info_sound.play(-1)


    # ===== Navigation Buttons on main =====
    def open_settings():
        pygame.mixer.Sound("Resources/computer-mouse-click.mp3").play()
        main_frame.pack_forget()
        settings_frame.pack(fill="both", expand=True)

    tk.Button(main_frame, text="⚙️ Settings", font=(FONT_NAME,6),
            bg=PRIMARY_COLOR, fg=TEXT_COLOR, bd=0,
            activebackground=PRIMARY_COLOR, command=open_settings).pack()

    tk.Button(main_frame, text="? Info", font=(FONT_NAME,6),
            bg=PRIMARY_COLOR, fg=TEXT_COLOR, bd=0,
            activebackground=PRIMARY_COLOR, command=open_info).pack()

    return root

# ===== Run App =====
if __name__ == "__main__":
    root = create_app()
    root.mainloop()