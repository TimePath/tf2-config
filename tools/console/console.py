#!/usr/bin/env python
import socket
from select import select
import time

class Console:
	def __init__(self, host="localhost", port=12345):
		self.lastcmd = None
		self.s = socket.socket()
		self.s.connect((host, port))
		self.f = self.s.makefile("rw")
		
	def read(self, timeslice=0):
		if timeslice:
			lines = []
			end = time.time() + timeslice
			while True:
				now = time.time()
				if now >= end: break
				r, w, x = select([self.s], [], [], end - now)
				if len(r) == 0: break
				line = self.read()
				lines.append(line)
			return lines
		else:
			line = self.f.readline()[:-1] # Remove trailing \n
			if line == self.lastcmd: return self.read()
			return line
		
	def send(self, cmd):
		self.lastcmd = cmd
		msg = "%s\n" % cmd
		self.f.write(msg)
		self.f.flush()

if __name__ == "__main__":
	c = Console()
	while True:
		line = c.read()
		print("%s" % line)