import globalvars
import random as rd


node_index = 0
faction_index = 1


class Mission():
	def __init__(self, name, success_description, failure_description, method):
		self.name = name
		self.node = None
		self.faction = None
		self.difficulty = 0
		self.method = method
		self.success_description = success_description
		self.failure_description = failure_description
		#The following arrays will contain arrays of the following values:
		#attribute_index_low, attribute_index_high, amount_change, target_object
		#index low and high are used so that a random attribute can be changed as when tech is changed.
		self.consequences_win = []
		self.consequences_fail = []


	def addWinConsequence(self, attribute_index_low, attribute_index_high, amount_change, target_object):
		self.consequences_win.append([attribute_index_low, attribute_index_high, amount_change, target_object])


	def addLoseConsequence(self, attribute_index_low, attribute_index_high, amount_change, target_object):
		self.consequences_fail.append([attribute_index_low, attribute_index_high, amount_change, target_object])


	def getTextArray(self):
		return [self.name,
			str(self.difficulty),
			self.success_description,
			self.failure_description]


	def executeConsequences(self, consequences):
		for c in consequences:
			attribute_index_low = c[0]
			attribute_index_high = c[1]
			amount_change = c[2]
			target_index = c[3]
			target_object = None
			if target_index == node_index:
				target_object = self.node
			elif target_index == faction_index:
				target_object = self.faction
			else:
				print 'ERROR in executeConsequences.'; exit()
			attribute_index = attribute_index_low
			if attribute_index_low != attribute_index_high:
				attribute_index = rd.randint(attribute_index_low, attribute_index_high)
			target_object.changeAttribute(attribute_index, amount_change)



def getMissionArray():
	missions = []

	temp = Mission('Asteroids','Asteroids -1. Faction +1','Asteroids +1. Faction -1', globalvars.scenario_manager.asteroids)
	temp.addWinConsequence(globalvars.node_debris_index, globalvars.node_debris_index, -1, node_index)
	temp.addWinConsequence(globalvars.faction_relationship_index, globalvars.faction_relationship_index, 1, faction_index)
	temp.addLoseConsequence(globalvars.node_debris_index, globalvars.node_debris_index, 1, node_index)
	temp.addLoseConsequence(globalvars.faction_relationship_index, globalvars.faction_relationship_index, -1, faction_index)
	missions.append(temp)

	temp = Mission('Gem Wild','Wealth -1. Personal Wealth +?. Faction -1','Faction -1', globalvars.scenario_manager.gemWild)
	temp.addWinConsequence(globalvars.faction_relationship_index, globalvars.faction_relationship_index, -1, faction_index)
	temp.addWinConsequence(globalvars.node_wealth_index, globalvars.node_wealth_index, -1, node_index)
	temp.addLoseConsequence(globalvars.faction_relationship_index, globalvars.faction_relationship_index, -1, faction_index)
	missions.append(temp)

	temp = Mission('Race','Tech +1. Faction +1','Faction -1', globalvars.scenario_manager.race)
	temp.addWinConsequence(globalvars.faction_relationship_index, globalvars.faction_relationship_index, 1, faction_index)
	temp.addWinConsequence(globalvars.faction_weapon_tech_index, globalvars.faction_engine_tech_index, 1, faction_index)
	temp.addLoseConsequence(globalvars.faction_relationship_index, globalvars.faction_relationship_index, -1, faction_index)
	missions.append(temp)

	temp = Mission('Furball','Tech -1. Faction -1','Faction -1', globalvars.scenario_manager.furball)
	temp.addWinConsequence(globalvars.faction_relationship_index, globalvars.faction_relationship_index, -1, faction_index)
	temp.addWinConsequence(globalvars.faction_weapon_tech_index, globalvars.faction_engine_tech_index, -1, faction_index)
	temp.addLoseConsequence(globalvars.faction_relationship_index, globalvars.faction_relationship_index, -1, faction_index)
	missions.append(temp)

	temp = Mission('Capital ship','Production -1. Faction -1','Faction -1', globalvars.scenario_manager.capitalShipScenario)
	temp.addWinConsequence(globalvars.faction_relationship_index, globalvars.faction_relationship_index, -1, faction_index)
	temp.addWinConsequence(globalvars.node_production_index, globalvars.node_production_index, -1, node_index)
	temp.addLoseConsequence(globalvars.faction_relationship_index, globalvars.faction_relationship_index, -1, faction_index)
	missions.append(temp)

	temp = Mission('Escort','Tech +1. Faction +1','Faction -1', globalvars.scenario_manager.escort)
	temp.addWinConsequence(globalvars.faction_relationship_index, globalvars.faction_relationship_index, 1, faction_index)
	temp.addWinConsequence(globalvars.faction_weapon_tech_index, globalvars.faction_engine_tech_index, 1, faction_index)
	temp.addLoseConsequence(globalvars.faction_relationship_index, globalvars.faction_relationship_index, -1, faction_index)
	missions.append(temp)

	temp = Mission('Battle','Tech -1. Faction -1','Faction -1', globalvars.scenario_manager.epicBattle)
	temp.addWinConsequence(globalvars.faction_relationship_index, globalvars.faction_relationship_index, -1, faction_index)
	temp.addWinConsequence(globalvars.faction_weapon_tech_index, globalvars.faction_engine_tech_index, -1, faction_index)
	temp.addLoseConsequence(globalvars.faction_relationship_index, globalvars.faction_relationship_index, -1, faction_index)
	missions.append(temp)

	return missions

