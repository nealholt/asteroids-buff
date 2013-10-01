import pygame
import globalvars
from colors import *

def writeTextToScreen(string='', fontSize=12, color=white, pos=(0,0)):
	'''Returns the rectangle of the given text.'''
	font = pygame.font.Font(None, fontSize)
	text = font.render(string, 1, color)
	textpos = text.get_rect(center=pos)
	globalvars.screen.blit(text, textpos)
	return textpos


class TemporaryText():
	'''Specify the position of the text, contents, whether or not the
	text should flash and how fast it should do so in seconds, and the 
	time for the text to live in seconds.
	Font size and color can also be specified'''
        def __init__(self, x=0, y=0, text=None, timeOn=0, timeOff=0, ttl=0, fontSize=12, color=white):
		font = pygame.font.Font(None, fontSize)
		self.texts = []
		self.positions = []
		maxWidth=0
		maxHeight=0
		leftmost = globalvars.WIDTH
		topmost = globalvars.HEIGHT
		for t in text:
			self.texts.append(font.render(t, 1, color))
			textpos = self.texts[-1].get_rect(center=(x, y+maxHeight))
			self.positions.append(textpos)
			maxWidth = max(textpos.width, maxWidth)
			maxHeight += fontSize
			leftmost = min(textpos.left, leftmost)
			topmost = min(textpos.top, topmost)
		self.rect = pygame.Rect(leftmost, topmost, maxWidth, maxHeight)
		self.timeOn = timeOn * globalvars.FPS
		self.timeOff = timeOff * globalvars.FPS
		self.ttl = ttl * globalvars.FPS
		#Whether to offset this object's location based on the camera.
		#Text does not useOffset because we want to only position it relative to 0,0
		self.useOffset = False
		#Attributes for flashing:
		self.showing = True
		self.countdown = self.timeOn

	def update(self):
		'''Return true to be removed from intangibles. Return False otherwise.'''
		if self.countdown <= 0:
			#Reset countdown and invert showing
			if self.showing:
				self.countdown = self.timeOff
			else:
				self.countdown = self.timeOn
			self.showing = not self.showing
		if self.showing and self.timeOff > 0:
				self.countdown -= 1
		else:
			self.countdown -= 1
		self.ttl -= 1
		return self.ttl <= 0

	def draw(self, _):
		for i in range(len(self.texts)):
			globalvars.screen.blit(self.texts[i], self.positions[i])
		
	def isOnScreen(self, _):
		return self.showing

	def kill(self): pass


