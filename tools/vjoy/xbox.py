#!/usr/bin/env python
#
# Configuration file to specify key to button or axis mappings.
#
# Key and button codes can be found here:
# http://gvalkov.github.com/python-evdev/moduledoc.html#module-evdev.ecodes
# here:
# http://pythonhosted.org/evdev/moduledoc.html#module-evdev.ecodes
# or here:
# http://www.cs.fsu.edu/~baker/devices/lxr/http/source/linux/include/linux/input.h?v=2.6.11.8
#
# Axes are LEFT_STICK_X, LEFT_STICK_Y, RIGHT_STICK_X, RIGHT_STICK_Y, LEFT_TRIGGER, and RIGHT_TRIGGER.
#
# Leave these lines alone.
from evdev.ecodes import *
from constants import *

NAME='Xbox 360 Wireless Receiver'
VENDOR=0x45e
PRODUCT=0x719
VERSION=0x100

CAPABILITIES = {
	EV_KEY : [
		BTN_A, # A
		BTN_B, # B
		BTN_X, # X
		BTN_Y, # Y
		BTN_TL, # LB
		BTN_TR, # RB
		BTN_SELECT, # Back
		BTN_START, # Start
		BTN_MODE, # Guide
		BTN_THUMBL, # LS
		BTN_THUMBR, # RS
		704, # Dpad left
		705, # Dpad right
		706, # Dpad up
		707, # Dpad down
	],
	EV_ABS : [
		(ABS_X,  (-32767, 32767, 0, 0)), # min, max, fuzz, flat
		(ABS_Y,  (-32767, 32767, 0, 0)),
		(ABS_Z,  (-32767, 32767, 0, 0)),
		(ABS_RX, (-32767, 32767, 0, 0)),
		(ABS_RY, (-32767, 32767, 0, 0)),
		(ABS_RZ, (-32767, 32767, 0, 0)),
	]
}

key_to_abs_map = {
	KEY_A : (LEFT_STICK_X, -1),
	KEY_D : (LEFT_STICK_X, 1),
	KEY_W : (LEFT_STICK_Y, -1),
	KEY_S : (LEFT_STICK_Y, 1),
}

key_to_key_map = {
	#KEY_SPACE : BTN_A,
	#KEY_LEFTSHIFT : BTN_THUMBL,
	#KEY_LEFT : 704,
	#KEY_RIGHT : 705,
	#KEY_UP : 706,
	#KEY_DOWN : 707,
}

mouse_key_to_abs_map = {
	#BTN_MOUSE : (RIGHT_TRIGGER, 1),
	#BTN_RIGHT : (LEFT_TRIGGER, 1),
}

mouse_key_to_key_map = {
	#BTN_MIDDLE : BTN_THUMBR,
}

mouse_rel_to_abs_map = {
	REL_X : (RIGHT_STICK_X, 1),
	#REL_Y : (RIGHT_STICK_Y, 1),
}

