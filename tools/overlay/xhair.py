#!/usr/bin/env python
import overlay
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import time

class Xhair(overlay.OSD):
	
	def render(self, qp):
		t = (time.time() - self.start) % (10 * 360)
		speed = 58
		m = 3
		qp.setPen(QPen(QColor.fromRgbF(.9, .9, .9, .75), 3))
		for i in range(m):
			self.arc(qp, self.size(), 40, 1, -1.5*t*speed+(360/m)*i, (360 / (m+1)))
			
			self.arc(qp, self.size(), 40, 5, t*speed+(360/m)*i, .25*(360 / (m+1)))
			self.arc(qp, self.size(), 40, 5, 180+t*speed+(360/m)*i, .25*(360 / (m+1)))
		
		qp.setPen(Qt.transparent)
		qp.setBrush(QColor.fromRgbF(0.8, 0.8, 0.8, 0.5))
		self.arc(qp, self.size(), 16, 0, 0, 360, qp.drawPie)
		
		qp.setPen(Qt.transparent)
		qp.setBrush(QColor.fromRgbF(1, 1, 1, 1))
		self.arc(qp, self.size(), 2, 0, 0, 360, qp.drawPie)

if __name__ == "__main__":
	Xhair().start()
