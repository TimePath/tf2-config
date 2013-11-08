#!/usr/bin/env python
import socket, re

s = socket.socket()
s.connect(('localhost', 12345))
f = s.makefile('r')
while 1:
	print f.readline()
	print "-----"
