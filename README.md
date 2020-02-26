# Raspberry Pi Zero Sends Emails On Hardware Event
A simple app for the Raspberry Pi Zero that monitors external hardware for an event and then sends an email alert when it occurs 

## Watch The [Complete Video Tutorial](https://youtu.be/7OaZsSdVpSQ)

![](images/mintymailer_yt_thumbnail_1200x675.jpg)

###### The Basics

Pin 7 of the Raspberry Pi (GPIO 4) is configured as an input and connected to the (+) side of a battery charger's
piezoelectric alarm buzzer.  When the buzzer is silent GPIO 4 sees a LOW. Any 'beep' from the buzzer is conversely
seen as a HIGH

![Wiring Diagram]("images/diagram800x800.png" width=800 height=800)

The script works by looking for these state changes and any transition from LOW to HIGH is considered
an 'event'.  Once an event is detected an email is sent, the LED is lit continuously and all subsequent events (i.e.
continuous beeping by the charger) are ignored until the START/RESET button is pressed

###### After Loading

When the script is first run the LED will slowly flash 5 times to indicate it has successfully loaded.  After that the
LED will remain OFF until the START/RESET button has been pressed

To work correctly, START/RESET must not be pressed until the charger has started a cycle.  This is because most LiPo
chargers beep with each key press - something that would be seen as an event and cause a false trigger (note that the
alerter cannot work if the charger's alarm has been silenced.)

After the battery charger's cycle has started (balance, fast charge, discharge, etc.) it's time to press the START/RESET
button.  The LED will then blink continuously once every 2 seconds as a heartbeat to show the script is actively waiting for
an event

When an event has been detected the LED will go ON, and then flash rapidly to indicate an email is in the process of
being sent.  Once an email is sent the LED will then remain ON (steady state) until the START/RESET button is pressed again

###### Test Emails

After the script has finished loading you can trigger an event and force the script to send an email by pressing the TEST button

###### Unloading

You can exit the script by pressing and holding the RESET then TEST buttons simultaneously until the LED begins to flash rapidly.
After that the script will have unloaded and you can release the buttons
