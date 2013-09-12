import pygame
import random as rd
import sys
sys.path.append('code')
import player
import colors
import ship
import testFunctions as test
import menus
from geometry import distance, angleFromPosition, translate, rotateAngle

DEBUG = True

FPS = 30 #frames per second

WIDTH = 900
HEIGHT = 700

CENTERX = WIDTH / 2
CENTERY = HEIGHT / 2

#Used by physicalObject to define what each physicalObject is.
BULLET = 0
OTHER = 1
SHIP = 2
FIXEDBODY = 3
HEALTH = 4
ASTEROID = 5

#The least distance to check for a collision. Might need adjusted if we start using really big objects.
MINSAFEDIST = 1024

BGCOLOR = colors.black
BGIMAGE = None

#instantiate sprite groups
tangibles = pygame.sprite.Group()
intangibles = pygame.sprite.Group()
#This last group will contain any sprites that will tickle whiskers
whiskerables = pygame.sprite.Group()
#An array of fixed-location, white specks designed to reveal player motion by their relative movement.
dust = []

#set up the display:
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
#Player must be created before scenario is called.
player = player.Player('images/ship')

#An object that displays scenario-specific hud stuff.
hud_helper = None

#If arena is set to anything other than zero, then the player will be forced to stay inside the arena and all other objects will also be pointed roughly in the direction of the center of the arena. This is used for 
arena = 0

def writeTextToScreen(string='', font_size=12, color=colors.white, pos=(0,0)):
	font = pygame.font.Font(None, font_size)
	text = font.render(string, 1, color)
	textpos = text.get_rect(center=pos)
	screen.blit(text, textpos)


def wipeOldScenario():
	#In order to change immutable variables, you have to declare them global
	global BGCOLOR, arena

	for sprt in tangibles: sprt.kill()
	for sprt in intangibles: sprt.kill()
	for sprt in whiskerables: sprt.kill()

	BGCOLOR = colors.black
	BGIMAGE = None

	#Add the player back in.
	tangibles.add(player)
	player.setHealthBar()

	#Immediately clear the panel
	game_obj.panel = None

	#Reset the hud_helper
	hud_helper = None

	#Reset the arena
	arena = 0


def updateDust(offset):
	'''For each dust particle,
	If the dust is too far from the player then move it to a location
	offscreen, but in the direction that the player is moving.
	Otherwise, just draw the dust with the update function.'''
	global dust
	limit = WIDTH*2
	for i in xrange(len(dust)):
		dist = distance(dust[i].rect.center, player.rect.center)
		if dist > limit:
			magnitude = rd.randint(WIDTH, WIDTH*2)
			rotation = rd.randint(-90, 90)
			dust[i].rect.center = translate(player.rect.center,\
				rotateAngle(player.theta, rotation),\
				magnitude)
		elif dist < WIDTH:
			dust[i].update(offset)


