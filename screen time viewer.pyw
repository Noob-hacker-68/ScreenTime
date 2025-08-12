import tkinter as tk
from tkinter import ttk
import json, os
from datetime import datetime
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import psutil
import win32gui, win32process
import threading

# 👉 Edit these lists to track and customize apps
TRACKED_APPS = [
    "explorer.exe",
    "Cities.exe",
    "MarvelRivalsClient.exe",
    "MarvelRivals_Launcher.exe",
    "steam.exe",
    "EpicGamesLauncher.exe",
    "brave.exe",
    "msedge.exe",
    "acrobat.exe",
    "Telegram.exe",
    "Whatsapp.exe",
    "settings.exe",
    "conhost.exe",
    "Code.exe",
    "Notepad.exe",
    "EXCEL.EXE",
    "Marvel-Win64-Shipping.exe",
    "SGWContracts.exe",
    "AC4BFSP.exe",
    "ACValhalla_Plus.exe",
    "arpanet.exe",
    "HoustonProblem.exe",
    "unicode.exe",
    "amd.exe",
    "intel.exe",
    "People2MoonIn4KBram.exe"
]
# Timer limits in seconds: app.exe -> max seconds before popup
APP_LIMITS = {
    "brave.exe": 60 * 60,          # Brave 
    "Marvel-Win64-Shipping.exe": 60 * 60,
    "Cities.exe": 30 * 60,
    "SGWContracts.exe": 30 * 60,
    "AC4BFSP.exe": 60 * 60,
    "ACValhalla_Plus.exe": 60 * 60,
    "Pilgrims.exe" : 60 * 60
  # "steam.exe": 60 * 60,       # Steam → 1 hour
}
# Friendly display names: app.exe -> label
FRIENDLY_NAMES = {
    "brave.exe": "Brave",
    "Code.exe" : "VS Code",
    "conhost.exe" : "cmd",
    "Cities.exe" : "Cities Skylines",
    "MarvelRivalsClient.exe" : "Marvel Rivals",
    "MarvelRivals_Launcher.exe" : "Rivals Launcher",
    "EpicGamesLauncher.exe" : "Epic Games",
    "EXCEL.EXE" : "Excel",
    "Marvel-Win64-Shipping.exe" : "Marvel Rivals",
    "SGWContracts.exe" : "Sniper Ghost",
    "AC4BFSP.exe" : "AC Black Flag",
    "ACValhalla_Plus.exe" : "AC Vallhalla",
    # "steam.exe": "Steam Client",
}

DATA_FILE = "E:/Code/gpt code/screen time/Github/screen_time_log.json"
REFRESH_INTERVAL = 5  # seconds for UI refresh and file watch

plt.style.use('dark_background')

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {}

# Popup warning window
def show_warning(app, time_spent):
    popup = tk.Toplevel()
    popup.title("⚠️ Time Alert")
    popup.configure(bg="black")
    popup.geometry("500x250+700+400") # Bigger popup, centerish
    popup.attributes('-topmost', True)
    popup.attributes('-alpha', 0.95)
    
    msg = f"⏰ You've used\\n{FRIENDLY_NAMES.get(app, app.replace('.exe',''))}\\nfor {time_spent//60} minutes!"
    label = tk.Label(popup, text=msg, font=("Segoe UI", 18, "bold"), fg="orange", bg="black", justify='center')
    label.pack(expand=True, padx=30, pady=30)
    
    popup.after(30000, popup.destroy) # Lasts 30 seconds

def format_time(seconds):
    """Convert seconds to human-readable format"""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        secs = seconds % 60
        if secs > 0:
            return f"{minutes}m {secs}s"
        return f"{minutes}m"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        if minutes > 0:
            return f"{hours}h {minutes}m"
        return f"{hours}h"

