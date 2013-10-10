import drawable
import pygame
import colors
import scenarios
import globalvars
from geometry import angleFromPosition, translate, distance

class Panel:
	"""The basic building block of the menu system. """
	def __init__(self):
		self.panels = []
		self.drawables = []
		self.method = None #Invoke this when the panel is clicked on.
		self.alt_color = colors.green #Use this alternate color upon mouseover
		self.use_alt = False
		self.argument = None #This is useful if the method of the panel takes an argument.

	def addDrawable(self, drawable):
		self.drawables.append(drawable)

	def addPanel(self, panel):
		self.panels.append(panel)

	def highlight(self):
		'''This function is called in response to mouse over events.'''
		self.use_alt = True

	def anySelected(self, pos):
		for d in self.drawables:
			if d.rect.collidepoint(pos):
				return True
		return False

	def setMethod(self, method):
		self.method = method

	def handleEvent(self, event):
		if not self.method is None:
			self.use_alt = False
			if event.type == pygame.MOUSEBUTTONDOWN:
				#Not all event types have positions so we check this inside the other guard.
				if self.anySelected(event.pos):
					if self.argument is None:
						self.method()
					else:
						self.method(self.argument)
			elif event.type == pygame.MOUSEMOTION:
				#Not all event types have positions so we check this inside the other guard.
				if self.anySelected(event.pos):
					self.highlight()
		#Pass event down to sub panels
		for panel in self.panels:
			panel.handleEvent(event)

	def draw(self):
		"""draws this panel on the surface."""
		for d in self.drawables:
			if self.use_alt:
				d.draw(use_color=self.alt_color)
			else:
				d.draw()
		for panel in self.panels:
			panel.draw()


#There was a lot of duplicate code so I moved some of it out.
border_padding = 100
padding = 25
top = border_padding
left = border_padding
height = globalvars.HEIGHT-2*border_padding
width = globalvars.WIDTH-2*border_padding
def getStandardMenu():
	'''There was a lot of code duplication so I stuck it in a method all its own.'''
	menu = Panel()

	#First draw a white frame around the menu.
	temp = drawable.Rectangle(x1=left, y1=top, width=width, height=height, \
		color=colors.white, thickness=3)
	menu.addDrawable(temp)

	#Then draw the background for the menu
	temp = drawable.Rectangle(x1=left, y1=top, width=width, height=height, \
		color=colors.reddishgray)
	menu.addDrawable(temp)

	return menu


def getTestingPanel():
	menu = getStandardMenu()

	#Then draw the contents of the menu
	horiz_space = 200
	vert_space = 70
	x1, y1 = horiz_space, globalvars.HEIGHT/2
	radius = 10
	#panel made of a circle centered at start
	subpanel = Panel()
	subpanel.setMethod(scenarios.testScenario00)
	temp = drawable.Circle(x1=x1, y1=y1, radius=radius, color=colors.yellow)
	subpanel.addDrawable(temp)
	menu.addPanel(subpanel)

	texts = ['Asteroids', 'Gem Wild', 'Race', 'Furball', 'Infinite space', 'Capital ship']
	methods = [scenarios.asteroids, scenarios.gemWild, scenarios.race, scenarios.furball, scenarios.infiniteSpace, scenarios.capitalShipScenario]

	x2 = horiz_space*2
	methodLength = len(methods)
	for i in range(methodLength):
		j = i-methodLength/2
		y2 = globalvars.HEIGHT/2+vert_space*j

		subpanel = Panel()
		#http://www.secnetix.de/olli/Python/lambda_functions.hawk
		subpanel.setMethod(methods[i])
		temp = drawable.Circle(x1=x2, y1=y2, radius=radius, color=colors.yellow)
		subpanel.addDrawable(temp)
		temp = drawable.Text(x1=(x2+2*radius), y1=y2, string=texts[i],\
			font_size=24, color=colors.white)
		subpanel.addDrawable(temp)
		menu.addPanel(subpanel)

		temp = drawable.Line(x1=x1, y1=y1, x2=x2, y2=y2)
		menu.addDrawable(temp)

	#Add a "tab" up at the top that switches to weapon selection
	subpanel = Panel()
	temp = drawable.Rectangle(x1=(left+30), y1=(top+5), width=100, height=20, \
		color=colors.yellow, thickness=2)
	subpanel.addDrawable(temp)
	#Add text
	temp = drawable.Text(x1=(left+30+5), y1=(top+5+5), string='Weapons', font_size=24, color=colors.white)
	subpanel.addDrawable(temp)
	#This will be the panel that allows the user to change weapons.
	subpanel.setMethod(setWeaponsPanel)
	menu.addPanel(subpanel)

	return menu


def setGalaxyPanel(travel):
	globalvars.panel = getGalaxyPanel(travel)


