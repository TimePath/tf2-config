#!/usr/bin/env python2

##python2
#import pygtk
#pygtk.require('2.0')
import gtk, gobject

##python3
#from gi.repository import Gtk as gtk
#from gi import pygtkcompat
#pygtkcompat.enable()
#pygtkcompat.enable_gtk(version='3.0')

import time
import cairo
from math import pi
import mumble_link as l
import math

from collections import deque

class CircularBuffer(deque):
	
	def __init__(self, size=0):
		super(CircularBuffer, self).__init__(maxlen=size)
		self.top = 0
	
	def append(self, what):
		super(CircularBuffer, self).append(what)
		self.top = max(list(self))
	
	def average(self):
		if len(self) == 0: return 0
		return sum(self) / len(self)

METERS_PER_INCH=float(0.0254)

cb = CircularBuffer(size=5)

def unpack(p):
	return (p[0], p[2], p[1])

def length(p):
	return math.sqrt((p[0] ** 2) + (p[1] ** 2) + (p[2] ** 2)) * (1 / METERS_PER_INCH)
	
def sub(p1, p2):
	return (p2[0] - p1[0], p2[1] - p1[1], p2[2] - p1[2])

rate_render = 25
rate_update = 10

def rad(angle):
	return pi/180*angle

locations = [(-6017.606445, 4338.713867, 120.432190), (-6023.517578,1358.113770,-48.077370)] # cp_gorge points A and B

def arc(cr, xy, radius, radred, start, length):
	cr.arc(xy[0]/2, xy[1]/2, radius-radred, start, start+length)
	
def point(cr, xy, radius, radred, start, length):
	arc(cr, xy, radius, radred, start - length/2, length)
	
def magnitude(v):
	return math.sqrt(sum(v[i]*v[i] for i in range(len(v))))

def add(u, v):
	return tuple([ u[i]+v[i] for i in range(len(u)) ])

def sub(u, v):
	return tuple([ u[i]-v[i] for i in range(len(u)) ])

def dot(u, v):
	return sum(u[i]*v[i] for i in range(len(u)))

def normalize(v):
	vmag = magnitude(v)
	return tuple([ v[i]/vmag  for i in range(len(v)) ])

class MainWindow(gtk.Window):
	
	def __init__(self):
		super(MainWindow, self).__init__()
		
		self.set_title("Python overlay")
		
		self.connect("destroy", gtk.main_quit)
		
		self.set_decorated(False)
		self.set_has_frame(False)
		self.set_keep_above(True)
		self.set_resizable(False)
		self.set_skip_taskbar_hint(True)
		self.set_skip_pager_hint(True)
		self.set_accept_focus(False)
		self.set_app_paintable(True)
		self.set_size_request(160, 160)
		
		size = self.get_size()
		bitmap = gtk.gdk.Pixmap(self.window, size[0], size[1], 1)
		self.input_shape_combine_mask(bitmap, 0, 0) # somewhat buggy, but generally works
		
		# Transparency
		screen = self.get_screen()
		rgba = screen.get_rgba_colormap()
		self.set_colormap(rgba)
		
		self.connect("expose-event", self.expose)
		self.start = time.time()
		
		self.label = gtk.Label()
		self.add(self.label)
		
	def render(self):
		self.queue_draw()
		#size = self.get_size()
		#width = gtk.gdk.screen_width() - size[0]
		#height = gtk.gdk.screen_height() - size[1]
		##self.move(10, 10)
		return True
	
	def update(self):
		nowpos = unpack(l.get_avatar_position())
		thistick = l.get_tick()
		now = time.time()
		try:
			self.init
		except AttributeError:
			self.init = True
			self.then = now
			self.lastpos = nowpos
			self.lasttick = thistick
			return True
		if self.lasttick != thistick:
			tickdiff = (thistick - self.lasttick) # frames
			timediff = (now - self.then) # seconds
			
			fps = tickdiff / timediff / 2 # positional audio is updated twice a frame, apparently
			
			vel = sub(self.lastpos, nowpos)
			speed = length((vel[0], vel[1], 0)) * (fps / tickdiff * 2)
			cb.append(speed)
			
			self.lasttick = thistick
			self.then = now
			self.lastpos = nowpos
			
			self.label.set_text("\n" * 8 + "%.2f\n%.2f\n%s" % (cb.average(), fps, time.strftime('%H:%M:%S')))
		return True
	
	def expose(self, widget, event):
		cr = widget.window.cairo_create()
		
		cr.set_operator(cairo.OPERATOR_CLEAR)
		cr.rectangle(0.0, 0.0, *widget.get_size())
		cr.fill()
		
		cr.set_operator(cairo.OPERATOR_OVER)
		
		try:
			self.lastpos
			"""
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
			front = l.get_camera_front()
			top = l.get_camera_top()
			
			pitch = -math.atan2(front[1], magnitude([front[0], front[2]])) / pi * 180
			
			yaw = -math.atan2(front[0], front[2]) / pi * 180 + 90
			#print("%.2f %.2f" % (pitch, yaw))
			invm = (1 / METERS_PER_INCH)
			pp = (self.lastpos[0] * invm, self.lastpos[1] * invm, self.lastpos[2] * invm)
			cr.set_source_rgba(0.4, 0.9, 0.4, 0.75)
			cr.set_source_rgba(0.4, 0.4, 0.9, 1)
			cr.set_line_width(10)
			for mark in locations:
				d = (mark[0] - pp[0], mark[1] - pp[1], mark[2] - pp[2])
				len = length(d)
				if len == 0:
					continue
				s = (100000/len) * 20 # 1000 appears full size
				s = min(max(s, 20), 90) # minimum 20, maximum 90
				point(cr, widget.get_size(), 30, 1, math.atan2(-d[1], d[0]) - pi/2 + rad(yaw), rad(s)); cr.stroke()
		except AttributeError: pass
		
		cr.set_source_rgba(0.9, 0.9, 0.9, 0.75)
		cr.set_line_width(3)
		t = (time.time() - self.start) % (10*2*pi)
		m = 3
		for i in range(m):
			arc(cr, widget.get_size(), 40, 1, -1.5*t+((2*pi)/m)*i, ((2*pi) / (m+1))); cr.stroke()
			
			arc(cr, widget.get_size(), 40, 5, t+((2*pi)/m)*i, .25*((2*pi) / (m+1))); cr.stroke()
			arc(cr, widget.get_size(), 40, 5, pi+t+((2*pi)/m)*i, .25*((2*pi) / (m+1))); cr.stroke()
		
		cr.set_source_rgba(0.8, 0.8, 0.8, 0.5)
		arc(cr, widget.get_size(), 16, 0, 0, pi*2); cr.fill()
		
		cr.set_source_rgba(1, 1, 1, 1)
		for i in range(2):
			arc(cr, widget.get_size(), 2, 0, 0, pi*2); cr.fill()

if __name__ == "__main__":
	main = MainWindow()
	main.show_all()
	gobject.timeout_add(1000/rate_render, main.render)
	if l.open():
		gobject.timeout_add(1000/rate_update, main.update)
	gtk.main()