class Game:
	""" """
	def __init__(self):
		self.fps = FPS
		self.top_left = 0, 0

		self.offsetx = 0
		self.offsety = 0

		#key polling:
		#Use this to keep track of which keys are up and which 
		#are down at any given point in time.
		self.keys = []
		for _i in range (322):
			self.keys.append(False)
		#mouse is [pos, button1, button2, button3,..., button6].
		#new Apple mice think they have 6 buttons.
		#Use this to keep track of which mouse buttons are up and which 
		#are down at any given point in time.
		#Also the tuple, self.mouse[0], is the current location of the mouse.
		self.mouse = [(0, 0), 0, 0, 0, 0, 0, 0]
		#pygame setup:
		self.clock = pygame.time.Clock()

		self.pause = False

		self.panel = None


	def run(self):
		"""Runs the game."""
		self.running = True

		#The in-round loop (while player is alive):
		while self.running:
			#frame maintainance:
			pygame.display.flip()
			self.clock.tick(FPS) #aim for FPS but adjust vars for self.fps.
			self.fps = max(1, int(self.clock.get_fps()))

			#Skip the rest of this loop until the game is unpaused.
			if self.pause:
				#Write paused in the middle of the screen
				writeTextToScreen(string='PAUSED', font_size=128,\
					pos=(WIDTH/3, HEIGHT/2))
				#Check for another s key press to unpause the game.
				for event in pygame.event.get():
					if event.type == pygame.KEYDOWN and event.key == 115: #s key
						self.pause = not self.pause
				#Skip the rest of this loop until the game is unpaused.
				continue

			#Display the panel
			if not self.panel is None:
				self.panel.draw()
				#Check for another m key press to remove the panel.
				for event in pygame.event.get():
					#Check for event m key being pressed to
					#remove the menu.
					if event.type == pygame.KEYDOWN and \
					event.key == 109: #m key
						self.panel = None
						break
					#Pass all other events to the panel
					else:
						self.panel.handleEvent(event)
				#Skip all the rest while displaying the menu.
				#This effectively pauses the game.
				continue

			#event polling:
			#See what buttons may or may not have been pushed.
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					self.running = False
				elif event.type == pygame.MOUSEBUTTONDOWN:
					self.mouse[event.button] = 1
					self.mouse[0] = event.pos
				elif event.type == pygame.MOUSEBUTTONUP:
					self.mouse[event.button] = 0
				#elif event.type == pygame.MOUSEMOTION:
				#	self.mouse[0] = event.pos
				elif event.type == pygame.KEYDOWN:
					self.keys[event.key % 322] = 1
					print "TODO TESTING: key press "+str(event.key)

					#Respond to key taps.
					#Keys that we want to respond to holding them down
					#will be dealt with below.
					if event.key == 273: #Pressed up arrow
						#increase speed by a fraction of max up to max.
						player.targetSpeed = min(player.maxSpeed,\
							player.targetSpeed +\
							player.maxSpeed*\
							player.speedIncrements)
					elif event.key == 274: #Pressed down arrow
						#decrease speed by a fraction of 
						#max down to zero.
						player.targetSpeed = max(0,\
							player.targetSpeed -\
							player.maxSpeed*\
							player.speedIncrements)
					elif event.key == 27: #escape key or red button
						self.running = False
					elif event.key == 109: #m key
						self.panel = menus.getTestingPanel()
						continue
					elif event.key == 112: #p key
						player.parkingBrake()
					elif event.key == 113: #q key
						#Obliterate destination.
						#Change to free flight.
						player.killDestination()
					elif event.key == 115: #s key
						self.pause = not self.pause; continue
					elif event.key == 116: #t key
						#shoot a bunch of hit box testers 
						#in towards the player
						print 'Width: '+\
						    str(player.image.get_width())+\
						' vs '+str(player.rect.width)
						print 'Height: '+\
						    str(player.image.get_height())+\
						' vs '+str(player.rect.height)
						test.hitBoxTest(player.rect.center)
					elif event.key == 47: 
						#forward slash (question mark
						#without shift) key.
						#Useful for querying one time info.
						print 'Print player destination: '+\
						str(player.destx)+','+\
						str(player.desty)

					#Separate if so other keys don't interfere
					#with this.
					if event.key == 32:
						#Pressed space bar
						#Force shot tells this to shoot
						#even if a target 
						#is not obviously in view. NPC's
						#will not take such wild shots.
						player.shoot(force_shot=True)

				elif event.type == pygame.KEYUP:
					#Keep track of which keys are no longer
					#being pushed.
					self.keys[event.key % 322] = 0

			##This will make the player move towards the mouse 
			##without any clicking involved.
			##Set player destination to current mouse coordinates.
			if self.mouse[1]:
				x,y = pygame.mouse.get_pos()
				x += self.offsetx
				y += self.offsety
				player.setDestination((x,y))

			#Respond to key holds.
			#Keys that we want to respond to tapping them
			#will be dealt with above.
			if self.keys[276]: #Pressed left arrow
				player.turnCounterClockwise()
			elif self.keys[275]: #Pressed right arrow
				player.turnClockwise()
			#This is not part of the above else if.
			#You can shoot and turn at the same time.
			if self.keys[32]: #Pressed space bar
				#Force shot tells this to shoot even if a target 
				#is not obviously in view. NPC's will not take such wild shots.
				player.shoot(force_shot=True)


			#draw BGCOLOR over the screen
			#TODO as a game effect, it is super neato to temporarily NOT do this.
			screen.fill(BGCOLOR)

			#Check all collisions
			collisionHandling()

			#If arena is non-zero, then make sure player and all 
			#whiskerables are within it
			if arena > 0:
				#The inner concentric ring bounces the player back 
				#towards center (don't actually bounce, just change 
				#angle directly towards center. The outer 
				#concentric ring, defined by distance from center 
				#plus object radius will bounce asteroids in a 
				#semi random direction towards the center-ish area.

				#Make sure player is within arena.
				#If not, change player's heading to be towards 0,0
				if distance(player.rect.center, (0.,0.)) > arena:
					player.theta = angleFromPosition(\
						player.rect.center, (0.,0.))
					player.updateImageAngle()
				#Check each whiskerable and if it is more than 
				#arena + diameter from center, then change its 
				#angle to point somewhere within the arena too.
				for w in whiskerables:
					if distance(w.rect.center, (0.,0.)) > \
					arena + w.radius:
						#Whiskerables reflect randomly
						#off arena boundaries towards a
						#point somewhere within 3/4 the
						#center of the arena.
						limit = 3*arena/4
						x = rd.randint(-limit, limit)
						y = rd.randint(-limit, limit)
						if not w.direction is None:
							#Asteroids distinguish between their orientation,
							#theta, and direction of movement, direction.
							#Thus we want direction changed, not theta.
							w.direction = angleFromPosition(\
								w.rect.center, (x,y))
						else:
							w.theta = angleFromPosition(w.rect.center, (x,y))

			#update all sprites:

			#First tell the ships what is closest to them
			#so that they can avoid collisions
			setClosestSprites()
			#Get the offset based on the player location.
			self.offsetx = player.rect.centerx - CENTERX
			self.offsety = player.rect.centery - CENTERY
			#Finally update all the sprites
			intangibles.update((self.offsetx,self.offsety))
			updateDust((self.offsetx,self.offsety))
			tangibles.update((self.offsetx,self.offsety))

			#Redraw the player to make sure things like the arena 
			#background aren't drawn overtop of the player.
			player.playerUpdate()
			player.drawAt((CENTERX, CENTERY))
			#Also redraw the player's healthbar.
			player.myHealthBar.update((self.offsetx,self.offsety))

			hud_helper.update((self.offsetx,self.offsety))
		#end round loop (until gameover)
	#end game loop


