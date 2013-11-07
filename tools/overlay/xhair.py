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

METERS_PER_INCH=float(0.0254)

def unpack(p):
	return (p[0], p[2], p[1])

def length(p):
	return math.sqrt((p[0] ** 2) + (p[1] ** 2) + (p[2] ** 2)) * (1 / METERS_PER_INCH)
	
def sub(p1, p2):
	return (p2[0] - p1[0], p2[1] - p1[1], p2[2] - p1[2])

def arc(cr, xy, radius, radred, start, length):
	cr.arc(xy[0]/2, xy[1]/2, radius-radred, start, start+length)

rate_render = 25
rate_update = 1

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
			tickdiff = (thistick - self.lasttick)
			timediff = (now - self.then)
			
			fps = tickdiff / timediff
			
			vel = sub(self.lastpos, nowpos)
			
			speed = length((vel[0], vel[1], 0)) / timediff
			
			self.lasttick = thistick
			self.then = now
			self.lastpos = nowpos
			
			self.label.set_text("\n" * 7 + "%.2f\n%s" % (speed, time.strftime('%H:%M:%S')))
		return True
	
	def expose(self, widget, event):
		cr = widget.window.cairo_create()

		cr.set_operator(cairo.OPERATOR_CLEAR)
		cr.rectangle(0.0, 0.0, *widget.get_size())
		cr.fill()
		
		cr.set_operator(cairo.OPERATOR_OVER)
		cr.set_source_rgba(0.9, 0.9, 0.9, 0.75)
		
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