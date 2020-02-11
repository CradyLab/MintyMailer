#! /usr/local/bin/python
#
#
#
#	MIT License Copyright (c)2017 Crady von Pawlak
#
#	Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
#	The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
#	THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
#	This work is also licensed under a Creative Commons Attribution-NonCommercial 4.0 International License
#	https://creativecommons.org/licenses/by-nc/4.0/
#
#
#	MintyMailer(CC)2017 Crady von Pawlak / CradyLab(tm)
#	rel 1.0
#	Written in Python 3 for Raspberry Pi in Raspbian Jessie with Pixel
#	Developed with Raspberry Pi 3 Model B v1.2 and Raspberry Pi Zero with Red Bear IoT pHAT
#	Tested with Turnigy REAKTOR 300W 20A and IMAX B6 balance chargers from HobbyKing.com
#
#
#	To launch the script on boot-up, place it in the Documents folder and then add the following to the last line of the .bashrc file:
#	python Documents/charger_alerts.py
#	
#	
#	Usage:
#	
#	Pin 7 of the Raspberry Pi (GPIO 4) is configured as an input and connected to the (+) side of a battery charger's
#	piezoelectric alarm buzzer.  When the buzzer is silent GPIO 4 sees a LOW. Any 'beep' from the buzzer is conversely
#	seen as a HIGH.
#
#	The script works by looking for these state changes and any transition from LOW to HIGH is considered
#	an 'event'.  Once an event is detected an email is sent, the LED is lit continuously and all subsequent events (i.e.
#	continuous beeping) are ignored until the START/RESET button is pressed.
#
#	After Loading
#
#	When the script is first run the LED will slowly flash 5 times to indicate it has successfully loaded.  After that the
#	LED will remain OFF until the START/RESET button has been pressed.
#
#	To work correctly, START/RESET must not be pressed until the charger has started a cycle.  This is because most LiPo
#	chargers beep with each key press - something that would be seen as an event and cause a false trigger (note that the
#	alerter cannot work if the charger's alarm has been silenced.)
#
#	After the battery charger's cycle has started (balance, fast charge, discharge, etc.) it's time to press the START/RESET
#	button.  The LED will then blink continuously once every 2 seconds to show the script is actively waiting for an event.
#
#	When an event has been detected the LED will go ON, and then flash rapidly to indicate an email is in the process of
#	being sent.  Once an email is sent the LED will then remain ON until the START/RESET button is pressed again.
#
#	Test Emails
#
#	After the script has loaded you can trigger an event and force the script to send an email by pressing the TEST button.
#



import smtplib
from email.mime.text import MIMEText

import sys
from time import sleep

import os, RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)


# define GPIO pins
GPIO.setup(2,GPIO.IN) # Physical pin 3 (has internal 1.8K pullup resistor) - START / RESET button
GPIO.setup(4,GPIO.IN,pull_up_down=GPIO.PUD_DOWN) # Physical pin 7 - SIGNAL connect to (+) of piezo buzzer
GPIO.setup(20,GPIO.IN,pull_up_down=GPIO.PUD_UP) # Physical pin 38 - TEST button
GPIO.setup(21,GPIO.OUT) # Physical pin 40 - LED anode via 1K resistor


# ChargerState values
# 0 = Awaiting START / RESET press
# 1 = Awaiting event
# 2 = Email sent
# 3 = dummy value to keep loop going
ChargerState = 0

Heartbeat = 0

GPIO.output(21,0) # Set LED to 'off' state



############################################## Emailer

# define email content
recipients = ["SomeEmailAddress@somedomain.com"] # Recipient email addresses
sender = "SomeEmailAddress@somedomain.com" # Sender email address
subject = "LiPo Charger"
body = """
Cycle completed.


=)

"""
msg = MIMEText(body)
msg['Subject'] = subject
msg['From'] = sender
msg['To'] = ", ".join(recipients)

# Send email function
def SendAlert():
    session = smtplib.SMTP('smtp.gmail.com', 587) # Email server (Gmail as example)
    session.starttls()
    session.login(sender, 'YourEmailPassword') # Email password
    send_it = session.sendmail(sender, recipients, msg.as_string())
    session.quit()
    return

