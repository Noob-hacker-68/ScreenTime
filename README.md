# ScreenTime
A screen time tracker for your windows, you can view your daily screen time in charts, set time limits, select which apps to track and which not

Tracks the apps only when in foreground and updates them every 5 seconds

Helping you set it up
Open the "screen time viewer.pyw" in any IDE and select the apps to track in the TRACKED_APPS LIST [Use same name as you may see in the .json file, you need to run the apps for a few seconds in the front to make them show up in the .json file, then pick the whole name including .exe]
Set App limits in the APP_LIMITS LIST
Set alias for processes in the FRIENDLY_NAMES LIST
[MOST IMPORTANT]Specify the file location in the DATA_FILE variable in both "screen time logger.pyw" and "screen time viewer.pyw"
You may, optionally, change the interval for updating the screen time on screen using the REFRESH_INTERVAL variable

You can add the shortcut for "screen time logger.pyw" to run every time your pc boots by copying it into the startup folder by opening the run dialog box (Win + R) and typing "shell:startup", this will open the startup folder
