#!/usr/bin/env python
import socket

class Console:
	def __init__(self, host="localhost", port=12345):
		self.lastcmd = None
		self.s = socket.socket()
		self.s.connect((host, port))
		self.f = self.s.makefile("rw")
	
	def read(self):
		line = self.f.readline()[:-1]
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