def getGalaxyPanel(travel):
	'''Pre: galaxy is a NodeManager object that has been initialized.'''
	menu = getStandardMenu()
	radius = 3

	font_size = 36
	if travel:
		temp = drawable.Text(x1=left+100, y1=top+font_size/2,\
			string='Click on a node to set it as the destination.',\
			font_size=font_size, color=colors.white)
	else:
		temp = drawable.Text(x1=left+100, y1=top+font_size/2,\
			string='Click on a node to learn more about it.',\
			font_size=font_size, color=colors.white)
	menu.addDrawable(temp)

	for n in globalvars.galaxy.nodes:
		subpanel = Panel()
		color = colors.yellow
		#Color the player's location red.
		if n.id == globalvars.player.nodeid:
			color = colors.red
		temp = drawable.Circle(x1=n.x, y1=n.y, radius=radius, color=color)
		subpanel.addDrawable(temp)
		#If this node is connected to the player's current node, make it clickable
		isconnected = False
		subpanel.argument = n.id
		#If travel is set, then view options that can be traveled to
		if travel:
			for c in n.connections:
				if globalvars.player.nodeid == c[0]:
					subpanel.setMethod(scenarios.setDestinationNode)
					break
		else:
			#Otherwise view options for information only
			subpanel.setMethod(setNodeViewPanel)
		#If this node is the player's current location then make this reset
		#the player's scenario. This is really only for testing since the player
		#can get away using the testing menu by pressing the m key.
		if n.id == globalvars.player.nodeid and travel:
			subpanel.setMethod(scenarios.goToInfiniteSpace)
		menu.addPanel(subpanel)

	for c in globalvars.galaxy.connections:
		temp = drawable.Line(x1=c[0], y1=c[1], x2=c[2], y2=c[3])
		menu.addDrawable(temp)

	return menu


def getLocalGalaxyPanel(travel):
	'''Pre: galaxy is a NodeManager object that has been initialized.'''
	menu = getStandardMenu()
	radius = 10
	#Magnitude of the stretch.
	magnitude = 4

	font_size = 36
	if travel:
		temp = drawable.Text(x1=left+100, y1=top+font_size/2,\
			string='Click on a node to set it as the destination.',\
			font_size=font_size, color=colors.white)
	else:
		temp = drawable.Text(x1=left+100, y1=top+font_size/2,\
			string='Click on a node to learn more about it.',\
			font_size=font_size, color=colors.white)
	menu.addDrawable(temp)
	#Center the player node location
	playerNodeLoc = (globalvars.CENTERX, globalvars.CENTERY)
	#Get the player's node
	playerNode = globalvars.galaxy.getNode(globalvars.player.nodeid)
	#Draw player node in the center of the menu.
	subpanel = Panel()
	subpanel.argument = globalvars.player.nodeid
	#If this node is the player's current location then make this reset
	#the player's scenario. This is really only for testing since the player
	#can get away using the testing menu by pressing the m key.
	if travel:
		subpanel.setMethod(scenarios.goToInfiniteSpace)
	else:
		subpanel.setMethod(setNodeViewPanel)
	temp = drawable.Circle(x1=playerNodeLoc[0]-radius, y1=playerNodeLoc[1]-radius,
				radius=radius, color=colors.red)
	subpanel.addDrawable(temp)
	menu.addPanel(subpanel)

	#Draw all the on-screen nodes and the connections between them
	for n in globalvars.galaxy.nodes:
		angle = angleFromPosition(playerNode.loc, n.loc)
		dist = distance(playerNode.loc, n.loc)
		position = translate(playerNodeLoc, angle, dist*magnitude)
		#If it is on screen...
		if position[0] > padding+border_padding and \
		position[0] < globalvars.WIDTH-padding-border_padding and \
		position[1] > padding+border_padding and \
		position[1] < globalvars.HEIGHT-padding-border_padding and \
		n.id != playerNode.id:
			#Draw it
			subpanel = Panel()
			subpanel.argument = n.id
			if travel:
				for c in n.connections:
					if globalvars.player.nodeid == c[0]:
						subpanel.setMethod(scenarios.setDestinationNode)
						break
			else:
				#Otherwise view options for information only
				subpanel.setMethod(setNodeViewPanel)
			temp = drawable.Circle(x1=position[0]-radius, y1=position[1]-radius,
						radius=radius, color=colors.yellow)
			subpanel.addDrawable(temp)
			menu.addPanel(subpanel)
			#draw connections
			for c in n.connections:
				angle = angleFromPosition(n.loc, c[1])
				dist = distance(n.loc, c[1])
				position2 = translate(position, angle, dist*magnitude)
				temp = drawable.Line(x1=position[0]-radius, y1=position[1]-radius,
					x2=position2[0]-radius, y2=position2[1]-radius)
				menu.addDrawable(temp)
	return menu


