#! /usr/bin/env python
import pygame
import random as rd

#Set random seed
rd.seed(0)

class Mover(pygame.sprite.Sprite):
	def __init__(self, start, destination):
		pygame.sprite.Sprite.__init__(self)
		self.x, self.y = start
		self.destx, self.desty = destination
		self.vx = 0
		self.vy = 0
		self.finished = False
		self.message = pygame.image.load('envelope_small.jpeg')
		self.message = self.message.convert() 

	def move(self):
		""" Move the message. """
		#Determine direction
		#horizontal
		if self.x < self.destx:
			self.vx = 1
		elif self.x > self.destx:
			self.vx = -1
		else:
			self.vx = 0
		#vertical
		if self.y < self.desty:
			self.vy = 1
		elif self.y > self.desty:
			self.vy = -1
		else:
			self.vy = 0

		#move
		self.x += self.vx
		self.y += self.vy

		#display the new
		screen.blit(self.message, (self.x, self.y))

		#Check for reached destination
		if self.x == self.destx and self.y == self.desty:
			self.finished = True



envelope_width = 30
envelope_height = 20

screen_width = 900
screen_height = 700

screen = pygame.display.set_mode((screen_width, screen_height))
clock = pygame.time.Clock()

num_messages = 10

#Make a message list
messages = []
for _ in range(num_messages):
	start = rd.randint(0,screen_width), rd.randint(0,screen_height)
	end = rd.randint(0,screen_width), rd.randint(0,screen_height)
	messages.append(Mover(start, end))

#Background image
BGIMAGE = pygame.image.load('ioOverJupiter.bmp').convert()
screen.blit(BGIMAGE, (0,0))
pygame.display.flip()

dirty_rects = []

wait_time = 20
finished = False
