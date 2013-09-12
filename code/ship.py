import pygame
import physicalObject
import profiles
import colors
import objInstances
from geometry import distance, lineIntersectsCircle, angleToSlope, inSights
import globalvars

class Ship(physicalObject.PhysicalObject):
	def __init__(self, centerx=0, centery=0, image_name='default'):

		physicalObject.PhysicalObject.__init__(self, centerx=centerx,\
			centery=centery, image_name=image_name)

		self.weapons=[]
		self.engine=None

		self.health=50
		self.maxhealth=50

		profiles.shipProfile(self, profile='mk1')
		self.setProfile()

		self.myHealthBar = None
		self.setHealthBar()

		self.is_a = globalvars.SHIP


	def setHealthBar(self):
		self.myHealthBar = objInstances.HealthBar(width=20, height=10, ship=self, vertical=False, 
			current=self.health, total=self.maxhealth)
		globalvars.intangibles.append(self.myHealthBar)


	def setProfile(self):
		#TODO shouldn't there be a better way to do this?
		self.maxSpeed = self.engine.maxSpeed
		self.dv = self.engine.dv
		self.dthea = self.engine.dtheta
		self.speedIncrements = self.engine.speedIncrements
		#Fraction of maxSpeed at which turn rate is maximal
		self.maxTurnSpeed = self.engine.maxTurnSpeed
		#Rate at which turn rate decays as speed moves away from maxTurnSpeed
		self.turnRateDecay = self.engine.turnRateDecay


	def takeDamage(self):
		self.health -= 10

	def gainHealth(self, amount):
		self.health = min(self.maxhealth, self.health+amount)

	def isDead(self):
		return self.health <= 0


	def shoot(self, force_shot=False):
		#Force shot tells this to shoot even if a target 
		#is not obviously in view. NPC's will not take such wild shots.
		for w in self.weapons:
			if w.cooldown == 0:
				#The player can shoot whenever he wants
				if force_shot:
					w.shoot()
				#NPCs need some intelligence when shooting
				else:
					angle = self.getAngleToTarget()
					#Decide whether or not we can shoot
					if inSights(self, self.destination,\
					w.weapon_range, w.attack_angle) and\
					self.clearLineOfSight():
						w.shoot()


	def cooldown(self):
		'''Cool all our weapons'''
		for w in self.weapons:
			w.cool()


	def clearLineOfSight(self):
		'''Pre: Sight_range is an int or float.
		Post: Returns true if there are no whiskerables in the line of sight of this ship.
		Useful for avoiding friendly fire.'''
		#Get distance to target
		dtt = distance(self.rect.center, self.destination)
		#For each potential obstacle...
		for w in globalvars.whiskerables:
			#Get distance to the obstacle
			dist = distance(self.rect.center, w.rect.center)
			#   If the distance to the obstacle is less than the distance 
			#to the target then the obstacle might be obstructing our 
			#sight of the target.
			#   If the obstacle's distance is greater than zero then the 
			#obstacle is not ourself.
			#   If the angle to the obstacle is less than 80 degrees, then 
			#the obstacle is in front of this ship.
			if dist < dtt and dist > 0 and\
			abs(self.getAngleToTarget(target=w.rect.center)) < 90:
				#   If a line extending straight out from this ship
				#intersects a circle around the obstacle, then our 
				#sight is blocked.
				m,b = self.getStraightAhead()
				x,y = w.rect.center
				r = w.radius
				#I boost the radius by a 1.5 fudge factor to 
				#help the NPCs avoid friendly fire.
				if lineIntersectsCircle(m, b, x, y, r*1.5):
					return False
		return True


	def getStraightAhead(self):
		'''Pre: 
		Post: returns slope and intercept of line extending straight 
		ahead from this ship'''
		slope = angleToSlope(self.theta)
		x,y = self.rect.center
		intercept = y - slope * x
		return slope, intercept


	def update(self, offset):
		#for now we assume that every ship is hostile to the player
		self.setDestination(globalvars.player.rect.center)

		#Turn towards target
		self.turnTowards()

		d = distance(self.rect.center, self.destination)
		#If target is far, increase goal speed.
		if d > 200:
			self.targetSpeed = self.maxSpeed
		#If target is near, decrease goal speed.
		elif d < 120:
			self.targetSpeed = 0
		else:
			self.targetSpeed = self.maxSpeed/2

		#cooldown all the weapons
		self.cooldown()
		#Check for firing solutions
		self.shoot()

		#modify speed
		self.approachSpeed()

		#move
		self.move()

		#draw
		x,y = self.rect.center
		pos = x - offset[0], y - offset[1]
		self.drawAt(pos)


	def handleCollisionWith(self, other_sprite):
		'''For now ships take damage regardless of what they hit.'''
		died = False
		#Check for collisions with one's own bullets.
		#Don't respond to such collisions.
		if other_sprite.is_a == globalvars.BULLET:
			if other_sprite.dontClipMe == self:
				return died
			else:
				self.takeDamage()
		elif other_sprite.is_a == globalvars.SHIP:
			#Check for bounce off
			#For now, area stands in for mass and only the
			#less massive object bounces off
			if other_sprite.getArea() >= self.getArea():
				self.bounceOff(other_sprite)
				self.takeDamage()
		elif other_sprite.is_a == globalvars.FIXEDBODY:
			self.bounceOff(other_sprite)
			return died
		elif other_sprite.is_a == globalvars.ASTEROID:
			self.bounceOff(other_sprite)
			self.takeDamage()
		#This if is not necessary since falling through has the same effect.
		#elif other_sprite.is_a == globalvars.HEALTH:
			#The health kit gives the player health. This is better because otherwise
			#we have to deal with multiple collisions between player and health
			#or a race condition over who gets updated first, the player sprite 
			#or the health sprite.
		#	return died
		if self.isDead():
			globalvars.intangibles.append(objInstances.Explosion(\
				x=self.rect.centerx,y=self.rect.centery))
			#kill removes the calling sprite from all sprite groups
			self.kill()
			globalvars.intangibles.remove(self.myHealthBar)
			self.myHealthBar.kill()
			died = True
		return died

