#!/usr/bin/env python2

import argparse
import evdev
import os
import signal
import sys
import time

from evdev import *
from evdev.ecodes import *
from select import select
from threading import Thread

from colorama import init, Fore, Back, Style
init(autoreset=True)
#Fore: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
#Back: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
#Style: DIM, NORMAL, BRIGHT, RESET_ALL

debug = False

# Device signatures list
keyboards = [
	[('EV_LED', 17), ('EV_MSC', 4), ('EV_KEY', 1), ('EV_SYN', 0)]
]
mice = [
	[('EV_KEY', 1), ('EV_REL', 2), ('EV_SYN', 0), ('EV_MSC', 4)],
	[('EV_KEY', 1), ('EV_REL', 2), ('EV_SYN', 0)]
]

def get_device(signature):
	devs = [InputDevice(dev) for dev in list_devices()]
	for dev in devs:
		try:
			if set(dev.capabilities(verbose=True).keys()) == set(signature):
				return dev
		except AttributeError:
			pass
	return None

def read(dev, key_abs_map, key_key_map):
	for event in dev.read_loop():
		if event.type == EV_KEY and (event.value == 0 or event.value == 1):
			if key_abs_map != None:
				if event.code in key_abs_map:
					axis = key_abs_map[event.code][0]
					direction = key_abs_map[event.code][1]	# Direction the axis moves
					sign = 2 * event.value - 1	# Key down (1) or up (-1)

					axis.move(direction * sign)

					ui.write(EV_ABS, axis.ABS, axis.state)
			if key_key_map != None:
				if event.code in key_key_map:
					button = key_key_map[event.code]

					ui.write(EV_KEY, button, event.value)
		if debug:
			if (event.type == SYN_REPORT or event.type == 4):
				pass
			else:
				print(categorize(event))
		ui.syn()

def relative(dev, rel_abs_map):
	highest = len(rel_abs_map)
	highest = 5
	last_time = time.time()

	targets = [0] * highest

	while True:
		this_time = time.time()
		dt = (this_time - last_time) # dt is the time delta in seconds (float).

		if int(dt * 1000) >= FRAME_TIME: 
			last_time = this_time

			deltas = [0] * highest
			while True: # Read mouse
				try:
					event = dev.read_one()

					if event.type == EV_REL:
						if event.code in rel_abs_map:
							axis = rel_abs_map[event.code][0]
							direction = rel_abs_map[event.code][1]
							deltas[event.code] += event.value

				except IOError:
					break

			sliders = [0] * highest
			for idx in rel_abs_map:
				axis = rel_abs_map[idx][0]
				direction = rel_abs_map[idx][1]
				delta = deltas[idx]
				slider = sliders[idx]
				target = targets[idx]

				target += delta * DEGREES_PER_MOUSE_DOT * direction
			
				if target > 0.0: # To the right
					if target < DEGREES_PER_FRAME:
						slider = int((JOY_MAX - JOY_THRESHOLD) * (target/DEGREES_PER_FRAME)) + JOY_THRESHOLD
						target = 0.0
					else: # Play catchup next frame because the joystick sensitivity can't keep up with the mouse sensitivity
						slider = JOY_MAX
						target -= DEGREES_PER_FRAME
				elif target < 0.0:
					if target > -DEGREES_PER_FRAME:
						slider = int((JOY_MAX - JOY_THRESHOLD) * (target/DEGREES_PER_FRAME)) - JOY_THRESHOLD
						target = 0.0
					else:
						slider = -JOY_MAX
						target += DEGREES_PER_FRAME;

				ui.write(EV_ABS, axis.ABS, slider)
			ui.syn()

		execution_time = (time.time() * 1000 - this_time * 1000)
		sleepTime = FRAME_TIME - execution_time
		if sleepTime > 0:
			time.sleep(sleepTime / 1000.0)

def signal_handler(signal, frame):
	print("Exiting...")
	ui.close()
	os._exit(0)
	#sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def get(provided, devicelist):
	if provided != None:
		return InputDevice(provided)
	for device in devicelist:
		dev = get_device(device)
		if dev is not None:
			return dev

parser = argparse.ArgumentParser(description="Maps keyboard and mouse input to a virtual joystick")
parser.add_argument('-c', '--config', action='store', type=str, required=True, help="Python script with joystick mappings.")
parser.add_argument('-s', '--sensitivity', action='store', type=float, required=True, help="Sensitivity from TF2.")
parser.add_argument('-m', '--mouse', action='store', type=str, help="Mouse device. By default, the script attempts to find the mouse in /dev/input/event*.")
parser.add_argument('-k', '--keyboard', action='store', type=str, help="Keyboard device. By default, the script attempts to find the keyboard in /dev/input/event*.")	
parser.add_argument('-a', '--adjustment', action='store', type=float, default=1.0, help="Sensitivity adjustment factor. Default: 1.0")
parser.add_argument('-f', '--fps', action='store', type=int, default=100, help="Frame rate of script (how often it updates the joystick). Default: 60")
parser.add_argument('--joy_yawsensitivity', action='store', default=50.0, type=float, help="joy_yawsensitivity from TF2. Default: 50")
parser.add_argument('--joy_yawthreshold', action='store', default=0.2, type=float, help="joy_yawthreshold from TF2. Default: 0.2")
parser.add_argument('--cl_yawspeed', action='store', type=float, default=210.0, help="cl_yawspeed from TF2. Default: 210")
parser.add_argument('--m_yaw', action='store', type=float, default=0.022, help="m_yaw from TF2. Default: 0.022")
args = parser.parse_args()

# Set constants
JOY_MAX = 32767

FPS = args.fps
FRAME_TIME = 1000 / FPS
JOY_YAWSENSITIVITY = args.joy_yawsensitivity
CL_YAWSPEED = args.cl_yawspeed
SENSITIVITY = args.sensitivity
M_YAW = args.m_yaw
ADJUSTMENT = args.adjustment

DEGREES_PER_MOUSE_DOT = SENSITIVITY  * M_YAW;
DEGREES_PER_FRAME = FRAME_TIME * JOY_YAWSENSITIVITY * CL_YAWSPEED / 1000.0;
JOY_THRESHOLD = int(JOY_MAX * args.joy_yawthreshold)

# Trim .py from config if it was included.
if args.config[-3:] == '.py': args.config = args.config[:-3]

config = __import__(args.config)

ui = UInput(config.CAPABILITIES, name=config.NAME, vendor=config.VENDOR, product=config.PRODUCT, version=config.VERSION, bustype=BUS_USB)
for axis in config.AXES: # Initialize axis positions.
	ui.write(EV_ABS, axis.ABS, axis.state)
	ui.syn()
	print(str(axis.ABS) + ' = ' + str(axis.state))

dev_kb = get(args.keyboard, keyboards)
print(Style.BRIGHT + Fore.YELLOW + "keyboard: " + str(dev_kb))

if dev_kb != None:
	thread_kb = Thread(target=read, args=[dev_kb, config.key_to_abs_map, config.key_to_key_map]).start()

dev_mouse = get(args.mouse, mice)
print(Style.BRIGHT + Fore.YELLOW + "mouse: " + str(dev_mouse))

if dev_mouse != None:
	#thread_mouse = Thread(target=read, args=[dev_mouse, config.mouse_key_to_abs_map, config.mouse_key_to_key_map]).start()
	relative(dev_mouse, config.mouse_rel_to_abs_map)

