import globalvars
import colors
import random as rd

class FactionAction():
	def __init__(self, action, node, actor):
		self.action = action #a string
		self.node = node #a node object
		self.actor = actor #a faction object

	def toString(self):
		return self.actor.name+' takes action '+self.action+' on node with id '+str(self.node.id)


class Faction():
	def __init__(self, name, myid, color, flag=None):
		''' '''
		self.name = name
		self.id = myid
		self.color = color
		self.flag = flag #Later this should be a small square image
		self.allies = []
		self.enemies = []
		self.nodes = []
		self.money = 0
		self.capital_ships = 0
		#Zero is neutral. Positive is a good relationship. Negative is a bad relationship.
		self.relationToPlayer = 0
		#Faction tech level
		self.ship_tech = 0
		self.engine_tech = 0
		self.weapon_tech = 0
		self.missile_tech = 0
		self.mine_tech = 0

	def captureNode(self, nodeid):
		'''Do this very carefully.'''
		#Make sure that the node has no current owner.
		node = globalvars.galaxy.getNode(nodeid)
		if node.owner != -1: print 'ERROR: node is already owned by '+str(node.owner)+'.'; exit()
		if nodeid in self.nodes: print 'ERROR: node is already owned by self.'; exit()
		self.nodes.append(nodeid)
		node.owner = self.id
		node.flag = self.flag

	def getRandomBorderNode(self):
		'''Get the id of a random node that is not owned by this faction, but which 
		borders a node owned by this faction.'''
		#Get a copy of all nodes, but shuffled randomly
		temp = self.nodes[:]
		rd.shuffle(temp)
		for nodeid in temp:
			node = globalvars.galaxy.getNode(nodeid)
			for c in node.connections:
				if not c[0] in self.nodes:
					return c[0]
		return -1

	def getTextArray(self):
		return ['Name: '+self.name,
			'Flag: '+str(self.flag),
			'Count of owned nodes: '+str(len(self.nodes)),
			'Money: $'+str(self.money),
			'Capital Ships: '+str(self.capital_ships),
			'Relationship with player: '+str(self.relationToPlayer),
			'Ship technology: '+str(self.ship_tech),
			'Engine technology: '+str(self.engine_tech),
			'Weapon technology: '+str(self.weapon_tech),
			'Missile technology: '+str(self.missile_tech),
			'Mine technology: '+str(self.mine_tech)
			]

	def changeAttribute(self, attribute_index, amount):
		if attribute_index == globalvars.faction_relationship_index:
			self.relationToPlayer += amount
		elif attribute_index == globalvars.faction_weapon_tech_index:
			self.weapon_tech += amount
		elif attribute_index == globalvars.faction_missile_tech_index:
			self.missile_tech += amount
		elif attribute_index == globalvars.faction_mine_tech_index:
			self.mine_tech += amount
		elif attribute_index == globalvars.faction_ship_tech_index:
			self.ship_tech += amount
		elif attribute_index == globalvars.faction_engine_tech_index:
			self.engine_tech += amount
		else:
			print 'Error: attribute_index, '+str(attribute_index)+' out of bounds in factions.changeAttribute'; exit()



