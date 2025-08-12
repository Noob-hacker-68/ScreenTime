import psutil, time, json, os
from datetime import datetime
import win32gui, win32process

DATA_FILE = "E:\Code\gpt code\screen time\Github\screen_time_log.json"
CHECK_INTERVAL = 5  # seconds (sampling every 5s for better accuracy)  # seconds
SAVE_INTERVAL = 30  # seconds

# Load previous data or initialize fresh
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {}

# Save data
def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

# Get current date string
def get_today():
    return datetime.now().strftime('%Y-%m-%d')

# Get name of active window's process
def get_active_process_name():
    try:
        hwnd = win32gui.GetForegroundWindow()
        if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd):
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            return psutil.Process(pid).name()
    except:
        return None

# Main screen-time tracking
def main():
    all_data = load_data()
    today = get_today()
    # Initialize today's entry if missing
    if today not in all_data:
        all_data[today] = {}
    day_data = {}
    last_save = time.time()

    print(f"Tracking started for {today}. Ctrl+C to stop.")

    try:
        while True:
            # Check date rollover
            current = get_today()
            if current != today:
                # Save previous day
                for app, secs in day_data.items():
                    all_data[today][app] = all_data[today].get(app, 0) + secs
                save_data(all_data)
                print(f"{today} data saved. Starting new day {current}.")
                # Reset for new day
                today = current
                all_data[today] = {}
                day_data = {}
                last_save = time.time()

            # Track active app
            active_proc = get_active_process_name()
            if active_proc:
                day_data[active_proc] = day_data.get(active_proc, 0) + CHECK_INTERVAL

            # Periodic save
            if time.time() - last_save >= SAVE_INTERVAL:
                for app, secs in day_data.items():
                    all_data[today][app] = all_data[today].get(app, 0) + secs
                save_data(all_data)
                day_data = {}
                last_save = time.time()
                print(f"[Auto-Save] {today} usage saved.")

            time.sleep(CHECK_INTERVAL)

    except KeyboardInterrupt:
        # Final save on exit
        for app, secs in day_data.items():
            all_data[today][app] = all_data[today].get(app, 0) + secs
        save_data(all_data)
        print("Tracking stopped. Final data saved.")

if __name__ == "__main__":
    main()
