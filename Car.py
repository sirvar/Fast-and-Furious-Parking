from pygame import *
from math import *

import Game

class Car():
	def __init__(self, surface, picture, x, y, angle):
		self.surface = surface
		self.carRect = Rect(0,0,0,0)
		self.speed = 1
		self.curSpeed = 0
		self.carImage = image.load(picture)
		self.carImageRotated = transform.rotozoom(self.carImage, angle, 1)
		self.boundingRect = self.carImageRotated.get_rect()
		self.x = x
		self.y = y
		self.angle = angle
		self.outline = self.getOuter()
		self.outlineRotated = self.outline[:]
		self.lastDirection = ""
		self.brakeSound = mixer.Sound("res/audio/ebrake.ogg")

	def render(self):
		if self.curSpeed < 0:
			self.curSpeed = 0
		self.carImageRotated = transform.rotozoom(self.carImage, self.angle, 1)
		self.boundingRect = self.carImageRotated.get_rect()
		self.surface.blit(self.carImageRotated, (self.x-self.boundingRect[2]/2,self.y-self.boundingRect[3]/2))
		self.carRect = Rect(self.x-self.boundingRect[2]/2,self.y-self.boundingRect[3]/2,self.boundingRect[2],self.boundingRect[3])
		# draw.circle(self.surface, (0,0,0), (int(self.x),int(self.y)),10)

	def drive(self, forward=False, backward=False, right=False, left=False):
		if forward:
			if self.lastDirection == "REVERSE" and self.curSpeed > 0:
				self.curSpeed -= self.speed*0.05
			else:
				if self.curSpeed < self.speed:
					self.curSpeed += 0.1
				if right:
					self.angle -= self.curSpeed/2
				elif left:
					self.angle += self.curSpeed/2
				self.x,self.y = self.point(self.x,self.y,self.curSpeed,self.angle+90)
				for pt in range(len(self.outline)):
					self.outline[pt] = self.point(self.outline[pt][0], self.outline[pt][1], self.curSpeed, self.angle+90)
					self.outlineRotated[pt] = self.rotatePoint(self.x, self.y, self.outline[pt][0], self.outline[pt][1], self.angle, 1)
				self.lastDirection = "FORWARD"
		elif backward:
			if self.lastDirection == "FORWARD" and self.curSpeed > 0:
				self.curSpeed -= self.speed*0.05
			else:
				if self.curSpeed < self.speed:
					self.curSpeed += 0.1
				if right:
					self.angle += self.curSpeed/2
				elif left:
					self.angle -= self.curSpeed/2
				self.x,self.y = self.point(self.x,self.y,self.curSpeed,self.angle-90)
				for pt in range(len(self.outlineRotated)):
					self.outline[pt] = self.point(self.outline[pt][0], self.outline[pt][1], self.curSpeed, self.angle-90)
					self.outlineRotated[pt] = self.rotatePoint(self.x, self.y, self.outline[pt][0], self.outline[pt][1], self.angle, 1)
				self.lastDirection = "REVERSE"
		else:
			if self.curSpeed > 0:
				self.curSpeed -= self.speed*0.01
				if self.lastDirection == "FORWARD":
					if right:
						self.angle -= self.curSpeed/2
					elif left:
						self.angle += self.curSpeed/2
					self.x,self.y = self.point(self.x,self.y,self.curSpeed,self.angle+90)
					for pt in range(len(self.outline)):
						self.outline[pt] = self.point(self.outline[pt][0], self.outline[pt][1], self.curSpeed, self.angle+90)
						self.outlineRotated[pt] = self.rotatePoint(self.x, self.y, self.outline[pt][0], self.outline[pt][1], self.angle, 1)
				elif self.lastDirection == "REVERSE":
					if right:
						self.angle += self.curSpeed/2
					elif left:
						self.angle -= self.curSpeed/2
					self.x,self.y = self.point(self.x,self.y,self.curSpeed,self.angle-90)
					for pt in range(len(self.outline)):
						self.outline[pt] = self.point(self.outline[pt][0], self.outline[pt][1], self.curSpeed, self.angle-90)
						self.outlineRotated[pt] = self.rotatePoint(self.x, self.y, self.outline[pt][0], self.outline[pt][1], self.angle, 1)
	def point(self,x,y,size,ang):
		dx = cos(radians(ang))
		dy = sin(radians(ang))
		return (x+dx*size,y-dy*size)

	def collision(self):
		Game.lostLife()

	def brake(self):
		if self.curSpeed > 0:
			self.curSpeed -= self.speed*0.05
			self.brakeSound.play()
		else:
			self.brakeSound.stop()

	def getOuter(self):
		points = []
		for x in range(1, self.carImageRotated.get_width()-1):
			for y in range(1, self.carImageRotated.get_height()-1):
				if self.carImageRotated.get_at((x,y))[3] >= 10 and 0 in [self.carImageRotated.get_at((x-1,y-1))[3],self.carImageRotated.get_at((x,y-1))[3],self.carImageRotated.get_at((x+1,y-1))[3],self.carImageRotated.get_at((x+1,y))[3],self.carImageRotated.get_at((x+1,y+1))[3],self.carImageRotated.get_at((x,y+1))[3],self.carImageRotated.get_at((x-1,y+1))[3],self.carImageRotated.get_at((x-1,y))[3]] or ((y == 1 or y == self.carImageRotated.get_height()-2) and self.carImageRotated.get_at((x,y))[3] >= 10) or ((x == 1 or x == self.carImageRotated.get_width()-2) and self.carImageRotated.get_at((x,y))[3] >= 10):
					points.append((x+int(self.x-self.boundingRect[2]/2),y+int(self.y-self.boundingRect[3]/2)))
		return (points)

	def getPt(self):
		return self.outline

	def getBoundRect(self):
		return Rect(self.x-(self.carImageRotated.get_width()//2), self.y-(self.carImageRotated.get_height()//2), self.carImageRotated.get_width(), self.carImageRotated.get_height())

	def xy2vect(self,x,y):
		mag = hypot(x,y)
		ang = degrees(atan2(y,x))
		return mag, ang

	def vect2xy(self, ang, mag):
		return cos(radians(ang))*mag, sin(radians(ang))*mag

	def rotatePoint(self, x, y, px, py, ang, size):
		dx, dy = px-x, py-y
		mag, curAng = self.xy2vect(dx,dy)
		curAng -= ang
		dx, dy = self.vect2xy(curAng, mag)
		return (x+dx)*size, (y+dy)*size