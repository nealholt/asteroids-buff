import pygame
import math
from displayUtilities import loadImage
import geometry
from colors import white
import globalvars

class PhysicalObject(pygame.sprite.Sprite):
	def __init__(self, centerx=0.0, centery=0.0, width=0, height=0, image_name=None, color=white):

		#Sprite tutorial being used is here:
		# http://kai.vm.bytemark.co.uk/~piman/writing/sprite-tutorial.shtml
		#Sprite class:
		# http://pygame.org/docs/ref/sprite.html
		pygame.sprite.Sprite.__init__(self)
		#There is nothing particularly special about any of the following default values.

		self.color = color

		#speed. All speeds will be in pixels per second.
		self.speed = 0.0
		self.targetSpeed = 0.0
		self.maxSpeed = 5.0
		#Acceleration in pixels per second squared. 
		#Each frame the speed goes up by this amount.
		self.dv = 1.0

		#Rotation. All rotations are in degrees
		self.theta = 0.0
		self.dtheta = 3.0

		#For simplicity, the player can set the target or goal speed in 
		#increments equal to this fraction of the maxSpeed.
		self.speedIncrements=1./4.
		#Speed at which turn rate is maximal
		self.maxTurnSpeed=self.maxSpeed*self.speedIncrements
		#Rate at which turn rate decays as speed moves away from maxTurnSpeed
		self.turnRateDecay=1.

		#you can be within this many degrees of the target to stop turning
		self.acceptableError = 0.5

		self.destination = (0.0, 0.0)

		self.image_name = image_name

		#The location of this object. It is two floats for accuracy, 
		#because rectangles will be rounded to an integer which can cause 
		#an inability to move diagonally at slow speeds because the integer 
		#always rounds down.
		#The downside of this is that there are now two valid location variables self.loc and self.rect.center, both of which need to be maintained and kept equal to each other.
		self.loc = (centerx, centery)

		if self.image_name is None:
			self.image = pygame.Surface([width, height])
			self.image.fill(self.color)
			self.base_image = self.image
		else:
			self.image = loadImage(self.image_name)
			#Base image is needed because we need a reference to the
			#original image that is never modified.
			#self.base_image is used in updateImageAngle.
			self.base_image = loadImage(self.image_name)
			self.rect = self.base_image.get_rect()

		self.rect = self.image.get_rect()
		self.rect.centerx = self.loc[0]
		self.rect.centery = self.loc[1]

		#For now calculate the radius as the average of the width and height.
		#Divide by 4 because we average the width and height and also divide them in half
		#to calculate radius rather than diameter.
		#Old way: This made the asteroids slightly too large.
		#self.radius = max(int((self.rect.width+self.rect.height)/4), 1)
		self.radius = max(int(min(self.rect.width,self.rect.height)/2), 1)

		#What is this object.
		self.is_a = globalvars.OTHER

		#We use closest_sprite to help the NPC's avoid objects.
		self.closest_sprite = None
		self.dist_to_closest = globalvars.MINSAFEDIST


	def handleCollisionWith(self, other_sprite):
		'''React to a collision with other_sprite.'''
		pass


	def update(self):
		'''This is called by game.py. Mostly objects implementing 
		physicalObjects should have their own version of this 
		function.
		Return False means "I didn't die so don't remove me." '''
		return False


	def updateImageAngle(self):
		self.image = pygame.transform.rotate(self.base_image, -self.theta).convert_alpha()
		#WITH the following code, the ship rotates smoothly relative to its health bar, but since the screen centers on the player, these constant small adjustments cause all the images drawn relative to the player to jiggle.
		#WITHOUT the following code, there is no jiggle, but the ships rotate a little more weirdly and the hit boxes might be slightly off.
		#For now, I choose to run without the following code.
		#temp = self.rect.topleft
		#self.rect = self.image.get_rect()
		#self.rect.topleft = temp


	def noClipWith(self,other):
		'''Everything defaults to clipping.
		The idea was to have one's own bullets not clip with one's 
		self since the bullet starts out under the object that fired it
		which would otherwise cause everything to shoot itself.'''
		return False

	def setColor(self, color):
		self.color = color
	        self.image.fill(color)

	def setClosest(self, closest_sprite, dist):
		self.closest_sprite = closest_sprite
		self.dist_to_closest = dist

	def calculateDTheta(self):
		'''This is used for xwing vs tie fighter-style
		maneuvering in which turn rate is reduced at 
		higher speeds. The following formula gives the maximum turn rate of
		self.dtheta only at 1/4 max velocity. The modifier on turn rate
		breaks down as follows:
		f(x) = -abs(x-1/4)+1
		Speed	Turn
		0	3/4
		1/4	1
		1/2	3/4
		3/4	1/2
		1	1/4
		'''
		return max((-self.turnRateDecay*\
				abs((self.speed / self.maxSpeed) - \
				self.maxTurnSpeed) + 1)\
				* self.dtheta,\
			0)

	def turnCounterClockwise(self, delta=None):
		'''Turn in the desired direction.
		I'm using an angle system like stardog uses such that 
		east=0, north=-90, west=180, south=90'''
		if delta is None: delta = self.calculateDTheta()
		self.theta -= delta
		if self.theta < -180: self.theta += 360
		self.updateImageAngle()

	def turnClockwise(self, delta=None):
		'''Turn in the desired direction
		I'm using an angle system like stardog uses such that 
		east=0, north=-90, west=180, south=90'''
		if delta is None: delta = self.calculateDTheta()
		self.theta += delta
		if self.theta > 180: self.theta -= 360
		self.updateImageAngle()

	def turn(self, delta):
		'''I'm using an angle system like stardog uses such that 
		east=0, north=-90, west=180, south=90'''
		self.theta += delta
		if self.theta > 180: self.theta -= 360
		elif self.theta < -180: self.theta += 360
		self.updateImageAngle()

	def park(self):
		'''Slow to a stop near target destination.'''
		itersToStop = self.speed / self.dv
		if not self.speed == 0 and \
		itersToStop >= geometry.distance(self.rect.center, self.destination) / self.speed:
			#Decelerate
			self.speed = max(0, self.speed - self.dv)
			self.targetSpeed = self.speed
			return True
		return False

	def approachSpeed(self):
		'''Modify this object's speed to approach the 
		goal speed (aka targetSpeed).'''
		if abs(self.speed - self.targetSpeed) < self.dv:
			self.speed = self.targetSpeed
		elif self.speed < self.targetSpeed:
			#Accelerate
			self.speed = min(self.maxSpeed, self.speed + self.dv)
		else:
			#Decelerate
			self.speed = max(0, self.speed - self.dv)

	def setDestination(self,point):
		'''Pre: point must be a tuple of integers or floats.'''
		self.destination = point

	def killDestination(self):
		self.destination = None

	def getAngleToTarget(self, target=None):
		'''This is a major departure from the old implementation. 
		THIS will pretend that up is positive Y values and down is 
		negative Y values as is standard in math, but not computer 
		science.'''
		if target is None:
			x,y = self.destination
		elif isinstance(target, tuple):
			x,y = target
		else:
			x,y = target.rect.center
		rise = y - self.rect.centery
		run = x - self.rect.centerx
		#As I understand it, this ought to return one angle to the target,
		#though not necessarily the shortest angle.
		#Range of arctan is negative pi to pi and the world is upside down
		#because down is positive in the y direction.
		#See testAngleToTarget.py in backups for some examples.
		angle_to_target = math.degrees(math.atan2(rise, run)) - self.theta
		if angle_to_target < -180: angle_to_target += 360
		if angle_to_target > 180: angle_to_target -= 360
		return angle_to_target

	def turnTowards(self):
		"""This was copied out of scripts.py in stardog and 
		modified slightly. Collision avoidance is all my 
		own, however."""
		#Collision avoidance: Avoid Collisions!
		#The following can only be used to suppress
		#turning if they are true. If false, they have no effect.
		dontTurnLeft = False
		dontTurnRight = False
		#If there is a closest sprite, amend turning to avoid it.
		if not self.closest_sprite is None:
			angle = self.getAngleToTarget(target=self.closest_sprite)
			#If the ship is at any angle closer than a right angle, consider altering its turn
			abs_angle = abs(angle)
			if abs_angle < 90:
				#self.dist_to_closest is the distance from this sprite's
				#center to self.closest_sprite's center. We need to factor 
				#in the radius for these sprites.
				actual_distance = self.dist_to_closest - \
					self.radius-self.closest_sprite.radius
				#TODO. These constants might need adjusted.
				#Previously the following was just this commented out portion. I thought making it trickier might reduce the jiggle. It did not.
				#if actual_distance + abs_angle < 30:
				if actual_distance < 20:

					#Too close. It's vital that we turn away from the object.
					if angle < 0:
						self.turnClockwise()
						return True
					else:
						self.turnCounterClockwise()
						return True
				#elif actual_distance + abs_angle < 70:
				elif actual_distance < 40:
					#It's not too close yet, but don't get any closer.
					if angle < 0:
						dontTurnLeft = True
					else:
						dontTurnRight = True
			#Reset closest sprite.
			self.closest_sprite = None
			self.dist_to_closest = globalvars.MINSAFEDIST


		angleToTarget = self.getAngleToTarget()
		#If we need to turn more towards the target or there is an 
		#object in front of us
		if abs(angleToTarget) > self.acceptableError:
			#Get the amount to turn. It may be less than the 
			#amount this object is capable of turning.
			#Only turn this small amount if there is no object in
			#front of us.
			if abs(angleToTarget) < self.calculateDTheta():
				if dontTurnLeft and angleToTarget < 0:
					pass
				elif dontTurnRight and angleToTarget > 0:
					pass
				else:
					self.turn(angleToTarget)
			#Turn counter clockwise if that's the direction of our 
			#target and there is no obstacle in that direction or
			#if there is an obstacle in front of us and to the right.
			elif angleToTarget < 0 and not dontTurnLeft:
				self.turnCounterClockwise()
			#In all other cases turn clockwise
			elif not dontTurnRight:
				self.turnClockwise()


	def move(self):
		'''self.loc is a tuple of floats, but rect.topleft is always
		converted to an integer because it has to be fitted to particular 
		pixels. At low speeds, the rounding down of the integer tuple
		can prevent diagonal motion. That's why we use self.loc instead.'''
		self.loc = geometry.translate(self.loc, \
			self.theta, self.speed)
		self.rect.centerx = self.loc[0]
		self.rect.centery = self.loc[1]


	def translate(self, angle, magnitude):
		self.loc = geometry.translate(self.loc, \
			angle, magnitude)
		self.rect.centerx = self.loc[0]
		self.rect.centery = self.loc[1]


	def draw(self, offset=(0,0)):
		x,y = self.rect.topleft
		pos = x - offset[0], y - offset[1]
		globalvars.screen.blit(self.image, pos)
		#TODO TESTING. Useful for looking at hit boxes.
		#Get a copy of the rect to draw at the proper offset position
		#temprect = pygame.Rect(self.rect.left, self.rect.top, self.rect.width, self.rect.height)
		#temprect.topleft = pos
		#pygame.draw.rect(globalvars.screen, white, temprect)

	def drawAt(self, position=(0,0)):
		pos = position[0] - self.rect.width/2, position[1] - self.rect.height/2
		globalvars.screen.blit(self.image, pos)


	def getArea(self):
		return self.rect.width*self.rect.height


	def bounceOff(self, other):
		'''Other is another physical object that this physical object 
		just struck and should bounce off of.

		two objects, A and B, collide. let theta be the angle of the line from the 
		center of A to the center of B. Let A be the smaller of the two. let 
		theta' be a line perpendicular to theta. If A's direction is less 
		than 90 degrees from pointing at B then reflect A's direction over 
		theta'. Reduce both objects' speeds. 
		else move A's direction half way to theta in the direction away from B. 
		Increase A's speed. Decrease B's speed. (This is the case where A 
		is hit from behind despite moving in the same direction as B.)
		'''
		angleToOther = self.getAngleToTarget(target=other)
		if abs(angleToOther) < 45:
			#This object should bounce off other in a dramatically
			#new direction. Specifically, our angle should be 
			#reflected over the line perpendicular to the line that
			#passes through the center of this and other.
			#First pass for code follows. This is good enough for now.
			if angleToOther < 0:
				self.turnClockwise(110)
			else:
				self.turnCounterClockwise(110)
		elif abs(angleToOther) < 90:
			#This object should bounce off other in a dramatically
			#new direction. Specifically, our angle should be 
			#reflected over the line perpendicular to the line that
			#passes through the center of this and other.
			#First pass for code follows. This is good enough for now.
			if angleToOther < 0:
				self.turnClockwise(65)
			else:
				self.turnCounterClockwise(65)
		else:
			#this should sort of be bounced to a higher speed, as 
			#when an object is hit from behind.
			#The angle will also change slightly to be more in the
			#direction of the object that struck us.
			#Specifically, change our angle to be halfway between 
			#our angle and the angle of other.
			#First pass for code follows. This is good enough for now.
			amountToTurn = (180 - abs(angleToOther))/2
			if angleToOther < 0:
				self.turnCounterClockwise(amountToTurn)
			else:
				self.turnClockwise(amountToTurn)
			#Use max because speed*1.5 might be zero.
			self.speed = max(self.speed*1.5, 10)
		#Prevent multiple consecutive collisions with the same object
		limit = 10; i = 0 #also prevent infinite loops
		while self.speed > 0 and geometry.distance(self.rect.center, other.rect.center) <= self.radius+other.radius and i < limit:
			i+=1
			self.move()

