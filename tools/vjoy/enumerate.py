#!/usr/bin/env python
import evdev

from evdev import *
from evdev.ecodes import *

from colorama import init, Fore, Back, Style
init(autoreset=True)
#Fore: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
#Back: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
#Style: DIM, NORMAL, BRIGHT, RESET_ALL

evdev_verbose=True

def str_event(evt):
	if type(evt) == long:
		try:
			return EV[evt]
		except KeyError:
			return str(evt)
	# If verbose listing:
	if type(evt) == tuple:
		name = evt[0]
		code = evt[1]
	if type(name) == list:
		name = str(name)
	if name == '?':
		return str(code)
	return str(name)
	
def str_key(ev, key):
	if type(key) == long:
		try:
			return str(bytype[ev][key])
		except KeyError:
			return str(key)
	# If verbose listing:
	absinfo = None
	if type(key) == tuple:
		name = key[0]
		if type(name) == tuple: # AbsInfo
			name = key[0] # tuple
			absinfo = key[1]

			name = name[0]
			key = name[1]
		else:
			key = key[1]
	if type(name) == list:
		name = str(name)
	if name == '?':
		name = key
	if absinfo == None:
		return str(name)
	else:
		return "(" + name + ", (" + ", ".join(str(value) for key, value in absinfo._asdict().iteritems()) + "))"
	
print(Style.BRIGHT + Back.RED + Fore.YELLOW + "Device listing:" + Back.RESET + "\n")
devs = [InputDevice(dev) for dev in list_devices()]
for dev in devs:
	print(Style.BRIGHT + Back.RED + Fore.YELLOW + str(dev) + "\n" + str(dev.info))
	print(Style.BRIGHT + "NAME = " + "\"" + dev.name + "\"" + "\n" + "\n".join(str(key).upper() + " = " + str(hex(value)) for key, value in dev.info._asdict().iteritems()))
	caps = dev.capabilities(verbose=evdev_verbose, absinfo=True)
	print(Style.BRIGHT + "SIG = " + str(caps.keys()))
	print(Style.BRIGHT + "CAPABILITIES = {\n" + "\n\t],\n".join(("\t" + str_event(key) + ": [\n" + (",\n".join("\t\t" + str_key(key, v) for v in value))) for key, value in caps.iteritems()) + "\n\t]\n}\n")

