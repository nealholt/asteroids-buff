import pygame.sprite
import pygame.display
import objInstances
import colors
import random as rd
from geometry import getCoordsNearLoc, translate, angleFromPosition
import ship
import capitalShip
import displayUtilities
import globalvars
import math
import player
import hudHelpers
import sys
sys.path.append('code/cython')
import cygeometry


class ScenarioManager:
	"""I created this to reduce the number of files importing scenarios.py which was getting cumbersome and limiting usability because I had to avoid mutual imports. An object referenced by a global variable seems like a much better option even if it doesn't have much state. """
	def __init__(self):
		#The distances between nodes in the galaxy view is proportional to the distance between warp portals in the regular ship view. The scaling factor is warpPortalScaling.
		self.warpPortalScaling = 100


	def asteroids(self, seed=0):
		''' '''
		rd.seed(seed) #Fix the seed for the random number generator.
		wipeOldScenario(); resetDustOnTop()
		rocks = ['bigrock','medrock','smallrock','gold','silver']
		#Reset the player's location to 0,0 and his speed to zero
		globalvars.player.loc = (0.0, 0.0)
		globalvars.player.speed = 0.0
		globalvars.player.targetSpeed = 0.0
		#Define an arena 2000 pixels across for the player and all the asteroids
		#to bounce around inside
		globalvars.arena = 1000 #1000 pixel radius centered at zero, zero.
		#Make the background color blue so that we can draw a black circle 
		#to show where the arena is located.
		globalvars.BGCOLOR = colors.blue
		#Draw a black circle and put it in intangibles to show the limits 
		#of the arena
		temp = objInstances.FixedCircle(x=0, y=0, radius=globalvars.arena, color=colors.black)
		globalvars.intangibles_bottom.add(temp)
		#Make 10 rocks centered around, but not on the player
		for _ in range(10):
			#Select a rock type
			rock = rocks[rd.randint(0, len(rocks)-1)]
			#Get the coordinates of the rock
			mindist = 200
			maxdist = 800
			x,y = getCoordsNearLoc(globalvars.player.rect.center, mindist, maxdist, maxdist)
			#Make the rock
			temp = objInstances.Asteroid(x=x, y=y, image_name=rock)
			globalvars.tangibles.add(temp); globalvars.whiskerables.add(temp)

		time_limit = 30 #time limit in seconds
		text = ['ASTEROIDS COMPLETED']
		#Display timer and score count with the following:
		globalvars.score_keeper = displayUtilities.TimeLimitDisplay(text, \
			points_to_win=50, time_limit=time_limit)
		globalvars.intangibles_top.add(globalvars.score_keeper)

		announcement = displayUtilities.TemporaryText(x=globalvars.CENTERX, y=globalvars.CENTERY,
			text='Watch out for asteroids while you',
			timeOff=0, timeOn=1, ttl=3.5, fontSize=52)
		globalvars.intangibles_top.add(announcement)
		announcement = displayUtilities.TemporaryText(x=globalvars.CENTERX, y=globalvars.CENTERY+52,
			text='blow them up to collect gems.',
			timeOff=0, timeOn=1, ttl=3.5, fontSize=52)
		globalvars.intangibles_top.add(announcement)

		#Draw the new background and flip the whole screen.
		globalvars.screen.fill(globalvars.BGCOLOR)
		pygame.display.flip()



	def gemWild(self, seed=0):
		rd.seed(seed) #Fix the seed for the random number generator.

		wipeOldScenario(); resetDustOnTop();
		#Reset the player's location to 0,0 and his speed to zero
		globalvars.player.loc = (0.0, 0.0)
		globalvars.player.speed = 0.0
		globalvars.player.targetSpeed = 0.0
		#Define an arena 2000 pixels across for the player and all the asteroids
		#to bounce around inside
		globalvars.arena = 1000 #1000 pixel radius centered at zero, zero.
		#Make the background color blue so that we can draw a black circle 
		#to show where the arena is located.
		globalvars.BGCOLOR = colors.blue
		#Draw a black circle and put it in intangibles to show the limits 
		#of the arena
		temp = objInstances.FixedCircle(x=0, y=0, radius=globalvars.arena, color=colors.black)
		globalvars.intangibles_bottom.add(temp)

		#Make 50 crystals centered around, but not on the player
		for _ in range(50):
			mindist = 200
			maxdist = 800
			x,y = getCoordsNearLoc(globalvars.player.rect.center, mindist, maxdist, maxdist)
			temp = objInstances.Gem(x=x, y=y)
			globalvars.tangibles.add(temp); globalvars.whiskerables.add(temp)

		time_limit = 30 #time limit in seconds
		text = ['GEM WILD COMPLETED']
		#Display timer and score count with the following:
		globalvars.score_keeper = displayUtilities.TimeLimitDisplay(text, \
			points_to_win=150, time_limit=time_limit)
		globalvars.intangibles_top.add(globalvars.score_keeper)

		announcement = displayUtilities.TemporaryText(x=globalvars.CENTERX, y=globalvars.CENTERY, 
			text='Collect as many gems as you can in '+str(time_limit)+' seconds.',
			timeOff=0, timeOn=1, ttl=3.5, fontSize=52)
		globalvars.intangibles_top.add(announcement)

		#Draw the new background and flip the whole screen.
		globalvars.screen.fill(globalvars.BGCOLOR)
		pygame.display.flip()



	def race(self, seed=0):
		rd.seed(seed) #Fix the seed for the random number generator.

		'''Race (infinite space) - player is given a destination and the clock 
		starts ticking. Space is populated pseudo randomly (deterministically) 
		with obstacles, enemies, gems.'''
		wipeOldScenario(); resetDust()
		#Reset the player's location to 0,0 and his speed to zero
		globalvars.player.loc = (0.0, 0.0)
		globalvars.player.speed = 0.0
		globalvars.player.targetSpeed = 0.0
		finish_line = (6000, 0)

		#Display arrow to finish line
		globalvars.intangibles_top.add(displayUtilities.ArrowToDestination(finish_line))
		#Display finish bullseye
		globalvars.intangibles_top.add(objInstances.FinishBullsEye(finish_line))

		#determine what sorts of obstacles to put on the race course.
		numbers = [0 for _ in range(hudHelpers.fuel+1)]
		numbers[hudHelpers.enemy] = 3
		numbers[hudHelpers.crystal] = 5
		numbers[hudHelpers.large_asteroid] = 20
		numbers[hudHelpers.medium_asteroid] = 30
		numbers[hudHelpers.small_asteroid] = 40
		numbers[hudHelpers.gold_metal] = 5
		numbers[hudHelpers.silver_metal] = 6
		numbers[hudHelpers.health] = 7
		numbers[hudHelpers.capital_ship] = 0
		numbers[hudHelpers.fuel] = 0

		#Populate space in a semi narrow corridor between the player and the finish line
		course_length = 6000 #pixels
		course_height = 1000 #pixels
		#Midway between player and destination
		midway = (course_length/2, 0)

		hudHelpers.populateSpace(objects=numbers, width=course_length, \
			height=course_height, center=midway, seed=rd.random())

		time_limit = 30 #time limit in seconds
		text = ['RACE COMPLETED']
		#Display timer and score count with the following:
		globalvars.score_keeper = displayUtilities.TimeLimitDisplay(text, \
			points_to_win=1000000, time_limit=time_limit)
		globalvars.intangibles_top.add(globalvars.score_keeper)

		announcement = displayUtilities.TemporaryText(x=globalvars.CENTERX, y=globalvars.CENTERY, 
			text='Welcome to the race!',
			timeOff=0.3, timeOn=0.5, ttl=3, fontSize=52)
		globalvars.intangibles_top.add(announcement)
		announcement = displayUtilities.TemporaryText(x=globalvars.CENTERX, y=globalvars.CENTERY+52, 
			text='Follow the yellow arrow',
			timeOff=0.3, timeOn=0.5, ttl=3, fontSize=52)
		globalvars.intangibles_top.add(announcement)
		announcement = displayUtilities.TemporaryText(x=globalvars.CENTERX, y=globalvars.CENTERY+52*2,
			text='to the finish as fast as possible.',
			timeOff=0.3, timeOn=0.5, ttl=3, fontSize=52)
		globalvars.intangibles_top.add(announcement)

		#Draw the new background and flip the whole screen.
		globalvars.screen.fill(globalvars.BGCOLOR)
		pygame.display.flip()


	def furball(self, seed=0):
		rd.seed(seed) #Fix the seed for the random number generator.
		wipeOldScenario(); resetDust()
		globalvars.BGIMAGE = displayUtilities.image_list['bggalaxies'].convert()
		#Make a few enemies near the player
		mindist = 200
		maxdist = 800
		#Make 3 enemy units:
		x,y = getCoordsNearLoc(globalvars.player.rect.center, mindist, maxdist, maxdist)
		makeNewEnemy(x=x, y=y)
		x,y = getCoordsNearLoc(globalvars.player.rect.center, mindist, maxdist, maxdist)
		makeNewEnemy(x=x, y=y)
		x,y = getCoordsNearLoc(globalvars.player.rect.center, mindist, maxdist, maxdist)
		makeNewEnemy(x=x, y=y)
		#Make the score keeper:
		time_limit = 30 #time limit in seconds
		text = ['FURBALL COMPLETED']
		#Display timer and score count with the following:
		globalvars.score_keeper = displayUtilities.TimeLimitDisplay(text, \
			points_to_win=3, time_limit=time_limit)
		globalvars.intangibles_top.add(globalvars.score_keeper)
		#Announce the start of the furball.
		announcement = displayUtilities.TemporaryText(x=globalvars.CENTERX, y=globalvars.CENTERY, 
			text='Fight off 3 enemy ships!',
			timeOff=0, timeOn=1, ttl=3.5, fontSize=52)
		globalvars.intangibles_top.add(announcement)

		#Draw the new background and flip the whole screen.
		globalvars.screen.blit(globalvars.BGIMAGE, (0,0))
		pygame.display.flip()


	def capitalShipScenario(self, seed=0):
		rd.seed(seed) #Fix the seed for the random number generator.
		wipeOldScenario(); resetDust()
		globalvars.BGIMAGE = displayUtilities.image_list['bggalaxies'].convert()
		#Make the capital ship
		enemy_ship = capitalShip.CapitalShip(centerx=0, centery=400, image_name='bigShip')
		globalvars.tangibles.add(enemy_ship)
		globalvars.whiskerables.add(enemy_ship)
		#Create the score keeper.
		time_limit = 30 #time limit in seconds
		text = ['CAPITAL SHIP BATTLE COMPLETED']
		#Display timer and score count with the following:
		globalvars.score_keeper = displayUtilities.TimeLimitDisplay(text, \
			points_to_win=100, time_limit=time_limit)
		globalvars.intangibles_top.add(globalvars.score_keeper)
		#Announce the goal of this minigame.
		announcement = displayUtilities.TemporaryText(x=globalvars.CENTERX, y=globalvars.CENTERY, 
			text='Blow up the capital ship!',
			timeOff=0, timeOn=1, ttl=3.5, fontSize=52)
		globalvars.intangibles_top.add(announcement)
		#Draw the new background and flip the whole screen.
		globalvars.screen.blit(globalvars.BGIMAGE, (0,0))
		pygame.display.flip()


	def goToInfiniteSpace(self, nodeid, update=True):
		'''This is a helper method that enables the menu system to function more easily.
		nodeid of the infinite space and the seed to use to generate the space.'''
		opportunity = None #See factions.update for what opportunity is all about
		if update:
			#Update all the factions
			opportunity = globalvars.factions.update(nodeid)
		#Get the node that has the id that this portal will lead to
		n = globalvars.galaxy.getNode(nodeid)
		self.infiniteSpace(seed=nodeid, playerloc=n.loc, warps=n.connections)
		#Check for an opportunity. This is when a player is moving to a node that is
		#the target of an action from a faction.
		if not opportunity is None:
			globalvars.menu.setOpportunityPanel(opportunity)
		#If the player has moved to a node in his path, then pop it.
		if len(globalvars.player.destinationNode) > 0 and globalvars.player.destinationNode[0] == nodeid:
			globalvars.player.destinationNode.pop(0)
		#Reset the arrow to the destination
		self.resetArrow()
		#If this node is faction-owned, then give the player options of minigame missions
		if n.owner != -1:
			globalvars.menu.setFactionMissionPanel(n)


	def infiniteSpace(self, seed=0, playerloc=(0.0,0.0), warps=None):
		rd.seed(seed) #Fix the seed for the random number generator.
		wipeOldScenario(); resetDust()	
		#Reset the player's location to 0,0 and his speed to zero
		globalvars.player.loc = playerloc
		globalvars.player.speed = 0.0
		globalvars.player.targetSpeed = 0.0
		globalvars.player.nodeid = seed #Player's new node id is set to be the seed argument.
		#Place warp portals
		allWarps = []
		if not warps is None:
			for w in warps:
				#Get the slope of the line from playerLoc to this warp
				angle = angleFromPosition(playerloc, w[1])
				scaledDistance = cygeometry.distance(playerloc, w[1]) * self.warpPortalScaling
				#print scaledDistance #TESTING
				x,y = translate(playerloc, angle, scaledDistance)
				temp = objInstances.WarpPortal(x=x, y=y, destinationNode=w[0],
							method=self.goToInfiniteSpace)
				globalvars.tangibles.add(temp)
				allWarps.append(temp)

		#Need a new hud helper that will generate the landscape and clean up distant objects on the fly.
		globalvars.intangibles_bottom.add(hudHelpers.InfiniteSpaceGenerator(seed=seed, warps=allWarps))
		#Display player location and speed info with the following:
		globalvars.intangibles_top.add(displayUtilities.ShipStatsText())

		announcement = displayUtilities.TemporaryText(x=globalvars.CENTERX, y=globalvars.CENTERY, 
			text='You\'ve arrived in system '+str(seed),
			timeOff=0, timeOn=1, ttl=3.5, fontSize=52)
		globalvars.intangibles_top.add(announcement)

		#Draw the new background and flip the whole screen.
		globalvars.screen.fill(globalvars.BGCOLOR)
		pygame.display.flip()


	def setDestinationNode(self, nodeid):
		'''Chart a shortest path using breadth first search to the node with the given id.
		Set the player's destination to be the path.
		Get the very first node in the path and point an arrow to it to lead 
		the player in the right direction.'''
		#End conditions
		failure = False #But this can be true if we run out of destinations to append.
				#There are disconnects in the graph.
		success = False #This is set true when we find the destination
		#Append as tuples all nodes reachable from player's current node along with the distance to them.
		visited_node_ids = [globalvars.player.nodeid]
		old_bfs_array = []
		new_bfs_array = []
		current_node = globalvars.galaxy.getNode(globalvars.player.nodeid)
		for connectid,location in current_node.connections:
			#If connectid is the destination then we can shortcircuit here
			if connectid == nodeid:
				globalvars.player.destinationNode = [nodeid]
				new_bfs_array = []
				success = True
				break
			if not connectid in visited_node_ids:
				#Calculate the distance (aka cost)
				cost = cygeometry.distance(current_node.loc, location)
				visited_node_ids.append(connectid)
				#Append a tuple where the first element is a path in the form of 
				#an array of node ids and the second element is the cost of the path.
				new_bfs_array.append(([connectid], cost))
		while not success and not failure:
			#Sort by shortest path when updating the arrays
			old_bfs_array = sorted(new_bfs_array, key=lambda pair: pair[1])
			new_bfs_array = []
			#We may exhaust all the connections if the destination is not 
			#connected to the player's location.
			if len(old_bfs_array) == 0:
				failure = True
				continue
			#Then for each node by id in the current list
			for path, cost in old_bfs_array:
				if success == True: break
				#Get the last node in the path
				current_node = globalvars.galaxy.getNode(path[-1])
				#For each of the node's neighbors
				for connectid,location in current_node.connections:
					#If connectid is the destination then we can shortcircuit here
					if connectid == nodeid:
						path.append(nodeid)
						globalvars.player.destinationNode = path
						success = True
						break
					#skip if the neighbor has already been considered
					#otherwise add node+neighbor + the sum of the distances to a new list
					elif not connectid in visited_node_ids:
						#Calculate the distance (aka cost)
						extra_cost = cygeometry.distance(current_node.loc, location)
						visited_node_ids.append(connectid)
						#Append a tuple where the first element is a path in the form of 
						#an array of node ids and the second element is the cost of 
						#the path.
						new_bfs_array.append((path+[connectid], cost+extra_cost))
		#If we failed to find a path, return false
		if failure: return False
		#Otherwise, make a new arrow point to the first warp point on the path and remove any old arrows.
		self.resetArrow()
		return True #Indicate that the destination was successfully set.


	def resetArrow(self):
		if len(globalvars.player.destinationNode) == 0:
			#Search through intangibles_top and remove any existing arrows
			for i in globalvars.intangibles_top:
				if i.is_a == globalvars.ARROW:
					globalvars.intangibles_top.remove(i)
			return True

		#Get the first node on the path:
		next_node_id = globalvars.player.destinationNode[0]

		#Find the infinite space generator
		destNodeLoc = None
		foundObjWithWarps = False
		for i in globalvars.intangibles_bottom:
			if hasattr(i, 'warps'):
				foundObjWithWarps = True
				#Get the location of the destination node
				for w in i.warps:
					if w.destinationNode == next_node_id:
						destNodeLoc = w.rect.center
						break
				break
		#Error check
		if destNodeLoc is None:
			if foundObjWithWarps:
				print 'ERROR: The infiniteSpaceGenerator object was found in intangibles_bottom, but it has no warp with an id matching nodeid '+str(next_node_id)+'. Exiting.'; exit()
			else:
				print 'Warning: cannot set destination node from here. No infiniteSpaceGenerator object was found in intangibles_bottom.'
		else:
			#Search through intangibles_top and remove any existing arrows
			for i in globalvars.intangibles_top:
				if i.is_a == globalvars.ARROW:
					globalvars.intangibles_top.remove(i)
			#Create a new arrow pointing to the destination node and add it to intangibles_top
			globalvars.intangibles_top.add(displayUtilities.ArrowToDestination(destNodeLoc))


	def restart(self):
		'''Give the player a new ship and boot him to the testing scenario. '''
		globalvars.player = player.Player('ship')
		globalvars.menu.main_panel = None

		#Order matters. This has to go after making the new player.
		self.goToInfiniteSpace(0)

		#reset the death display countdown
		globalvars.deathcountdown = 15