#Create a game object. Currently only used by scenarios.py. I wonder if this indicates that there is a better way? TODO
game_obj = Game()




#The following were yanked out of behaviors.py and behaviors.py was removed because behaviors.py and game.py were mutually importing which can lead to errors. In any case, behaviors was only imported by game.py.

def setClosestSprites():
	'''Pre:
	Post: For all ships in the whiskerables sprite list, the closest sprite 
	and the distance to that sprite is set. This is used for helping NPC 
	ships avoid collisions.'''
	#Get all the whiskerable sprites in an array
	sprite_list = whiskerables.sprites()
	#TODO I'd like to make use of sorting like I do for collision checking with this, but recently it was gumming up the works, so I'm simplifying it for now.
	#Sort them by their top point as is done when checking for collisions.
	#sprite_list = sorted(sprite_list, \
	#	key=lambda c: c.rect.topleft[1]+c.rect.height,\
	#	reverse=True)
	#For each sprite...
	for i in xrange(len(sprite_list)):
		#Get the next sprite to deal with.
		A = sprite_list[i]
		#only ships can avoid objects.
		if A.is_a != SHIP: #TODO this could be more efficient by keeping another group that is just ships. Of course there is a cost there. It might be worth profiling at some point to see if this is better or another group that is just non-player ships is better.
			continue
		#Reset closest sprite and the distance to that sprite. Sprites 
		#further than this distance will be ignored.
		closest_sprite = None
		least_dist = MINSAFEDIST
		#search for too close sprites
		for j in xrange(len(sprite_list)):
			if j != i:
				B = sprite_list[j]
				dist = distance(A.rect.center, B.rect.center) - B.radius - A.radius
				if dist < least_dist:
					least_dist = dist
					closest_sprite = B
		'''#TODO this is the old way it was done when the sprite list was sorted, but I was accidentally missing checks on certain sprites so I simplified it for the time being.
		#search forward for too close sprites
		for j in xrange(i+1, len(sprite_list)):
			B = sprite_list[j]
			dist = distance(A.rect.center, B.rect.center) - B.radius - A.radius
			if dist < least_dist:
				least_dist = dist
				closest_sprite = B
				#break #TODO TESTING
			#TODO TESTING
			#elif abs(A.rect.centerx - B.rect.centerx) > least_dist:
			#	break
		#search backward for too close sprites
		count_back = []
		if i > 0:
			count_back = range(0, i-1)
			count_back.reverse()
		for j in count_back:
			B = sprite_list[j]
			dist = distance(A.rect.center, B.rect.center) - B.radius - A.radius
			if dist < least_dist:
				least_dist = dist
				closest_sprite = B
				#break #TODO TESTING
			#TODO TESTING
			#elif abs(A.rect.centerx - B.rect.centerx) > least_dist:
			#	break'''
		#Set sprite A's closest sprite and the distance to that sprite.
		#if not closest_sprite is None: print closest_sprite.image_name+' at '+str(least_dist) #TODO TESTING
		A.setClosest(closest_sprite, least_dist)


