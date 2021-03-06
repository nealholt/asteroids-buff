import colors
from objInstances import Bullet, Missile, Mine
import globalvars
from testFunctions import HitBoxTestBullet
import random as rd


num_weapon_attributes = 6
#The following arrays map classes into actual values. The class is the index and the values are, well, the array values:

#Number of bullets per shot
spread_classes = [1,2,3,4,5]
#This is one over the number of shots per second. So 0.1 means 10 shots per second. 0.2 = 5 shots per second.
refire_classes = [0.35, 0.3, 0.25, 0.2, 0.15]
for i in range(len(refire_classes)):
	refire_classes[i] = int(refire_classes[i]*globalvars.FPS)
#Type affects special effects of the bullets
type_classes = ['kinetic', 'ion', 'laser']
#Bullet speed in pixels per second
speed_classes = [500, 550, 600, 650, 700]
#Make the actual conversion to pixels per second
for i in range(len(speed_classes)):
	speed_classes[i] = speed_classes[i]/float(globalvars.FPS)
#Amount of damage caused
damage_classes = [1,2,3,4,5]
#Time in seconds until the bullet disappears
lifespan_classes = [2.0, 2.5, 3.0]
for i in range(len(lifespan_classes)):
	lifespan_classes[i] = int(lifespan_classes[i]*globalvars.FPS)


#Names of the various weapon classes
weapon_class_names = ['Worthless', 'Scrap', 'Cheap', 'Okay', 'Cool', 'Hot', 'Noble', 'King', 'Emperor', 'Tyrant', 'Transcendent']


def generateWeapon(weapon_class):
	'''Returns a weapon of the given class.'''
	#Start by randomly generating a weapon.
	weapon = Weapon(None)
	#Calculate the class of the weapon.
	actual_class = weapon.getWeaponClass()
	#print 'Weapon is class '+weapon_class_names[actual_class]+' ('+str(actual_class)+') but should be class '+weapon_class_names[weapon_class]+' ('+str(weapon_class)+')'
	#print 'Weapon name: '+weapon.getWeaponName()
	#Now nudge the weapon in the direction of the desired weapon class.
	#randomly select an attribute of the weapon
	randatt = rd.randint(0, num_weapon_attributes-1)
	#while the weapon is above the selected class...
	while actual_class > weapon_class:
		#Decrement selected attribute
		weapon.decrementAttribute(randatt)
		#move to the next weapon attribute
		randatt = (randatt+1)%num_weapon_attributes
		#Calculate the class of the weapon.
		actual_class = weapon.getWeaponClass()
		#print 'Weapon is now class '+weapon_class_names[actual_class]+' ('+str(actual_class)+') but should be class '+weapon_class_names[weapon_class]+' ('+str(weapon_class)+')'
		#print 'Weapon name: '+weapon.getWeaponName()
	#randomly select an attribute of the weapon
	randatt = rd.randint(0, num_weapon_attributes-1)
	#while the weapon is below the selected class...
	while actual_class < weapon_class:
		#Increment selected attribute
		weapon.incrementAttribute(randatt)
		#move to the next weapon attribute
		randatt = (randatt+1)%num_weapon_attributes
		#Calculate the class of the weapon.
		actual_class = weapon.getWeaponClass()
		#print 'Weapon is now class '+weapon_class_names[actual_class]+' ('+str(actual_class)+') but should be class '+weapon_class_names[weapon_class]+' ('+str(weapon_class)+')'
		#print 'Weapon name: '+weapon.getWeaponName()
	#print 'Final Weapon is class '+weapon_class_names[actual_class]+' ('+str(actual_class)+') but should be class '+weapon_class_names[weapon_class]+' ('+str(weapon_class)+')'
	#print 'Final Weapon name: '+weapon.getWeaponName()+'\n'
	weapon.initialize()
	return weapon


kinetic_names = ['Round', 'Bolt', 'Flechete', 'Depleted Uranium', 'Doped Diamond']
ion_names = ['Bubble', 'Pulse', 'Ion', 'Plasma', 'EMP']
laser_names = ['Photon', 'Infrared', 'Ultraviolet', 'Gamma Ray', 'Greasy Photon']
def getWeaponNoun(type_index, damage_index):
	if type_classes[type_index] == 'kinetic':
		return kinetic_names[damage_index]
	elif type_classes[type_index] == 'ion':
		return ion_names[damage_index]
	elif type_classes[type_index] == 'laser':
		return laser_names[damage_index]
	else:
		print 'ERROR in getWeaponNoun. Exiting'; exit()