def wipeOldScenario():
	globalvars.tangibles.empty()
	globalvars.intangibles_bottom.empty()
	globalvars.intangibles_top.empty()
	globalvars.whiskerables.empty()
	globalvars.BGCOLOR = colors.black
	globalvars.BGIMAGE = None
	globalvars.score_keeper = None
	#Add the player back in.
	#Set the player's health bar. This must be done right before adding any ship to tangibles
	globalvars.player.setHealthBar()
	globalvars.tangibles.add(globalvars.player)
	#Immediately clear the panel
	globalvars.menu.main_panel = None
	#Reset the arena
	globalvars.arena = 0


def makeNewEnemy(x=0, y=0):
	enemy_ship = ship.generateShip(rd.randint(0,len(ship.ship_class_names)-1))
	enemy_ship.loadNewImage('destroyer')
	enemy_ship.setLocation(x, y)
	#Set the ship's health bar. This must be done right before adding any ship to tangibles
	enemy_ship.setHealthBar()
	enemy_ship.setProfile()
	globalvars.tangibles.add(enemy_ship)
	globalvars.whiskerables.add(enemy_ship)


def resetDust():
	#Kill all the old dust.
	for d in globalvars.intangibles_bottom:
		if d.is_a == globalvars.DUST:
			d.kill()
	for d in globalvars.intangibles_top:
		if d.is_a == globalvars.DUST:
			d.kill()
	#Make 50 dust particles scattered around the player.
	for _ in range(50):
		size = rd.randint(1,4)
		x,y = getCoordsNearLoc(globalvars.player.rect.center, 50, 
				globalvars.WIDTH, globalvars.WIDTH)
		temp = objInstances.Dust(x=x, y=y, width=size, height=size,\
				 color=colors.white)
		globalvars.intangibles_bottom.add(temp)


def resetDustOnTop():
	#Kill all the old dust.
	for d in globalvars.intangibles_bottom:
		if d.is_a == globalvars.DUST:
			d.kill()
	for d in globalvars.intangibles_top:
		if d.is_a == globalvars.DUST:
			d.kill()
	#Make 50 dust particles scattered around the player.
	for _ in range(50):
		size = rd.randint(1,4)
		x,y = getCoordsNearLoc(globalvars.player.rect.center, 50, 
				globalvars.WIDTH, globalvars.WIDTH)
		temp = objInstances.Dust(x=x, y=y, width=size, height=size,\
				 color=colors.white)
		globalvars.intangibles_top.add(temp)


def profile():
	'''Profile some of the functions in this file.'''
	import cProfile
	cProfile.runctx('for _ in range(10000): hudHelpers.getObstacles(seed=0)', globals(),locals(), 'profiling/getObstacles.profile')
	cProfile.runctx('for _ in range(1000): 	obstacles = hudHelpers.getObstacles(seed=0); hudHelpers.populateSpace(objects=obstacles, width=1000, height=1000, center=(0,0), seed=0)', globals(),locals(), 'profiling/populateSpace.profile')

