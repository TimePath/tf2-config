#!/usr/bin/env python2
#-*- coding:utf-8 -*-

"""
Python 2 or 3

Deps:
	python-pyqt4

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

import sys
import signal
import time
import math
from math import pi
from collections import deque
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtOpenGL import *

try: import mumble_link as l # python2 only
except ImportError: pass

import PyQt4.pyqtconfig
print("Running on PyQt version " + PyQt4.pyqtconfig.Configuration().pyqt_version_str)

# QWidget or QGLWidget
backend = QGLWidget
#renderhints = QPainter.Antialiasing | QPainter.SmoothPixmapTransform | QPainter.HighQualityAntialiasing
geometry = (0, 43, 1920, 1037) # comment for fullscreen
rate_render = 30
rate_update = 100
velocity_samples = 5

locations = [(-6017.606445, 4338.713867, 120.432190), (-6023.517578, 1358.113770, -48.077370)] # cp_gorge points A and B

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
	return (p[0], p[2], p[1])

def arc(qp, xy, radius, radred, start, length, method=None):
	if method == None:
		method = qp.drawArc
	r = radius-radred
	method(xy.width()/2 - r, xy.height()/2 - r, r * 2, r * 2, start * -16, length * -16)

def point(qp, xy, radius, radred, start, length):
	arc(qp, xy, radius, radred, start - length/2, length)


def add(u, v):
	return tuple([u[i]+v[i] for i in range(len(u))])

def sub(u, v):
	return tuple([u[i]-v[i] for i in range(len(u))])

def magnitude(v):
	return math.sqrt(sum(v[i]*v[i] for i in range(len(v))))

def normalize(v):
	vmag = magnitude(v)
	return tuple([v[i]/vmag for i in range(len(v))])

def length(p):
	return magnitude(p) * (1 / METERS_PER_INCH)

class OSD(backend):
	def __init__(self, parent=None):
		backend.__init__(self, parent)
		self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
		self.setAttribute(Qt.WA_TranslucentBackground, True)
		self.setWindowTitle("OSD")
		self.start = time.time()
		hwnd = self.winId()
		if sys.platform.startswith("win"): # http://wxwidgets.10942.n7.nabble.com/wxPython-and-pywin32-Implementing-on-top-transparency-and-click-through-on-Windows-td30543.html
			import win32con, win32gui
			extendedStyleSettings = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
			win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, extendedStyleSettings | win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT)
		elif sys.platform.startswith("linux"): # http://pastebin.com/nCs93R1L
			from ctypes import cdll
			cdll.LoadLibrary("./passthrough.so").allow_input_passthrough(hwnd)
		
	def repaint(self):
		self.update()
		
	def paintEvent(self, event):
		qp = QPainter()
		qp.begin(self)
		qp.beginNativePainting()
		qp.endNativePainting()
		try: qp.setRenderHints(renderhints)
		except NameError: pass
		self.render(qp)
		qp.end()
		
	def render(self, qp): # http://pyqt.sourceforge.net/Docs/PyQt4/qpainter.html
		qp.setFont(QFont("monospaced", 10))
		try:
			qp.drawText(100, 100, "vel: %.2f" % cb.average())
			qp.drawText(100, 200, "fps: %.2f" % self.fps)
			qp.drawText(100, 300, time.strftime("%H:%M:%S"))
		except AttributeError: pass
		except NameError: pass
	
		try:
			front = l.get_camera_front()
			top = l.get_camera_top()
			
			pitch = -math.atan2(front[1], magnitude([front[0], front[2]])) / pi * 180
			
			yaw = math.atan2(front[0], front[2]) / pi * 180 + 180
			if yaw < 90: yaw = -90 - yaw
			else: yaw = 270 - yaw
			#print('%.2f %.2f' % (pitch, yaw))
			invm = (1 / METERS_PER_INCH)
			pp = (self.lastpos[0] * invm, self.lastpos[1] * invm, self.lastpos[2] * invm)
			
			qp.setPen(QPen(QColor.fromRgbF(0.4, 0.4, 0.9, 1), 10))
			
			for mark in locations:
				d = (mark[0] - pp[0], mark[1] - pp[1], mark[2] - pp[2])
				len = length(d)
				if len == 0:
					continue
				s = (100000/len) * 20 # 1000 appears full size
				s = min(max(s, 20), 90) # minimum 20, maximum 90
				point(qp, self.size(), 30, 1, math.atan2(-d[1], d[0])/pi*180 + yaw - 90, s);
		except AttributeError: pass
		
		qp.setPen(QPen(QColor.fromRgbF(.9, .9, .9, .75), 3))

		t = (time.time() - self.start) % (10 * 360)
		speed = 58
		m = 3
		for i in range(m):
			arc(qp, self.size(), 40, 1, -1.5*t*speed+(360/m)*i, (360 / (m+1)));
			
			arc(qp, self.size(), 40, 5, t*speed+(360/m)*i, .25*(360 / (m+1)));
			arc(qp, self.size(), 40, 5, 180+t*speed+(360/m)*i, .25*(360 / (m+1)));
		
		qp.setPen(Qt.transparent)
		qp.setBrush(QColor.fromRgbF(0.8, 0.8, 0.8, 0.5))
		arc(qp, self.size(), 16, 0, 0, 360, qp.drawPie);
		
		qp.setPen(Qt.transparent)
		qp.setBrush(QColor.fromRgbF(1, 1, 1, 1))
		arc(qp, self.size(), 2, 0, 0, 360, qp.drawPie);
	
	def refresh(self):
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
			
			self.fps = tickdiff / timediff / 2 # positional audio is updated twice a frame, apparently
			
			vel = sub(self.lastpos, nowpos)
			speed = length((vel[0], vel[1], 0)) * (self.fps / tickdiff * 2)
			cb.append(speed)
			
			self.lasttick = thistick
			self.then = now
			self.lastpos = nowpos

if __name__ == "__main__":
	def handleIntSignal(signum, frame):
		PyQt4.QtGui.qApp.closeAllWindows()
		sys.exit(0)
		print()
	signal.signal(signal.SIGINT, handleIntSignal)
	app = QApplication(sys.argv)
	osd = OSD()
	try: osd.setGeometry(*geometry); osd.show()
	except NameError: osd.showFullScreen()
	
	timer = QTimer()
	QObject.connect(timer, QtCore.SIGNAL("timeout()"), osd.repaint)
	timer.start(1000/rate_render)
	
	try:
		if l.open():
			cb = CircularBuffer()
			timer2 = QTimer()
			QObject.connect(timer2, QtCore.SIGNAL("timeout()"), osd.refresh)
			timer2.start(1000/rate_update)
	except NameError: pass
	
	sys.exit(app.exec_())