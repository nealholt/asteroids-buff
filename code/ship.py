import pygame
import physicalObject
import profiles
import colors
import objInstances
from geometry import distance, lineIntersectsCircle, angleToSlope, inSights
import globalvars
import weapon

healthBarDefaultWidth = 20

class Ship(physicalObject.PhysicalObject):
	def __init__(self, centerx=0, centery=0, image_name='default'):

		physicalObject.PhysicalObject.__init__(self, centerx=centerx,\
			centery=centery, image_name=image_name)

		self.engine=None

		self.health=50
		self.maxhealth=50
		#number of gun addon hardpoints
		self.gunHardpoints = 1
		#number of missile addon hardpoints
		self.missileHardpoints = 1
		#number of mine addon hardpoints
		self.mineHardpoints = 1
		#number of mine addon hardpoints
		self.weapons=[]
		#number of misc addon hardpoints
		self.miscHardpoints = 1
		#int fuel (just make it a big number and divide it by 100 or 1000 and then display that number without the decimal.)
		self.fuel = 18000 #5*60*60 = 5 minutes of fuel assuming 60 frames per second.
		#Money. This is updated when the ship runs into a gem.
		self.money = 0
		#cargo space
		self.cargoSpace = 30
		#cargo array
		self.cargo = []

		profiles.shipProfile(self, profile='mk1')
		self.setProfile()

		self.myHealthBar = None
		self.healthBarOffset = self.rect.height
		self.setHealthBar()

		self.is_a = globalvars.SHIP
		self.isPlayer = False


	def setWeapon(self, weaponId):
		'''Pre: weaponId is a string such as 'spread_mk3'.
		Assumes the ship only has one weapon equipped.
		Post: Changes the player's weapon.
		This is called by the weapons panel in menus.py.'''
		self.weapons = [weapon.getWeapon(weaponId, self)]


	def unequipWeapon(self):
		self.cargo.append(self.weapons.pop(0))
		

	def equipWeaponFromCargo(self, cargo_index):
		#Error checking
		if cargo_index >= len(self.cargo):
			print 'ERROR: cargo_index '+str(cargo_index)+' is outside the cargo array.'
			exit()
		#This is a bad way to check if the indexed cargo is a weapon but it's what I've got for now.
		if not hasattr(self.cargo[cargo_index], 'shooter'):
			print 'ERROR: cargo indexed by '+str(cargo_index)+' is not a weapon.'
			exit()
		#If there is a current weapon, unequip it.
		while len(self.weapons) > 0:
			self.unequipWeapon()
		#Equip the weapon from cargo.
		self.weapons.append(self.cargo.pop(cargo_index))


	def setHealthBar(self):
		self.myHealthBar = objInstances.HealthBar(width=healthBarDefaultWidth, height=10)
		self.myHealthBar.new_width = (self.health/float(self.maxhealth))*healthBarDefaultWidth
		globalvars.intangibles_top.add(self.myHealthBar)


	def setProfile(self):
		self.maxSpeed = self.engine.maxSpeed
		self.dv = self.engine.dv
		self.dtheta = self.engine.dtheta
		self.speedIncrements = self.engine.speedIncrements
		#Fraction of maxSpeed at which turn rate is maximal
		self.maxTurnSpeed = self.engine.maxTurnSpeed
		#Rate at which turn rate decays as speed moves away from maxTurnSpeed
		self.turnRateDecay = self.engine.turnRateDecay


	def takeDamage(self):
		self.health -= 10
		self.myHealthBar.new_width = (self.health/float(self.maxhealth))*healthBarDefaultWidth


	def gainHealth(self, amount):
		self.health = min(self.maxhealth, self.health+amount)
		self.myHealthBar.new_width = (self.health/float(self.maxhealth))*healthBarDefaultWidth

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
				r = w.collisionradius
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


	def update(self):
		'''The following code is mostly duplicated in the missile's update function. Eventually I'd like to break this out as a more general seeking behavior.'''
		#for now we assume that every ship is hostile to the player
		self.setDestination(globalvars.player_target_lead)

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

		#Update my health bar
		self.updateHealthBar()


	def updateHealthBar(self):
		self.myHealthBar.rect.center = self.rect.center
		self.myHealthBar.rect.top -= self.healthBarOffset


	def draw(self, offset):
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
			globalvars.intangibles_top.add(objInstances.Explosion(\
				x=self.rect.centerx,y=self.rect.centery))
			#kill removes the calling sprite from all sprite groups
			self.kill()
			self.myHealthBar.kill()
			died = True
		return died

