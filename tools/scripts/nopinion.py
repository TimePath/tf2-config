#!/usr/bin/env python
import console, re

if __name__ == "__main__":
	c = console.Console()
	last_address = None
	while True:
		contents = c.read()
		ip = re.findall(r"(?<=Connected to )[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\:[0-9]{1,5}", contents)
		if ip:
			address = ip.pop()
			print(address)
			if not address == last_address:
				last_address = address
				c.send("connect %s matchmaking" % address)
