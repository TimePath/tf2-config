#!/usr/bin/env python
from console.console import Console
import re

if __name__ == "__main__":
	c = Console()
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