very_slow_names = ['Flicker', 'Cougher', 'Sneezer', 'Belcher', 'Sprayer']
slow_names = ['Shooter', 'Skew', 'Blaster', 'Blat', 'Stub']
normal_names = ['Driver', 'Serpentine', 'Tri-gun', 'Shotgun', 'Phalanx']
fast_names = ['Spear', 'Sai', 'Trident', 'Katana', 'Excalibur']
very_fast_names = ['Accelerator', 'Cannon', 'Dragon', 'Leviathan', 'Breath of God']
def getWeaponVerb(spread_index, speed_index):
	if speed_index == 0:
		return very_slow_names[spread_index]
	elif speed_index == 1:
		return slow_names[spread_index]
	elif speed_index == 2:
		return normal_names[spread_index]
	elif speed_index == 3:
		return fast_names[spread_index]
	elif speed_index == 4:
		return very_fast_names[spread_index]
	else:
		print 'ERROR in getWeaponVerb. Exiting'; exit()


young_names = ['Premature', 'Unsatisfying', 'Brief', 'Quick', 'Eager']
middle_aged_names = ['Lazy', 'Sluggish', '', 'Stoked', 'Hyper']
old_names = ['Pokey', 'Steady', 'Extended', 'Amped', 'Aggressive']
def getWeaponAdj(refire_index, lifespan_index):
	if lifespan_index == 0:
		return young_names[refire_index]
	elif lifespan_index == 1:
		return middle_aged_names[refire_index]
	elif lifespan_index == 2:
		return old_names[refire_index]
	else:
		print 'ERROR in getWeaponAdj. Exiting'; exit()



class Weapon():
	def __init__(self, shooter, name='default'):
		self.spread_index = rd.randint(0, len(spread_classes)-1)
		self.refire_index = rd.randint(0, len(refire_classes)-1)
		self.type_index = rd.randint(0, len(type_classes)-1)
		self.speed_index = rd.randint(0, len(speed_classes)-1)
		self.damage_index = rd.randint(0, len(damage_classes)-1)
		self.lifespan_index = rd.randint(0, len(lifespan_classes)-1)

		self.name=name
		self.refire_rate=10 #Fires once every refire_rate frames
		self.cooldown=0 #How long until next shot
		self.bullet_speed=10
		self.bullet_lifespan=50 #How long the bullet lasts before expiring
		self.bullet_num=1 #number of bullets fired at a time
		self.bullet_color=colors.pink
		self.spread=0 #spread of bullets fired
		self.attack_angle = 1 #if within this angle to target, can shoot at target
		self.damage = 1
		#1.2 is a fudge factor used so that the ship shoots slightly before 
		#its target moves into range, in case the two ships are closing
		self.weapon_range = self.bullet_speed*self.bullet_lifespan*1.2
		self.shooter = shooter
		#Use the following for ships like the capital ship that have guns offset from their center
		self.offset = (0,0)
		self.is_a = 'gun'

	def initialize(self):
		'''Take all the indicies and initialize the attributes based on them.'''
		self.name=self.getWeaponName()
		self.bullet_num = spread_classes[self.spread_index]
		if self.bullet_num > 1: self.spread = 10
		self.refire_rate = refire_classes[self.refire_index]
		self.bullet_speed = speed_classes[self.speed_index]
		self.damage = damage_classes[self.damage_index]
		self.bullet_lifespan=lifespan_classes[self.lifespan_index]
		if type_classes[self.type_index] == 'kinetic':
			self.bullet_color=colors.yellow
		elif type_classes[self.type_index] == 'ion':
			self.bullet_color=colors.blue
		elif type_classes[self.type_index] == 'laser':
			self.bullet_color=colors.red
		#1.2 is a fudge factor used so that the ship shoots slightly before 
		#its target moves into range, in case the two ships are closing
		self.weapon_range = self.bullet_speed*self.bullet_lifespan*1.2

	def decrementAttribute(self, attribute_index):
		if attribute_index == 0:
			if self.spread_index > 0: self.spread_index -= 1
		elif attribute_index == 1:
			if self.refire_index > 0: self.refire_index -= 1
		elif attribute_index == 2:
			pass #Type has no influence on class
		elif attribute_index == 3:
			if self.speed_index > 0: self.speed_index -= 1
		elif attribute_index == 4:
			if self.damage_index > 0: self.damage_index -= 1
		elif attribute_index == 5:
			if self.lifespan_index > 0: self.lifespan_index -= 1
		else:
			print 'ERROR in weapon.decrementAttribute. Exiting'; exit()

	def incrementAttribute(self, attribute_index):
		if attribute_index == 0:
			if self.spread_index < len(spread_classes)-1: self.spread_index += 1
		elif attribute_index == 1:
			if self.refire_index < len(refire_classes)-1: self.refire_index += 1
		elif attribute_index == 2:
			pass #Type has no influence on class
		elif attribute_index == 3:
			if self.speed_index < len(speed_classes)-1: self.speed_index += 1
		elif attribute_index == 4:
			if self.damage_index < len(damage_classes)-1: self.damage_index += 1
		elif attribute_index == 5:
			if self.lifespan_index < len(lifespan_classes)-1: self.lifespan_index += 1
		else:
			print 'ERROR in weapon.incrementAttribute. Exiting'; exit()

	def getWeaponClass(self):
		rating = 0
		#Spread of 2-3 costs 1 class point.
		#Spread of 4-5 costs 2 class points.
		if self.spread_index > 0:
			rating += 1
			if self.spread_index > 2:
				rating += 1
		#Refire rate of 3 costs 1 class point.
		#Refire rate of 4-5 costs 1 class point.
		if self.refire_index > 1:
			rating += 1
			if self.refire_index > 2:
				rating += 1
		#Ballistic speed of 3 costs 1 class point.
		#Ballistic speed of 4-5 costs 2 class point.
		if self.speed_index > 1:
			rating += 1
			if self.speed_index > 2:
				rating += 1
		#Damage of 2-3 costs 1 class point.
		#Damage of 4-5 costs 2 class points.
		if self.damage_index > 0:
			rating += 1
			if self.damage_index > 2:
				rating += 1
		#Lifespan of 2 costs 1 class point.
		#Lifespan of 3 costs 2 class point.
		if self.lifespan_index > 0:
			rating += 1
			if self.lifespan_index > 1:
				rating += 1
		return rating

	def getWeaponClassName(self):
		return weapon_class_names[self.getWeaponClass()]

	def getWeaponName(self):
		return getWeaponAdj(self.refire_index, self.lifespan_index)+' '+\
			getWeaponNoun(self.type_index, self.damage_index)+' '+\
			getWeaponVerb(self.spread_index, self.speed_index)

	def cool(self):
		if self.cooldown > 0:
			self.cooldown -= 1

	def shoot(self, forceAngle=None):
		'''forceAngle allows a custom firing angle.'''
		if forceAngle is None:
			forceAngle = self.shooter.theta
		#If we are firing spread shot, do things differently
		if self.spread > 0 and self.bullet_num > 1:
			#I calculate half beforehand because for some reason in python
			#rounding works differently when the numbers are negative. 
			#For example:
			# 3/2 = 1
			# -3/2 = -2
			half = self.bullet_num/2
			if self.bullet_num%2 == 0:
				range_of_spread = range(-half/2, half+1)
			else:
				range_of_spread = range(-half, half+1)
			#Adjust the angle for each bullet in the spread
			for adj in range_of_spread:
				angle = forceAngle + self.spread*adj
				self.makeBullet(angle)
		else:
			self.makeBullet(forceAngle)
		#reset cooldown
		self.cooldown = self.refire_rate

	def makeBullet(self, angle):
		tempbullet = Bullet(angle, self.shooter.rect.centerx+self.offset[0],\
			self.shooter.rect.centery+self.offset[1], self.damage, self.shooter)
		#Set bullet attributes
		tempbullet.speed = self.bullet_speed
		tempbullet.setColor(self.bullet_color)
		tempbullet.timeToLive = self.bullet_lifespan
		#Add bullet to the sprite groups
		globalvars.tangibles.add(tempbullet)

	def getWeaponType(self):
		return type_classes[self.type_index]

	def toStringArray(self):
		str_array = [self.name,
			'Class: '+self.getWeaponClassName(),
			'Type: '+self.getWeaponType(),
			'Refire rate: '+str(self.refire_rate),
			'Projectile speed: '+str(self.bullet_speed),
			'Damage: '+str(self.damage),
			'Range: '+str(self.weapon_range),
			'Projectiles per shot: '+str(self.bullet_num)]
		return str_array


