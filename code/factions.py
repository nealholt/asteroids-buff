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
		#Zero is neutral. Positive is a good relationship. Negative is a bad relationship.
		self.relationToPlayer = 0

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


	def getFactionById(self, factionid):
		for f in self.factions:
			if f.id == factionid:
				return f
		return None


	def getFactionActions(self):
		actions = [] #Store all faction actions
		for f in self.factions:
			#Get a random number corresponding to an action to perform
			rand = rd.randint(0, 3)
			#Get a random owned node
			randnode = rd.randint(0, len(f.nodes)-1)
			randnode = globalvars.galaxy.getNode(randnode)
			if rand == 0: #increase strength at one of the owned nodes
				actions.append(FactionAction('strength+', randnode, f))
			elif rand == 1: #increase wealth at one of owned nodes
				actions.append(FactionAction('wealth+', randnode, f))
			elif rand == 2: #decrease debris at one of owned nodes
				actions.append(FactionAction('debris-', randnode, f))
			elif rand == 3: #pick a neighboring node and attack it
				#Pick a neighboring node
				randnode = f.getRandomBorderNode()
				#If no border node exists then skip and no action is performed.
				if randnode == -1: continue
				randnode = globalvars.galaxy.getNode(randnode)
				#if node is unoccupied then add it to list of owned nodes
				if randnode.owner == -1 or randnode.strength == 0.0:
					actions.append(FactionAction('capture', randnode, f))
				#else do one of the following
				else:
					rand = rd.randint(0, 3)
					#decrease strength of node
					if rand < 2:
						actions.append(FactionAction('strength-', randnode, f))
					#decrease wealth of node
					elif rand == 2:
						actions.append(FactionAction('wealth-', randnode, f))
					#increase debris of node
					else:
						actions.append(FactionAction('debris+', randnode, f))
		#for a in actions: #TESTING
		#	print a.toString()
		return actions


	def performFactionActions(self, action_list):
		for a in action_list:
			if a.action == 'strength+':
				a.node.strength = min(2.0, a.node.strength+0.2)
			elif a.action == 'strength-':
				a.node.strength = max(0.0, a.node.strength-0.2)
			elif a.action == 'wealth+':
				a.node.amt_wealth = min(3.0, a.node.amt_wealth+0.4)
			elif a.action == 'wealth-':
				a.node.amt_wealth = max(0.0, a.node.amt_wealth-0.4)
			elif a.action == 'debris+':
				a.node.amt_debris = min(15.0, a.node.amt_debris+1.0)
			elif a.action == 'debris-':
				a.node.amt_debris = max(0.0, a.node.amt_debris-1.0)
			elif a.action == 'capture':
				#if node is unoccupied then add it to list of owned nodes
				if a.node.owner == -1:
					a.actor.captureNode(a.node.id)
				#else if strength of node is sufficiently low
				elif a.node.strength == 0.0:
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
		  increase strength at one of the owned nodes
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
		#Find and extract an action, if any, that occurs at the player's destination node.
		to_return = None
		for a in actions:
			if a.node.id == player_dest_nodeid:
				to_return = actions.remove(a)
				break
		#Perform the actions
		self.performFactionActions(actions)
		#Return the action for the player to influence
		return to_return

