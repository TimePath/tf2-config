#!/usr/bin/env python2
import mumble_link as l
import time
import math

METERS_PER_INCH=float(0.0254)

def unpack_m(p):
	return (p[0], p[2], p[1])

def unpack(p):
	return (p[0] * (1/METERS_PER_INCH), p[2] * (1/METERS_PER_INCH), p[1] * (1/METERS_PER_INCH))

def length(p):
	return math.sqrt((p[0] ** 2) + (p[1] ** 2) + (p[2] ** 2))
	
def sub(p1, p2):
	return (p2[0] - p1[0], p2[1] - p1[1], p2[2] - p1[2])

sample = .5

if l.open():
	lastpos = (0,0,0)
	init = False
	while True:	
		unpacked = unpack(l.get_avatar_position())
		nowpos = unpacked
		if init:
			nowvel = sub(lastpos, nowpos)
			print(length((nowvel[0], nowvel[1], 0)) * (1/sample))
		init = True
		lastpos = unpacked
		time.sleep(sample)
