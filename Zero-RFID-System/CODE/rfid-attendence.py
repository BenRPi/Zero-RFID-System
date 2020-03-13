import lcddriver
import SimpleMFRC522
import datetime
import time
import socket
import RPi.GPIO as GPIO
from squid import *
from button import button
import pickle
import os
import glob

led = Squid(18, 23, 24)
button = Button(17)
reader = SimpleMFRC522.SimpleMFRC522()
display = lcddriver.lcd()

display.lcd_clear()

mode = 'LISTEN'
allowed_tags = []

def handle_listen_mode():
    display.lcd_clear()
    global mode, allowed_tags
    led.set_color(GREEN)
    dispaly.lcd_display_string("Present Card:",1)
    id = reader.read_id_no_block()
    if id:
        if id in allowed_tags:
            display.lcd_clear()
            unlock_door()
        else:
            display.lcd_clear()
            print("Unknown Tag")
            display.lcd_display_string("Unknown Tag", 1)
            display.lcd_display_string("Please Try Again", 2)
            flash(RED, 5, 0.1)
            display.lcd_clear()
    if button.is_pressed():
        print("pressed")
        mode = 'GRANT'
    
def handle_grant_mode():
    global mode, allowed_tags
    led.set_color(CYAN)
    id = reader.read_id_no_block()
    if id and id not in allowed_tags:
        allowed_tags.append(id)
        save_tags()
        flash(GREEN, 1, 0.1)
    if button.is_pressed():
        mode = 'REVOKE'
        
def handle_revoke_mode():
    global mode
    led.set_color(PURPLE)
    id = reader.read_id_no_block()
    if id and id in allowed_tags:
        allowed_tags.remove(id)
        save_tags()
        flash(PURPLE, 1, 0.1)
    if button.is_pressed():
        mode = 'LISTEN'
        
def unlock_door():
    print("Door UNLOCKED")
    flash(GREEN, 10, 0.5)
    print("Door LOCKED")
    
def flash(color, times, delay):
    for i in range(0, times):
        led.set_color(color)
        time.sleep(delay)
        led.set_color(OFF)
        time.sleep(delay) 
        
def load_tags():
    global allowed_tags
    try:
        with open('allowed_tags.pickle', 'rb') as handle:
            allowed_tags = pickle.load(handle)
        print("Loaded Tags")
        print(allowed_tags)      
    except:
        pass
    
def save_tags():
    global allowed_tags
    print("Saving Tags")
    print(allowed_tags)
    with open('allowed_tags.pickle', 'wb') as handle:
        pickle.dump(allowed_tags, handle)

load_tags()
try:
    while True:
        if mode == "LISTEN":
            handle_listen_mode()
        elif mode == "GRANT":
            handle_grant_mode()
        elif mode == "REVOKE":
            handle_revoke_mode()
finally:
    print("cleaning up")
    GPIO.cleanup()
