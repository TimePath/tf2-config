#!/usr/bin/env python

from console.console import Console
from mumble.point import Vector3D
from overlay.overlay import OSD

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtOpenGL import *

import re

import pprint

debug = False

class GrowingList(list):
	def __setitem__(self, index, value):
		if index >= len(self):
			self.extend([None]*(index + 1 - len(self)))
		list.__setitem__(self, index, value)

def unpack(type, val):
	if type == "bool":
		if val == "true": return True
		else: return False
	elif type == "short" or type == "integer":
		return int(val)
	elif type == "float":
		return float(val)
	elif type == "vector":
		return Vector3D(*tuple([float(x) for x in val.split(" ")]))
	else:
		return str(val)

def parse(line):
	obj = re.search(r"(.*) (bool|short|integer|float|vector|string) \((.*)\)", line)
	if obj:
		var = obj.group(1)
		val = unpack(obj.group(2), obj.group(3))
		# More pythonic, but m_iPing and m_iHealth are both variables and arrays. Should I parse individual scopes?
		#index = var.find("[")
		#if index >= 0:
		#	name = var[:index]
		#	print(name)
		#	if not name in vars:
		#		vars[name] = GrowingList([])
		#	index = var[index+1:var.find("]")]
		#	vars[name][int(index)] = val
		#else:
		vars[var] = val
	else: pass
		#print("Ignored %s" % line)

class LCD(OSD):
	def logic(self):
		c.send("g15_dumpplayer")
		lines = c.read(1/self.rate_update)
		for line in lines:
			parse(line)
		self.repaint()
			
	def render(self, qp):
		if debug:
			qp.setPen(QColor.fromRgbF(1, 1, 1, 0.5))
			qp.setFont(QFont("monospaced", 8))
			initial = [50, 100]
			current = [50, 100]
			try:
				for line in pprint.pformat(vars).split("\n"):
					qp.drawText(current[0], current[1], line)
					current[1] += 15
					if current[1] >= 1000:
						current[1] = initial[1]
						if current[0] == initial[0]: current[0] += 200
						current[0] += 200
						
			except AttributeError: pass
		xs = {1:100, 3:400, 2:960}
		ys = {1:200, 3:200, 2:200}
		for i in range(33):
			i = str(i)
			try:
				connected	= vars["m_bConnected["+i+"]"]
				if not connected: continue
				alive		= vars["m_bAlive["+i+"]"]
				deaths		= vars["m_iDeaths["+i+"]"]
				if alive:
					health	= vars["m_iHealth["+i+"]"]
				else:
					health = 0
				ping		= vars["m_iPing["+i+"]"]
				score		= vars["m_iScore["+i+"]"]
				team		= vars["m_iTeam["+i+"]"]	# 0 = no, 1 = spec, 2/3 = red/blu
				name		= vars["m_szName["+i+"]"]	# Names. '' = none, 'unconnected' = empty slot
				string = "%s (%s) %.2f" % (name, health, score / max(deaths, 1))
				font = QFont("monospaced", 11)
				fm = QFontMetrics(font)
				qp.setFont(font)
				height = fm.height() + fm.descent()
				qp.fillRect(xs[team], ys[team] - fm.height(), fm.width(string), height, QColor.fromRgbF(0,0,0,.5))
				qp.drawText(xs[team], ys[team], string)
				
				if health == 0:
					qp.setPen(QColor.fromRgbF(1, 0, 0, .75))
				elif health <= 150:
					qp.setPen(QColor.fromRgbF(1, .5, 0, .75))
				else:
					qp.setPen(QColor.fromRgbF(1, 1, 1, .75))
				qp.drawText(xs[team], ys[team], string)
				ys[team] += height
			except KeyError: pass

"""
m_Activity					Overall activity - idling?
m_Local.m_bDrawViewmodel
m_Local.m_bDucked
m_Local.m_bDucking
m_Local.m_bInDuckJump
m_Local.flDuckJumpTime
m_Local.m_flDucktime
m_Local.m_flFallVelocity
m_Local.m_flJumpTime
m_Shared.m_bFeignDeathReady
m_Shared.m_bJumping
m_Shared.m_bLastDisguisedAsOwnTeam
m_Shared.m_bRageDraining
m_Shared.m_flChargeMeter
m_Shared.m_flCloakMeter
m_Shared.m_flDisguiseCompleteTime
m_Shared.m_flDuckTimer
m_Shared.m_flEnergyDrinkMeter
m_Shared.m_flHypeMeter
m_Shared.m_flInvisChangeCompleteTime
m_Shared.m_flNextRageEarnTime
m_Shared.m_flRageMeter
m_Shared.m_iAirDash
m_Shared.m_nAirDucked
m_Shared.m_nDesiredDisguiseClass
m_Shared.m_nDesiredDisguiseTeam
m_Shared.m_nDisguiseClass
m_Shared.m_nDisguiseTeam
m_bAltFiresUnderwater
m_bBeingRepurposedForTaunt
m_bCritFire
m_bCurrentAttackIsCrit
m_bDisguiseWeapon
m_bFiresUnderwater
m_bFiringWholeClip
m_bInReload
m_bReadyToBackstab
m_bReloadsSingly
m_fFireDuration
m_fOnTarget
m_flChargeBeginTime
m_flChargedDamage
m_flDetonateTime
m_flEffectBarRegenTime
m_iAmmo[0-31]				your reserve ammo, 1 2 3
m_iClip1	Current clip
m_iClip2	Current clip (for single clip weapons)
m_iComboCount
m_iDeaths
m_iFOVStart		current FOV
m_iHealth	my health

m_iPing	my ping

m_iPrimaryAmmoCount
m_iPrimaryAmmoType
m_iReloadMode
m_iRoundsWon
m_iScore		my score?


m_iSecondaryAmmoCount
m_iSecondaryAmmoType
m_iState
m_iTeamNum


m_iViewModelIndex	Current weapon
m_iWorldModelIndex	Current weapon
m_nViewModelIndex	Old? Current weapon?

pl.deadflag		Me dead
"""

if __name__ == "__main__":
	c = Console()
	vars = {}
	g15 = LCD()
	g15.rate_update = 1
	g15.start()
