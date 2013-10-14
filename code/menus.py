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
border_padding = 50
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

	#Add tabs to the menu:
	addAllTabs(menu)

	return menu


def addAllTabs(menu):
	'''Takes a menu and adds a standard set of tabs along the top of the menu.'''
	width = 100
	localheight = 20
	textbuffer = 9
	framethickness = 2
	x_val = left
	#ship
	subpanel = Panel()
	temp = drawable.Rectangle(x1=x_val, y1=(top), width=width, height=localheight, \
		color=colors.yellow, thickness=framethickness)
	subpanel.addDrawable(temp)
	temp = drawable.Text(x1=(x_val+textbuffer), y1=(top+textbuffer), \
		string='Ship', font_size=24, color=colors.white)
	subpanel.addDrawable(temp)
	subpanel.setMethod(setShipPanel)
	menu.addPanel(subpanel)
	x_val += width

	#galaxy info
	subpanel = Panel()
	temp = drawable.Rectangle(x1=x_val, y1=(top), width=width, height=localheight, \
		color=colors.yellow, thickness=framethickness)
	subpanel.addDrawable(temp)
	temp = drawable.Text(x1=(x_val+textbuffer), y1=(top+textbuffer), \
		string='Galaxy', font_size=24, color=colors.white)
	subpanel.addDrawable(temp)
	subpanel.setMethod(setGalaxyPanel)
	subpanel.argument = False
	menu.addPanel(subpanel)
	x_val += width

	#local info
	subpanel = Panel()
	temp = drawable.Rectangle(x1=x_val, y1=(top), width=width, height=localheight, \
		color=colors.yellow, thickness=framethickness)
	subpanel.addDrawable(temp)
	temp = drawable.Text(x1=(x_val+textbuffer), y1=(top+textbuffer), \
		string='Local Info', font_size=24, color=colors.white)
	subpanel.addDrawable(temp)
	subpanel.setMethod(setLocalGalaxyPanel)
	subpanel.argument = False
	menu.addPanel(subpanel)
	x_val += width

	#local travel
	subpanel = Panel()
	temp = drawable.Rectangle(x1=x_val, y1=(top), width=width, height=localheight, \
		color=colors.yellow, thickness=framethickness)
	subpanel.addDrawable(temp)
	temp = drawable.Text(x1=(x_val+textbuffer), y1=(top+textbuffer), \
		string='Travel', font_size=24, color=colors.white)
	subpanel.addDrawable(temp)
	subpanel.setMethod(setLocalGalaxyPanel)
	subpanel.argument = True
	menu.addPanel(subpanel)
	x_val += width

	#test scenarios
	subpanel = Panel()
	temp = drawable.Rectangle(x1=x_val, y1=(top), width=width, height=localheight, \
		color=colors.yellow, thickness=framethickness)
	subpanel.addDrawable(temp)
	temp = drawable.Text(x1=(x_val+textbuffer), y1=(top+textbuffer), \
		string='Test', font_size=24, color=colors.white)
	subpanel.addDrawable(temp)
	subpanel.setMethod(setTestingPanel)
	menu.addPanel(subpanel)
	x_val += width


def setTestingPanel():
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

	globalvars.panel = menu


def setGalaxyPanel(travel):
	globalvars.panel = getGalaxyPanel(travel)


def getGalaxyPanel(travel):
	'''Pre: galaxy is a NodeManager object that has been initialized.'''
	menu = getStandardMenu()
	radius = 3
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
		#If travel is set and the node is already connected to the player's node
		if travel and n.alreadyConnected(globalvars.player.nodeid):
			subpanel.setMethod(scenarios.setDestinationNode)
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


def setLocalGalaxyPanel(travel):
	'''Pre: galaxy is a NodeManager object that has been initialized.'''
	menu = getStandardMenu()
	radius = 10
	#Magnitude of the stretch.
	magnitude = 4
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
			#If travel is set and the node is already connected to the player's node
			if travel and n.alreadyConnected(globalvars.player.nodeid):
				subpanel.setMethod(scenarios.setDestinationNode)
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
	globalvars.panel = menu


def setNodeViewPanel(nodeid):
	node = globalvars.galaxy.getNode(nodeid)
	topbuffer = 100
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
			y1=font_size*i+topbuffer+top, string=text[i],\
			font_size=font_size, color=colors.white)
		menu.addDrawable(temp)

	globalvars.panel = menu


def setRestartPanel():
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

	globalvars.panel = menu


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


def unequipPlayerWeapon():
	'''This method allows me to keep the unequipWeapon method in the ship object 
	unpolluted by menu concerns, but to also reset the menu to reflect changes the 
	player makes to his ship.'''
	globalvars.player.unequipWeapon()
	setShipPanel()


