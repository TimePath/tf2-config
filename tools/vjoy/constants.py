from evdev import ecodes as ec

# Class to save the state of an axis
class Axis:
	def __init__(self, ABS, base=0, step=32767):
		self.state = base
		self.ABS = ABS
		self.step = step
	
	def move(self, direction):
		self.state += direction * self.step

# Define axes
LEFT_STICK_X = Axis(ec.ABS_X)
LEFT_STICK_Y = Axis(ec.ABS_Y)
RIGHT_STICK_X = Axis(ec.ABS_RX)
RIGHT_STICK_Y = Axis(ec.ABS_RY)
LEFT_TRIGGER = Axis(ec.ABS_Z, base=-32767, step=65534)
RIGHT_TRIGGER = Axis(ec.ABS_RZ, base=-32767, step=65534)

AXES = [LEFT_STICK_X, LEFT_STICK_Y, LEFT_TRIGGER, RIGHT_STICK_X, RIGHT_STICK_Y, RIGHT_TRIGGER]
