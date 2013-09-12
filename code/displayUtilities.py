import pygame
import game
import colors
import time
from geometry import *

#copied from stardog utils.py
#setup images
#if there is extended image support, load .gifs, otherwise load .bmps.
#.bmps do not support transparency, so there might be black clipping.
ext = ".bmp"
if pygame.image.get_extended(): ext = ".gif"

def loadImage(filename):
	'''copied from stardog utils.py '''
	try:
		image = pygame.image.load(filename).convert()
		#colorkey tells pygame what color to make transparent.
		#We assume that the upper left most pixel's color is the color to make transparent.
		colorkey = image.get_at((0,0))
		image.set_colorkey(colorkey)
	except pygame.error:
		image = pygame.image.load("images/default" + ext).convert()
		image.set_colorkey(colors.white)
	return image



def trunc(f, n):
	'''Truncates/pads a float f to n decimal places without rounding.
	Source: http://stackoverflow.com/questions/783897/truncating-floats-in-python '''
	slen = len('%.*f' % (n, f))
	return str(f)[:slen]


def displayShipLoc(ship):
	string = "Player X,Y: "+trunc(ship.rect.centerx, 0)+','+trunc(ship.rect.centery,0)+\
		'. Speed: '+trunc(ship.speed,0)+'. MaxSpeed: '+str(ship.maxSpeed)
	game.writeTextToScreen(string=string, font_size=36, \
			       color=colors.white, pos=(400,10))


class PlayerInfoDisplayer():
	'''I have a hunch that this is not the best way to do this,
	but it will work for now.
	Displays player information at the top of the screen.'''
        def __init__(self):
		pass

	def update(self, _):
		displayShipLoc(game.player)



def formatTime(seconds):
	minutes = str(int(seconds/60))
	sec = str(int(seconds%60))
	if len(sec) == 1: sec = '0'+sec
	return minutes+':'+sec


class TimeTrialAssistant():
	'''Displays an arrow pointing towards the destination
	and counts down time remaining in race.'''
        def __init__(self, target):
		self.target = target #A location
		self.radius = min(game.WIDTH, game.HEIGHT)/2
		self.elapsed_time = 0
		#Track time in seconds as well as what the time the game 
		#thinks has elapsed. for testing purposes.
		self.start_time = time.time()
		self.finish_reached = False

	def update(self, offset):
		#Draw a bulls eye (multiple overlapping red and white 
		#circles centered at the destination point.
		target = (self.target[0] - offset[0], self.target[1] - offset[1])
		pygame.draw.circle(game.screen, colors.red, target, 50, 0)
		pygame.draw.circle(game.screen, colors.white, target, 40, 0)
		pygame.draw.circle(game.screen, colors.red, target, 30, 0)
		pygame.draw.circle(game.screen, colors.white, target, 20, 0)
		pygame.draw.circle(game.screen, colors.red, target, 10, 0)

		if self.finish_reached: return True

		#Update elapsed time
		self.elapsed_time += 1.0 / game.game_obj.fps
		#TESTING: alternative elapsed time
		alt_elapsed = time.time() - self.start_time
		#Write the elapsed time to the top of the screen.
		string = 'Time: '+formatTime(self.elapsed_time)+\
			'. Alt Time: '+formatTime(alt_elapsed)
		game.writeTextToScreen(string=string, font_size=36,\
				       color=colors.white, pos=(400,10))

		#Distance to target
		dtt = distance(game.player.rect.center, self.target)

		#Only display the guiding arrow if player is too far away to see the target
		if dtt > self.radius:
			#Get player's angle to target regardless of current player orientation.
			att = angleFromPosition(game.player.rect.center, target)
			#Get a point radius distance from the player in the 
			#direction of the target, centered on the screen.
			#This will form the tip of the arrow
			tip = translate((game.CENTERX, game.CENTERY), att, self.radius)
			#Get a point radius-20 distance from the player in the 
			#direction of the target
			#This will be used to build the base of the triangle.
			base = translate((game.CENTERX, game.CENTERY), att, self.radius-20)
			#get angles + and - 90 degrees from the angle to the target
			leftwing = rotateAngle(att, -90)
			rightwing = rotateAngle(att, 90) 
			#Use these angles and the point closer to the player to 
			#get points for the "wings" of the triangle that forms 
			#the head of the arrow.
			leftwingtip = translate(base, leftwing, 10)
			rightwingtip = translate(base, rightwing, 10)
			#Draw a filled in polygon for the arrow head.
			pygame.draw.polygon(game.screen, colors.yellow, \
				[leftwingtip, tip, rightwingtip])
			#Get a point radius-50 distance from the player in the 
			#direction of the target.
			#This will be used to draw the line part of the arrow.
			linestart = translate((game.CENTERX, game.CENTERY), att, self.radius-50)
			#Draw a 20 pixel thick line for the body of the arrow.
			pygame.draw.line(game.screen, colors.yellow, linestart, base, 10)
		#Check if the player has reached the destination.
		if dtt < 40:
			#If so, end the race.
			self.finish_reached = True
			game.writeTextToScreen(string='TIME TRIAL COMPLETED',\
				font_size=64,pos=(game.WIDTH/3, game.HEIGHT/2))
			pygame.display.flip()
			time.sleep(2) #Sleep for 2 seconds.
		pass


class TimeLimit():
	'''Initially to be used for the gem wild scenario in 
	which the player has a limited amount of time to 
	grab as many gems as possible.'''
        def __init__(self, time_limit=0):
		self.points = 0
		self.time_limit = time_limit #in seconds
		self.elapsed_time = 0
		#Track time in seconds as well as what the time the game 
		#thinks has elapsed. for testing purposes.
		self.start_time = time.time()
		self.finish_reached = False

	def update(self, offset):
		if self.finish_reached: return True

		#Update elapsed time
		self.elapsed_time += 1.0 / game.game_obj.fps
		#TESTING: alternative elapsed time
		alt_elapsed = time.time() - self.start_time
		#Write the elapsed time to the top of the screen.
		string = 'Time: '+formatTime(self.elapsed_time)+\
			'. Alt Time: '+formatTime(alt_elapsed)+\
			' Points:'+str(self.points)
		game.writeTextToScreen(string=string, font_size=36,\
				       color=colors.white, pos=(400,10))

		#Check to see if time has run out.
		if self.elapsed_time >= self.time_limit:
			#If so, end the scenario.
			self.finish_reached = True
			game.writeTextToScreen(string='GEM WILD COMPLETED',\
				font_size=64,pos=(game.WIDTH/3, game.HEIGHT/2))
			pygame.display.flip()
			time.sleep(2) #Sleep for 2 seconds.
			game.wipeOldScenario()
		pass