def equipPlayerWeapon(cargo_index):
	'''This method allows me to keep the equipWeaponFromCargo method in the ship object 
	unpolluted by menu concerns, but to also reset the menu to reflect changes the 
	player makes to his ship.'''
	globalvars.player.equipWeaponFromCargo(cargo_index)
	setShipPanel()


def setShipPanel():
	menu = getStandardMenu()
	#TODO
	temp = drawable.DrawableImage(x1=left+20, y1=100+top, image='shipoutline')
	menu.addDrawable(temp)

	textbuffer = 8
	localtopbuffer = 50
	leftoffset = 500
	localheight = 70
	localwidth = 200
	font_size = 24
	framethickness = 2
	#Draw the currently equipped weapon if any
	if len(globalvars.player.weapons) > 0:
		x_val = 200
		y_val = 80
		subpanel = Panel()
		#Add frame around weapon
		temp = drawable.Rectangle(x1=(left+x_val),\
					y1=(top+y_val),\
					width=localwidth,\
					height=localheight,\
					color=colors.yellow,\
					thickness=framethickness)
		subpanel.addDrawable(temp)
		#Add weapon name
		temp = drawable.Text(x1=(left+x_val+textbuffer),\
				y1=(top+y_val+textbuffer),\
				string=globalvars.player.weapons[0].name, font_size=font_size,\
				color=colors.white)
		subpanel.addDrawable(temp)
		menu.addPanel(subpanel)
		#Add option to unequip weapon
		subpanel = Panel()
		temp = drawable.Text(x1=(left+x_val+textbuffer),\
				y1=(top+y_val+font_size+textbuffer),\
				string='Unequip', font_size=font_size,\
				color=colors.white)
		subpanel.setMethod(unequipPlayerWeapon)
		subpanel.addDrawable(temp)
		menu.addPanel(subpanel)
		#Add option to view information on weapon
		subpanel = Panel()
		temp = drawable.Text(x1=(left+x_val+textbuffer),\
				y1=(top+y_val+font_size*2+textbuffer),\
				string='View stats', font_size=font_size,\
				color=colors.white)
		subpanel.setMethod(setWeaponViewPanel)
		subpanel.argument = globalvars.player.weapons[0]
		subpanel.addDrawable(temp)
		menu.addPanel(subpanel)


	#Draw all the weapons in the cargo hold along the right side of the screen.
	i = 0
	for j in xrange(len(globalvars.player.cargo)):
		c = globalvars.player.cargo[j]
		#This is a clunky way to distinguish weapons from non-weapons, but it will work for now.
		if hasattr(c, 'shooter'):
			subpanel = Panel()
			#Add frame around weapon
			temp = drawable.Rectangle(x1=(left+leftoffset),\
						y1=(localtopbuffer+top+i*localheight),\
						width=localwidth,\
						height=localheight, \
						color=colors.yellow,\
						thickness=framethickness)
			subpanel.addDrawable(temp)
			#Add weapon name
			temp = drawable.Text(x1=(left+leftoffset+textbuffer),\
					y1=(localtopbuffer+top+i*localheight+textbuffer),\
					string=c.name, font_size=font_size, \
					color=colors.white)
			subpanel.addDrawable(temp)
			menu.addPanel(subpanel)
			#Add option to equip weapon
			subpanel = Panel()
			temp = drawable.Text(x1=(left+leftoffset+textbuffer),\
					y1=(localtopbuffer+top+i*localheight+textbuffer+font_size),\
					string='Equip', font_size=font_size, \
					color=colors.white)
			subpanel.setMethod(equipPlayerWeapon)
			subpanel.argument = j
			subpanel.addDrawable(temp)
			menu.addPanel(subpanel)
			#Add option to view information on weapon
			subpanel = Panel()
			temp = drawable.Text(x1=(left+leftoffset+textbuffer),\
					y1=(localtopbuffer+top+i*localheight+textbuffer+font_size*2),\
					string='View stats', font_size=font_size, \
					color=colors.white)
			subpanel.setMethod(setWeaponViewPanel)
			subpanel.argument = c
			subpanel.addDrawable(temp)
			menu.addPanel(subpanel)
			i += 1

	globalvars.panel = menu



def setWeaponViewPanel(weapon):
	topbuffer = 100
	menu = getStandardMenu()
	#Then draw the contents of the menu
	font_size = 24
	text = weapon.toStringArray()
	for i in range(len(text)):
		temp = drawable.Text(x1=left+50,\
			y1=font_size*i+topbuffer+top, string=text[i],\
			font_size=font_size, color=colors.white)
		menu.addDrawable(temp)
	globalvars.panel = menu