############################################## Emailer



# LED heartbeat
def DoHeartbeat():
    global ChargerState
    if (ChargerState != 1):
        sleep(0.15)
        return
    else:
        global Heartbeat
        if (Heartbeat == 14): # Briefly flash LED approx. every 2S
            GPIO.output(21,1)
            sleep(0.06) # LED on for 60ms
            GPIO.output(21,0)
            Heartbeat = 0
    sleep(0.15)
    Heartbeat = Heartbeat + 1
    return


# Flash LED at 2Hz
def Flash_LED_At_2Hz():
    LED_blinks = 0
    while(LED_blinks < 5): # Briefly flash LED at 2Hz
        GPIO.output(21,1)
        sleep(0.5)
        GPIO.output(21,0)
        sleep(0.5)
        LED_blinks = LED_blinks + 1
    GPIO.output(21,0) # Leave LED OFF
    return


# Flash LED at 10Hz
def Flash_LED_At_10Hz():
    LED_blinks = 0
    while(LED_blinks < 5): # Briefly flash LED at 10Hz
        GPIO.output(21,1)
        sleep(0.1)
        GPIO.output(21,0)
        sleep(0.1)
        LED_blinks = LED_blinks + 1
    GPIO.output(21,0) # Leave LED OFF
    return


# Flash LED at 30Hz
def Flash_LED_At_30Hz():
    LED_blinks = 0
    while(LED_blinks < 15): # briefly flash LED at 30Hz
        GPIO.output(21,1)
        sleep(0.033)
        GPIO.output(21,0)
        sleep(0.033)
        LED_blinks = LED_blinks + 1
    GPIO.output(21,1) # Leave LED ON
    return


# Exit function - unloads program
def KillTheScript():
    Flash_LED_At_30Hz() # Flash LED quickly so we know exit has started
    GPIO.output(21,0) # Turn off LED
    print ("Charger emailer terminated")
    sys.exit() # Exit script


Flash_LED_At_2Hz() # Slowly blink the LED 5 times to indicate program is loaded and ready
print ("Emailer loaded. Press START when charger cycle has begun.")




while ChargerState != 3: # Loop indefinitely

    if (GPIO.input(4) == 1): # Detect if piezo buzzer energized
        if (ChargerState == 1): # Test program the status
            GPIO.output(21,1) # Turn on LED to show email is sending
            SendAlert() # Send email
            ChargerState = 2 # Update status to 'Email sent'
            print ("Email sent")
            Flash_LED_At_30Hz() # Indicate email has been sent then stay on until reset

    #elif (GPIO.input(2) == 0 and GPIO.input(20) == 1 and ChargerState == 0): # START / RESET has been pressed
            #ChargerState = 1 # Update status to 'Awaiting event'
            #Flash_LED_At_10Hz() # Flash LED
            #print ("Started. Awaiting event ...")

    elif (GPIO.input(2) == 0 and GPIO.input(20) == 1 and ChargerState != 1): # START / RESET has been pressed
            ChargerState = 1 # Update status to 'Awaiting event'
            Flash_LED_At_10Hz() # Flash LED
            print ("Reset. Awaiting event ...")

    elif (GPIO.input(20) == 0 and GPIO.input(2) == 1): # TEST button has been pressed
            GPIO.output(21,1) # Turn on LED to show email is sending
            SendAlert() # Send test email
            ChargerState = 2 # Update status to 'Email sent'
            print ("Test email sent")
            Flash_LED_At_30Hz() # Indicate an email has been sent then stay on until reset

    elif (GPIO.input(20) == 0 and GPIO.input(21) == 0): # Both buttons are being pressed simultaneously
                                                        # (press and hold RESET then TEST buttons)
            print ("Hold BOTH buttons until LED is off")
            GPIO.output(21,0) # Turn on LED off
            #ChargerState = 3
            KillTheScript()

    else: DoHeartbeat() # Nothing happening? Pause for 150ms to reduce CPU load then resume loop


#    That's it! =)