class ScreenTimeUI:
    def _alert_watcher_loop(self):
        while True:
            try:
                self.data = load_data()
                today = datetime.now().strftime('%Y-%m-%d')
                today_data = self.data.get(today, {})
                
                for app, limit in APP_LIMITS.items():
                    used = today_data.get(app, 0)
                    if used >= limit and app not in self.alerted:
                        self.root.after(0, show_warning, app, used)
                        self.alerted.add(app)
            except Exception:
                pass
            time.sleep(10)

    def __init__(self):
        self.root = tk.Tk()
        self.root.iconbitmap("E:/Code/gpt code/screen time/screen time app.ico")
        self.root.title("Screen Time Tracker")
        self.root.configure(bg="black")
        self.root.geometry("1920x1080")

        # Total screen time display at the very top
        total_frame = tk.Frame(self.root, bg="black")
        total_frame.pack(fill='x', padx=10, pady=(10, 0))
        
        self.total_time_label = tk.Label(total_frame, text="Total Screen Time: 0h 0m", 
                                       font=("Arial", 16, "bold"), fg="#00FFFF", bg="black")
        self.total_time_label.pack()

        # Top bar with dropdown
        top = tk.Frame(self.root, bg="#2F4F4F") # dark slate grey for subtle top bar
        top.pack(fill='x', pady=(5, 0))
        
        self.selected_day = tk.StringVar()
        self.dropdown = ttk.Combobox(top, textvariable=self.selected_day, font=("Arial", 14))
        self.dropdown.pack(pady=(10,0), padx=10)
        self.dropdown.bind("<<ComboboxSelected>>", lambda e: self.update_display())

        # Chart area
        self.fig, self.ax = plt.subplots(figsize=(12,6))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack(fill='both', expand=True, pady=(0,10))

        # State
        self.data = {}
        self.last_mtime = 0
        self.alerted = set()
        
        self.update_dates()
        self.root.after(REFRESH_INTERVAL*1000, self.schedule_refresh)
        self.root.bind("<Escape>", lambda e: self.root.destroy())

        # Start continuous alert checker thread
        threading.Thread(target=self._alert_watcher_loop, daemon=True).start()
        
        self.root.mainloop()

    def update_dates(self):
        self.data = load_data()
        dates = sorted(self.data.keys())
        self.dropdown['values'] = dates
        if dates and not self.selected_day.get():
            self.selected_day.set(dates[-1])
        self.update_display()

    def update_display(self):
        day = self.selected_day.get()
        if not day:
            return
            
        day_data = self.data.get(day, {})
        
        # Calculate total time for ALL processes in the JSON
        total_seconds = sum(day_data.values())
        
        # Update the total time label
        self.total_time_label.config(text=f"Total Screen Time: {format_time(total_seconds)}")
        
        self.draw_chart()

    def update_dashboard(self):
        self.data = load_data()
        dates = sorted(self.data.keys())
        self.dropdown['values'] = dates
        if dates and not self.selected_day.get():
            self.selected_day.set(dates[-1])

        # Update total label
        day = self.selected_day.get()
        total_secs = sum(self.data.get(day, {}).values())
        total_mins = total_secs // 60
        hrs = total_mins // 60
        mins = total_mins % 60
        total_text = f"Total: {hrs}h {mins}m" if hrs else f"Total: {mins}m"
        self.total_label.config(text=total_text)

        # Update total seconds label
        self.total_seconds_label.config(text=f"{total_secs}s")
        
        self.draw_chart()

    def draw_chart(self):
        day = self.selected_day.get()
        self.ax.clear()
        
        if not day:
            return
            
        day_data = self.data.get(day, {})
        
        apps = []
        times = []
        
        for proc, secs in day_data.items():
            if proc.lower() in [p.lower() for p in TRACKED_APPS]:
                apps.append(FRIENDLY_NAMES.get(proc, proc.replace('.exe','')))
                times.append(secs / 60)

        if not apps:
            self.ax.text(0.5, 0.5, 'No tracked app data for this day', 
                        transform=self.ax.transAxes, ha='center', va='center',
                        fontsize=14, color='white')
            self.canvas.draw()
            return

        self.ax.barh(apps, times, color='#00CED1', edgecolor='#008B8B')
        bars = self.ax.barh(apps, times, color='#00CED1', edgecolor='#008B8B')
        
        for bar in bars:
            width = bar.get_width()
            hrs = int(width) // 60
            mins = int(width) % 60
            label = f"{hrs}h {mins}m" if hrs else f"{mins}m"
            self.ax.text(width + 1, bar.get_y() + bar.get_height()/2, label, va='center', ha='left', fontsize=10, color='white')

        self.ax.set_xlabel("Minutes", color='white')
        self.ax.set_title(f"Screen Time on {day}", color='white')
        self.ax.tick_params(axis='x', colors='white')
        self.ax.tick_params(axis='y', colors='white')
        
        self.canvas.draw()

    def schedule_refresh(self):
        try:
            if os.path.exists(DATA_FILE):
                mtime = os.path.getmtime(DATA_FILE)
                if mtime != self.last_mtime:
                    self.last_mtime = mtime
                    self.update_dates()
                    self.check_alerts()
        except FileNotFoundError:
            pass
        self.root.after(REFRESH_INTERVAL*1000, self.schedule_refresh)

    def check_alerts(self):
        today = datetime.now().strftime('%Y-%m-%d')
        today_data = self.data.get(today, {})
        
        for app, limit in APP_LIMITS.items():
            used = today_data.get(app, 0)
            if used >= limit and app not in self.alerted:
                show_warning(app, used)
                self.alerted.add(app)

if __name__ == "__main__":
    ScreenTimeUI()