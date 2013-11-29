#!/usr/bin/env python

from mumble.point import Vector3D as V
from overlay.overlay import OSD

from PyQt4.QtGui import *

from collections import deque
import time
import math
from math import pi

"""
Notes:

	Coordinate system:
	angle(0,0,0) = vec(1,0,0)
	positive yaw is anticlockwise
	positive pitch is down (negative)
	
	0 yaw: +x
	+ yaw = counter clockwise
	0 pitch = level
	+ pitch = down
	
	 +y
	  |_+x
	 /
	+z (up in the air)

"""

velocity_samples = 5

currentmap = "cp_gorge"

# color, min length (arc), max length (arc), distance
style_objective = ((0.4, 0.4, 0.9, 1), 10, 90, 2000)
style_health = ((0.4, 0.9, 0.9, 1), .1, 60, 750)

locations = {
	"cp_gorge":	{
		style_objective: [
			((-6017.606445, 4338.713867, 120.432190), "A"),
			((-6023.517578, 1358.113770, -48.077370), "B"),
			],
		style_health: [
			((-6001.607910, 4442.310547, -87.896652), "H"),
			((-5985.979492, 5071.383301, -30.968689), "H"),
			((-4599.325684, 3295.571777, 102.758224), "H"),
			((-6047.500000, 3562.177246, 97.031311), "H"),
			],
		}
}

METERS_PER_INCH=float(0.0254)

class CircularBuffer(deque):
	def __init__(self, size=0):
		super(CircularBuffer, self).__init__(maxlen=velocity_samples)
		self.top = 0
	
	def append(self, what):
		super(CircularBuffer, self).append(what)
		self.top = max(list(self))
	
	def average(self):
		if len(self) == 0: return 0
		return sum(self) / len(self)

def unpack(p):
	return V(p[0], p[2], p[1])

class AR(OSD):
	def logic(self):
		try: ln
		except NameError: return # no link
		
		nowpos = unpack(ln.get_avatar_position())
		thistick = ln.get_tick()
		now = time.time()
		
		try: self.init
		except AttributeError: # init if required
			self.init = True
			self.then = now
			self.lastpos = nowpos
			self.lasttick = thistick
			return
		
		if self.lasttick != thistick:
			tickdiff = (thistick - self.lasttick) # frames
			timediff = (now - self.then) # seconds
			
			self.fps = tickdiff / timediff / 2 # positional audio is updated twice a frame, apparently
			
			vel = self.lastpos - nowpos
			speed = V(vel.x, vel.y, 0).magnitude() * (self.fps / tickdiff * 2)
			cb.append(speed)
			
			front = V(*ln.get_camera_front())
			top = V(*ln.get_camera_top())
			
			self.pitch = -math.atan2(front[1], V(front[0], front[2]).magnitude()) / pi * 180
			
			self.yaw = math.atan2(front[0], front[2]) / pi * 180 + 180
			if self.yaw < 90: self.yaw = -90 - self.yaw
			else: self.yaw = 270 - self.yaw
			
			self.roll = 0
			# setang_exact 90 -90 0 == setang_exact 90 -45 45
			#left = front.rotate(top, pi/2) * -1
			#print(str(front) + " " + str(front.magnitude()))
			#print(str(top) + " " + str(top.magnitude()))
			#print(str(left) + " " + str(left.magnitude()))
			#self.roll = math.atan2(left[1], V(left[0], left[2]).magnitude()) / pi * 180
			
			self.lasttick = thistick
			self.then = now
			self.lastpos = nowpos
	
	def render(self, qp):
		qp.setFont(QFont("monospaced", 10))
		qp.drawText(100, 300, time.strftime("%H:%M:%S"))
		
		try:
			qp.drawText(1800, 40, "%.2f %.2f %.2f" % (self.pitch, self.yaw, self.roll))
			qp.drawText(100, 200, "fps: %.2f" % self.fps)
			qp.drawText(100, 100, "vel: %.2f" % cb.average())
		except AttributeError: pass
		
		try:
			map = locations.get(currentmap)
			if map:
				for style in map:
					qp.setPen(QPen(QColor.fromRgbF(*style[0]), 10))
					for entry in locations[currentmap][style]:
						location = V(*entry[0])
						d = location - (self.lastpos / METERS_PER_INCH)
						len = d.magnitude()
						if len == 0:
							continue
						# 1 = min, 2 = max, 3 = distance
						#s = min(max((style[3]/len), 1) * style[1], style[2]) # hyperbolic
						s = max((style[3] - min(style[3], len)) / style[3] * style[2], style[1]) # linear
						self.point(qp, self.size(), 30, 1, math.atan2(-d[1], d[0])/pi*180 + self.yaw - 90, s)
		except NameError: pass		# 'currentmap' is undefined
		except AttributeError: pass	# 'lastpos' is undefined

if __name__ == "__main__":
	import sys
	sys.path.append("mumble_link")
	import mumble_link as ln
	if ln.open():
		cb = CircularBuffer()
	AR().start()
