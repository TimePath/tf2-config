#!/usr/bin/env python

"""
Python 2 or 3

Deps:
	python-pyqt4
"""

import sys
import signal
import time
import math
from math import pi
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtOpenGL import *

import PyQt4.pyqtconfig
print("Running on PyQt version " + PyQt4.pyqtconfig.Configuration().pyqt_version_str)

# QWidget or QGLWidget
backend = QGLWidget
#renderhints = QPainter.Antialiasing | QPainter.SmoothPixmapTransform | QPainter.HighQualityAntialiasing
geometry = (0, 44, 1920, 1037) # comment for fullscreen
rate_render = 30
rate_update = 10

class OSD(backend):
	def __init__(self, parent=None):
		self.parent = parent
		self.rate_update = rate_update
		
	def start(self):
		def handleIntSignal(signum, frame):
			PyQt4.QtGui.qApp.closeAllWindows()
			sys.exit(0)
			print()
		signal.signal(signal.SIGINT, handleIntSignal)
		
		app = QApplication(sys.argv)
		
		backend.__init__(self, self.parent)
		self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
		self.setAttribute(Qt.WA_TranslucentBackground, True)
		self.start = time.time()
		hwnd = self.winId()
		if sys.platform.startswith("win"): # http://wxwidgets.10942.n7.nabble.com/wxPython-and-pywin32-Implementing-on-top-transparency-and-click-through-on-Windows-td30543.html
			import win32con, win32gui
			extendedStyleSettings = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
			win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, extendedStyleSettings | win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT)
		elif sys.platform.startswith("linux"): # http://pastebin.com/nCs93R1L
			import os
			from ctypes import cdll
			cdll.LoadLibrary(os.path.join(os.path.dirname(__file__), "passthrough.so")).allow_input_passthrough(hwnd)
		
		try: self.setGeometry(*geometry); self.show()
		except NameError: self.showFullScreen()
		
		timer = QTimer()
		QObject.connect(timer, QtCore.SIGNAL("timeout()"), self.repaint)
		timer.start(1000/rate_render)
		
		timer2 = QTimer()
		QObject.connect(timer2, QtCore.SIGNAL("timeout()"), self.logic)
		timer2.start(1000/self.rate_update)
		
		sys.exit(app.exec_())
		
	def arc(self, qp, xy, radius, radred, start, length, method=None):
		if method == None:
			method = qp.drawArc
		r = radius-radred
		method(xy.width()/2 - r, xy.height()/2 - r, r * 2, r * 2, start * -16, length * -16)

	def point(self, qp, xy, radius, radred, start, length):
		self.arc(qp, xy, radius, radred, start - length/2, length)
		
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
	
	def logic(self): pass
	
	def render(self, qp): pass # http://pyqt.sourceforge.net/Docs/PyQt4/qpainter.html
