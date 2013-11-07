import mmap
import math
import json
import ctypes
import os
import time
import select

class Link(ctypes.Structure):

	_fields_ = [
		("uiVersion",	   ctypes.c_uint32),
		("uiTick",		  ctypes.c_uint32),
		("fAvatarPosition", ctypes.c_float * 3),
		("fAvatarFront",	ctypes.c_float * 3),
		("fAvatarTop",	  ctypes.c_float * 3),
		("name",			ctypes.c_wchar * 256),
		("fCameraPosition", ctypes.c_float * 3),
		("fCameraFront",	ctypes.c_float * 3),
		("fCameraTop",	  ctypes.c_float * 3),
		("identity",		ctypes.c_wchar * 256),
		("context_len",	 ctypes.c_uint32),
		("context",		 ctypes.c_uint32 * 64), # is actually 256 bytes of whatever
		("description",	 ctypes.c_wchar * 2048)
	]
	
	def json(self):
		return json.dumps([x[0] for x in self._fields_])
 
def unpack(ctype, buf):
	cstring = ctypes.create_string_buffer(buf)
	ctype_instance = ctypes.cast(ctypes.pointer(cstring), ctypes.POINTER(ctype)).contents
	return ctype_instance
	
period = 1
			 
if __name__ == "__main__":
	fd = os.open('/dev/shm/MumbleLink.1000', os.O_RDONLY)
	previous_tick = -1
	memfile = mmap.mmap(fd, mmap.PAGESIZE, mmap.MAP_SHARED, mmap.PROT_READ) # ctypes.sizeof(Link), "MumbleLink")
	while True:
		memfile.seek(0)
		#select.select([fd], [], [])
		time.sleep(.1 * period)
		data = memfile.read(ctypes.sizeof(Link))
		result = unpack(Link, data)
		if result.uiTick == previous_tick:
			continue
		if previous_tick > 0 and previous_tick + 1 < result.uiTick:
			print("Dropped")
		print(result.json())
		previous_tick = result.uiTick