def setNodeViewPanel(nodeid):
	node = globalvars.galaxy.getNode(nodeid)

	menu = getStandardMenu()

	text = [
	'Id: '+str(node.id)+'.',
	'Description: '+node.description+'.',
	'Hostility: '+str(node.hostility)+'. Chance to generate opposing ships.',
	'Enemy strength: '+str(node.strength)+'. Strength of opposing ships (initially just capital ship chance).',
	'Debris: '+str(node.amt_debris)+'. Chance of asteroids.',
	'Wealth: '+str(node.amt_wealth)+'. Chance of gems, health, and rich asteroids.'
	]

	#Then draw the contents of the menu
	font_size = 24
	for i in range(len(text)):
		temp = drawable.Text(x1=left+50,\
			y1=font_size*i+20+top, string=text[i],\
			font_size=font_size, color=colors.white)
		menu.addDrawable(temp)

	#Put button to return to previous view.
	subpanel = Panel()
	temp = drawable.Text(x1=left+50, y1=font_size*len(text)+20+top,\
		string='Return to node info menu.', font_size=font_size, color=colors.yellow)
	subpanel.addDrawable(temp)
	subpanel.setMethod(setGalaxyPanel)
	subpanel.argument = False
	menu.addPanel(subpanel)

	globalvars.panel = menu


def getRestartPanel():
	menu = getStandardMenu()

	#Then draw the contents of the menu
	#Display text explaining that player died.
	temp = drawable.Text(x1=globalvars.WIDTH/2-100, y1=200, string='You have died',\
		font_size=24, color=colors.white)
	menu.addDrawable(temp)
	#Display button allowing player to restart.
	subpanel = Panel()
	subpanel.setMethod(scenarios.restart)
	temp = drawable.Rectangle(x1=globalvars.WIDTH/2-75, y1=300, width=200, height=50, \
		color=colors.blue)
	subpanel.addDrawable(temp)
	temp = drawable.Text(x1=globalvars.WIDTH/2, y1=340, string='Restart',\
		font_size=32, color=colors.white)
	subpanel.addDrawable(temp)
	menu.addPanel(subpanel)

	return menu


def getHelpPanel():
	menu = getStandardMenu()

	help = [
	'INSTRUCTIONS:', 
	'Press space bar to shoot.',
	'Press "/" or "?" to query game state. Currently this just prints the player\'s destination.',
	'Press escape to quit.',
	'Press "e" to create an enemy ship that will attack the player.',
	'Press up arrow to increase player speed by one quarter of max up to max.',
	'Press down arrow to decrease player speed by one quarter of max down to zero.',
	'Press left arrow to turn counter-clockwise 30 degrees.',
	'Press right arrow to turn clockwise 30 degrees.',
	'Click on the screen to tell the starship to move towards the clicked point.',
	'Press "m" open the scenarios menu.',
	'Press "l" to display the galaxy node info menu.',
	'Press "n" to display the galaxy node travel menu.',
	'Press anything to close the current menu.',
	'Press "p" to slow down and park at destination.',
	'Press "s" to pause/unpause the game.',
	'Press "q" to remove destination and simply fly in current direction.',
	'Press "t" for hit box test.',
	'Press "s" to pause and unpause.',
	'Press "y" profile a variety of methods.',
	'Press "u" profile game.run().',
	'Press "h" Display help info.',
	'Press "k" to display the galaxy node info menu.',
	'Press "o" to display the galaxy node travel menu.'
	]

	#Then draw the contents of the menu
	font_size = 24
	for i in range(len(help)):
		temp = drawable.Text(x1=left+50,\
			y1=font_size*i+20+top, string=help[i],\
			font_size=font_size, color=colors.white)
		menu.addDrawable(temp)

	return menu


weaponsList = ['mk0', 'mk1', 'mk2', 'spread_mk2', 'spread_mk3', 'missile_mk1', 'mine', 'hit_box_test']
def setWeaponsPanel():
	'''Creates the weapon panel and sets the current panel to be the weapon panel.'''
	menu = getStandardMenu()
	#Then draw the contents of the menu
	for i in xrange(len(weaponsList)):
		subpanel = Panel()
		temp = drawable.Text(x1=globalvars.WIDTH/2-100, y1=(40*i+150), \
			string=weaponsList[i], font_size=24, color=colors.white)
		subpanel.addDrawable(temp)
		#The following commented code does not work so I created an argument attribute for the panel object.
		#subpanel.setMethod(lambda: globalvars.player.setWeapon(weaponsList[i]))
		subpanel.setMethod(globalvars.player.setWeapon)
		subpanel.argument = weaponsList[i]
		menu.addPanel(subpanel)
	globalvars.panel = menu