class FactionManager():
	def __init__(self):
		self.factions = []
		#initialize a short list of factions
		self.factions.append(Faction('Federation', 0, colors.blue, flag='flag00'))
		self.factions.append(Faction('Cephalopods', 1, colors.red, flag='flag01'))
		self.factions.append(Faction('Pirates', 2, colors.black, flag='flag02'))
		#Assign each faction a random node
		for f in self.factions:
			#Get a node that is not yet owned:
			nodeid = rd.randint(0, len(globalvars.galaxy.nodes))
			node = globalvars.galaxy.getNode(nodeid)
			while node.owner != -1:
				nodeid = rd.randint(0, len(globalvars.galaxy.nodes))
				node = globalvars.galaxy.getNode(nodeid)
			#Give this node to the current faction
			f.captureNode(nodeid)
		#For testing purposes, give a faction nodes near the player's start:
		self.factions[0].captureNode(4)
		self.factions[0].captureNode(5)
		self.factions[0].captureNode(6)
		self.factions[0].captureNode(0)
		self.factions[0].captureNode(9)
		self.factions[0].captureNode(10)
		self.factions[0].captureNode(17)


	def getFactionById(self, factionid):
		for f in self.factions:
			if f.id == factionid:
				return f
		return None


	def getFactionActions(self):
		actions = [] #Store all faction actions
		for f in self.factions:
			#Get a random owned node
			randnode = rd.randint(0, len(f.nodes)-1)
			randnode = globalvars.galaxy.getNode(randnode)
			#Get a random number corresponding to an action to perform
			rand = rd.randint(0, 4)
			if rand == 0: #increase production at one of the owned nodes
				actions.append(FactionAction('production+', randnode, f))
			elif rand == 1: #increase wealth at one of owned nodes
				actions.append(FactionAction('wealth+', randnode, f))
			elif rand == 2: #decrease debris at one of owned nodes
				actions.append(FactionAction('debris-', randnode, f))
			elif rand == 3: #increase tech
				actions.append(FactionAction('tech+', randnode, f))
			else: #pick a neighboring node and attack it
				#Pick a neighboring node
				randnode = f.getRandomBorderNode()
				#If no border node exists then skip and no action is performed.
				if randnode == -1: continue
				randnode = globalvars.galaxy.getNode(randnode)
				#if node is unoccupied then add it to list of owned nodes
				if randnode.owner == -1 or randnode.getStrength() == 0:
					actions.append(FactionAction('capture', randnode, f))
				#else do one of the following
				else:
					rand = rd.randint(0, 6)
					if rand == 0: #decrease production of node
						actions.append(FactionAction('production-', randnode, f))
					elif rand == 1: #decrease wealth of node
						actions.append(FactionAction('wealth-', randnode, f))
					elif rand == 2: #decrease tech
						actions.append(FactionAction('tech-', randnode, f))
					elif rand == 3:  #increase debris of node
						actions.append(FactionAction('debris+', randnode, f))
					else: #attack the node to reduce its strength.
						#This is more likely than the other actions.
						actions.append(FactionAction('attack', randnode, f))
		#for a in actions: #TESTING
		#	print a.toString()
		return actions


	def performFactionActions(self, action_list): #TODO LEFT OFF HERE
		for a in action_list:
			if a.action == 'production+':
				a.node.changeAttribute(globalvars.node_production_index, 1)
				#a.node.boostProduction(production_attribute, tech_level, amount)
			elif a.action == 'production-':
				a.node.changeAttribute(globalvars.node_production_index, -1)
			elif a.action == 'wealth+':
				a.node.amt_wealth = min(3.0, a.node.amt_wealth+0.4)
			elif a.action == 'wealth-':
				a.node.amt_wealth = max(0.0, a.node.amt_wealth-0.4)
			elif a.action == 'debris+':
				a.node.amt_debris = min(15.0, a.node.amt_debris+1.0)
			elif a.action == 'debris-':
				a.node.amt_debris = max(0.0, a.node.amt_debris-1.0)
			elif a.action == 'tech+':
				pass
			elif a.action == 'tech-':
				pass
			elif a.action == 'attack':
				pass
			elif a.action == 'capture':
				#if node is unoccupied then add it to list of owned nodes
				if a.node.owner == -1:
					a.actor.captureNode(a.node.id)
				#else if strength of node is sufficiently low
				elif a.node.getStrength() == 0:
					#remove it from current owner
					owner = self.getFactionById(a.node.owner)
					owner.nodes.remove(a.node.id)
					a.node.owner = -1
					#add it to this owner.
					a.actor.captureNode(a.node.id)
			else:
				print 'Error, unrecognized action in performFactionActions from action "'\
					+a.toString()+'"'
				exit()


	def update(self, player_dest_nodeid):
		'''Update each faction. On each update, every faction will do one of the following:
		  increase production at one of the owned nodes
		  increase wealth at one of owned nodes
		  decrease debris at one of owned nodes
		  pick a neighboring node and attack it
		    if node is unoccupied then add it to list of owned nodes
		    else if strength of node is sufficiently low, remove it from current owner and 
		      add it to this owner.
		    else do one of the following
		      decrease strength of node
		      decrease wealth of node
		      increase debris of node'''
		actions = self.getFactionActions()
		#Previously I wanted actions that happen to occur at the location 
		#the player is headed to to be influenced by the player. I imagined
		#the player getting a pop up menu asking if he/she would like to 
		#take the mission. However, I think this is too random so I'm commenting out 
		#the code that implemented it for now:
		#See also menus.setOpportunityPanel and scenarios.goToInfiniteSpace
		#Find and extract an action, if any, that occurs at the player's destination node.
		to_return = None
		#for a in actions:
		#	if a.node.id == player_dest_nodeid:
		#		to_return = actions.remove(a)
		#		break
		#Perform the actions
		self.performFactionActions(actions)
		#Return the action for the player to influence
		return to_return

