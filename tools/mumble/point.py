#!/usr/bin/env python
import math

class Vector3D:
	
	def __init__(self, x = 0, y = 0, z = 0):
		self.x, self.y, self.z = float(x), float(y), float(z)
		self.c = [self.x, self.y, self.z]
	
	def __add__(self, v):
		return Vector3D(*tuple([self[i]+v[i] for i in range(len(self))]))
	
	def __sub__(self, v):
		return Vector3D(*tuple([self[i]-v[i] for i in range(len(self))]))
	
	def __mul__(self, s):
		return Vector3D(*tuple([self[i]*s for i in range(len(self))]))
	
	def __div__(self, s): # python2
		return Vector3D(*tuple([self[i]/s for i in range(len(self))]))
	
	def __truediv__(self, s): # python3
		return Vector3D(*tuple([self[i]/s for i in range(len(self))]))
	
	def __floordiv__(self, s): # python3
		return Vector3D(*tuple([self[i]//s for i in range(len(self))]))
	
	def __len__(self):
		return len(self.c)
	
	def __getitem__(self, index):
		return self.c[index]
	
	def __str__(self):
		return str(self.c)
	
	def __repr__(self):
		return repr(self.c)
	
	def magnitude(self):
		return math.sqrt(sum(self[i]**2 for i in range(len(self))))

	def normalize(self):
		vmag = self.magnitude()
		return Vector3D(*tuple([self[i]/vmag for i in range(len(self))]))
	
	def cross(self, v):
		cross = [0,0,0]
		cross[0] = self[1] * v[2] - self[2] * v[1]
		cross[1] = self[2] * v[0] - self[0] * v[2]
		cross[2] = self[0] * v[1] - self[1] * v[0]
		return Vector3D(*tuple(cross))
	
	def rotate(self, v2, a):
		""" Rotates this vector around 'v2' by 'a' radians """
		u, v, w = self * v2.x, self * v2.y, self * v2.z
		sa, ca = math.sin(a), math.cos(a)
		vec=[v2.x*(u[0]+v[1]+w[2])+(self.x*(v2.y**2+v2.z**2)-v2.x*(v[1]+w[2]))*ca+(-w[1]+v[2])*sa,
			v2.y*(u[0]+v[1]+w[2])+(self.y*(v2.x**2+v2.z**2)-v2.y*(u[0]+w[2]))*ca+(+w[0]-u[2])*sa,
			v2.z*(u[0]+v[1]+w[2])+(self.z*(v2.x**2+v2.y**2)-v2.z*(u[0]+v[1]))*ca+(-v[0]+u[1])*sa]
		return Vector3D(*vec)
	
	def project(self, win_width, win_height, fov, viewer_distance):
		factor = fov / (viewer_distance + self.z)
		x = self.x * factor + win_width / 2
		y = -self.y * factor + win_height / 2
		return Vector3D(x, y, 1)
	
#print(str(Vector3D(0,1,0).rotate(Vector3D(0,0,1), math.pi/2)) + ", expected [-1, 0, 0]")
