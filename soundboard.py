import tkinter as tk
from tkinter import ttk, filedialog
import pygame
import json
import os
from typing import Dict

class Soundboard:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Soundboard")
        self.root.geometry("800x600")
        
        pygame.mixer.init()
        
        self.sounds: Dict[str, dict] = {}
        self.current_sound = None
        
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.buttons_frame = ttk.Frame(self.main_frame)
        self.buttons_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.load_keybinds()
        
        self.add_button = ttk.Button(self.main_frame, text="Add Sound", command=self.add_sound)
        self.add_button.grid(row=1, column=0, pady=10)
        
        self.root.bind('<Key>', self.on_key_press)
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(0, weight=1)
    
    def load_keybinds(self):
        try:
            with open('keybinds.json', 'r') as f:
                self.sounds = json.load(f)
                for sound_name, sound_data in self.sounds.items():
                    if 'volume' not in sound_data:
                        sound_data['volume'] = 1.0
                self.refresh_buttons()
        except FileNotFoundError:
            self.sounds = {}
    
    def save_keybinds(self):
        with open('keybinds.json', 'w') as f:
            json.dump(self.sounds, f)
    
    def add_sound(self):
        file_path = filedialog.askopenfilename(filetypes=[("MP3 files", "*.mp3")])
        if file_path:
            sound_name = os.path.basename(file_path)
            self.sounds[sound_name] = {
                'path': file_path,
                'key': str(len(self.sounds) + 1),
                'volume': 1.0 
            }
            self.save_keybinds()
            self.refresh_buttons()
    
    def delete_sound(self, sound_name):
        if self.current_sound == sound_name and pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
            self.current_sound = None
            
        if sound_name in self.sounds:
            del self.sounds[sound_name]
            self.save_keybinds()
            self.refresh_buttons()
    
    def play_sound(self, sound_name):
        if self.current_sound == sound_name and pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
            self.current_sound = None
        else:
            pygame.mixer.music.load(self.sounds[sound_name]['path'])
            volume = self.sounds[sound_name].get('volume', 1.0)
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play()
            self.current_sound = sound_name
    
    def change_keybind(self, sound_name):
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Change keybind for {sound_name}")
        dialog.geometry("300x100")
        
        ttk.Label(dialog, text="Press new key:").pack(pady=10)
        entry = ttk.Entry(dialog)
        entry.pack(pady=5)
        
        def on_key(event):
            self.sounds[sound_name]['key'] = event.char
            self.save_keybinds()
            self.refresh_buttons()
            dialog.destroy()
        
        entry.bind('<Key>', on_key)
        entry.focus()
    
    def update_volume(self, sound_name, volume):
        self.sounds[sound_name]['volume'] = volume
        self.save_keybinds()
        
        if self.current_sound == sound_name and pygame.mixer.music.get_busy():
            pygame.mixer.music.set_volume(volume)
    
    def refresh_buttons(self):
        for widget in self.buttons_frame.winfo_children():
            widget.destroy()
        
        for i, (sound_name, sound_data) in enumerate(self.sounds.items()):
            frame = ttk.Frame(self.buttons_frame)
            frame.grid(row=i, column=0, pady=5, sticky=(tk.W, tk.E))
            
            ttk.Label(frame, text=sound_name).grid(row=0, column=0, padx=5)
            
            play_btn = ttk.Button(
                frame,
                text=f"Play (Key: {sound_data['key']})",
                command=lambda sn=sound_name: self.play_sound(sn)
            )
            play_btn.grid(row=0, column=1, padx=5)
            
            keybind_btn = ttk.Button(
                frame,
                text="Change Keybind",
                command=lambda sn=sound_name: self.change_keybind(sn)
            )
            keybind_btn.grid(row=0, column=2, padx=5)
            
            delete_btn = ttk.Button(
                frame,
                text="Delete",
                command=lambda sn=sound_name: self.delete_sound(sn)
            )
            delete_btn.grid(row=0, column=3, padx=5)
            
            ttk.Label(frame, text="Volume:").grid(row=0, column=4, padx=(10, 0))
            
            volume_var = tk.DoubleVar(value=sound_data.get('volume', 1.0))
            volume_slider = ttk.Scale(
                frame,
                from_=0.0,
                to=1.0,
                orient="horizontal",
                variable=volume_var,
                length=100,
                command=lambda val, sn=sound_name: self.update_volume(sn, float(val))
            )
            volume_slider.grid(row=0, column=5, padx=5)
    
    def on_key_press(self, event):
        for sound_name, sound_data in self.sounds.items():
            if event.char == sound_data['key']:
                self.play_sound(sound_name)
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = Soundboard()
    app.run()