class HitBoxTesterGun(Weapon):
	def __init__(self, shooter, name='default'):
		Weapon.__init__(self,shooter)
		self.name='HitBoxTesterGun'
		self.cooldown=0 #How long until next shot
		self.bullet_speed=5
		self.refire_rate=10 #Fires once every refire_rate frames
		self.bullet_lifespan=150 #How long the bullet lasts before expiring
		self.bullet_color=colors.yellow
		self.shooter = shooter
		self.is_a = 'gun'

	def cool(self):
		if self.cooldown > 0:
			self.cooldown -= 1

	def shoot(self):
		self.makeBullet(self.shooter.theta)
		#reset cooldown
		self.cooldown = self.refire_rate


	def makeBullet(self, angle):
		tempbullet = HitBoxTestBullet(angle, self.shooter.rect.centerx,\
			self.shooter.rect.centery, self.shooter)
		#Set bullet attributes
		tempbullet.speed = self.bullet_speed
		tempbullet.setColor(self.bullet_color)
		tempbullet.timeToLive = self.bullet_lifespan
		#Add bullet to the sprite groups
		globalvars.tangibles.add(tempbullet)

	def toStringArray(self):
		return [self.name, 'This is to be used for testing purposes only.']


#def testing():
#	print '\nThere are '+str(len(spread_classes)*len(refire_classes)*len(type_classes)*len(speed_classes)*len(damage_classes)*len(lifespan_classes))+' unique weapons.\n'
#	for i in range(len(weapon_class_names)):
#		generateWeapon(i)
#testing()
#exit()
