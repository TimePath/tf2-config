#!/usr/bin/env python
import socket, re

s = socket.socket()
s.connect(('localhost', 12345))
last_address=None
while 1:
    contents = s.recv(1024)
    ip = re.findall(r"(?<=Connected to )[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\:[0-9]{1,5}", contents)
    if ip:
        address = ip.pop()
        print(address)
        if not address == last_address:
            last_address = address
            cmd = 'connect %s matchmaking\n'%address
            s.send(cmd)