def collisionHandling():
	'''The following function comes from pseudo code from
	 axisAlignedRectangleCollision.txt that has been modified.'''
	#Get a list of all the sprites
	sprite_list = tangibles.sprites()
	#sort the list in descending order based on each 
	#sprite's y coordinate (aka top) plus height.
	#Remember that larger y coordinates indicate further down
	#on the screen.
	#Reverse tells sorted to be descending.
	#rect.topleft[1] gets the y coordinate, top.
	sprite_list = sorted(sprite_list, \
		key=lambda c: c.rect.topleft[1]+c.rect.height,\
		reverse=True)
	#iterate over the sprite list
	for i in xrange(len(sprite_list)):
		A = sprite_list[i]
		for j in xrange(i+1, len(sprite_list)):
			B = sprite_list[j]
			#if A's least y coord (A's top) is > B's
			#largest y coord (B's bottom)
			#then they don't overlap and none of the following
			#sprites overlap A either becuase the list is sorted
			#by bottom y coordinates.
			#We therefore skip the rest of the sprites in the list.
			if A.rect.topleft[1] > B.rect.topleft[1]+B.rect.height:
				break
			else:
				#Otherwise, we need to see if they overlap
				#in the x direction.
				#if A's greatest x coord is < B's least x coord
				#or B's greatest x coord is < A's least x coord
				#then they don't overlap, but one of the following 
				#sprites might still overlap so we move to the
				#next sprite in the list.
				#OLD WAY based on rectangles:
				#if A.rect.topleft[0]+A.rect.width < B.rect.topleft[0]\
				#or B.rect.topleft[0]+B.rect.width < A.rect.topleft[0]:
				#NEW WAY based on circles:
				#If the distance between our centers is larger than are 
				#summed radii, then we have not collided.
				if distance(A.rect.center, B.rect.center) > A.radius+B.radius:
					pass
				else:
					#they overlap. They should handle 
					#collisions with each other.
					A_died = A.handleCollisionWith(B)
					B.handleCollisionWith(A)
					#If A has died, then don't worry about A
					#colliding with anything else.
					if A_died:
						break


