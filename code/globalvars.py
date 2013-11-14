DEBUG = True

FPS = 60 #frames per second

NUMBEROFNODES = 200

WIDTH = 900
HEIGHT = 700

CENTERX = WIDTH / 2
CENTERY = HEIGHT / 2
#Radius of a circle that just barely fits inside the screen:
SCREENRADIUS = min(WIDTH, HEIGHT)/2

MENU_BORDER_PADDING = 50
MENU_PADDING = 25

#Used by physicalObject to define what each physicalObject is.
BULLET = 0
OTHER = 1
SHIP = 2
FIXEDBODY = 3
HEALTH = 4
ASTEROID = 5
GEM = 6
DUST = 7
ARROW = 8

#The least distance to check for a collision. Might need adjusted if we start using really big objects.
MINSAFEDIST = 1024

BGCOLOR = (0,0,0) #Black. I would have imported colors but I want globalvars to import absolutely nothing so there are no loops in the graph of my imports.
BGIMAGE = None

#instantiate sprite groups
tangibles = None
intangibles_bottom = None #Display beneath all other things
intangibles_top = None #Display above all other things
#This last group will contain any sprites that will tickle whiskers. NPCs have whiskers for collision avoidance.
whiskerables = None

#set up the display:
screen = None
#Player must be created before scenario is called.
player = None

#The point in space just ahead of the player that all the enemies will aim for.
player_target_lead = (0.0,0.0)

#If arena is set to anything other than zero, then the player will be forced to stay inside the arena and all other objects will also be pointed roughly in the direction of the center of the arena. This is used for 
arena = 0

#Display menus and the like on the panel.
menu = None

#How many seconds to continue displaying while the player is dead before kicking him back to the restart menu.
deathcountdown = 3 * FPS

#Local system of nodes
galaxy = None

#List of all the factions and object to manage them:
factions = None

#Track score and time limit in minigames
score_keeper = None
