import colors
from objInstances import Mine
import globalvars
import random as rd

num_mine_attributes = 6
#The following arrays map classes into actual values. The class is the index and the values are, well, the array values:

#Time in seconds until the mine disappears
longevity_classes = [1.5, 2.0, 2.5, 3.0]
for i in range(len(longevity_classes)):
	longevity_classes[i] = int(longevity_classes[i]*globalvars.FPS)
damage_classes = [5,10,20,30,40,50]
#This is one over the number of shots per second. So 0.1 means 10 shots per second. 0.2 = 5 shots per second.
refire_classes = [2.0, 1.5, 1.0, 0.5, 0.2]
for i in range(len(refire_classes)):
	refire_classes[i] = int(refire_classes[i]*globalvars.FPS)
ammo_classes = [1,5,10,25,50]
blast_classes = ['Area of effect', 'Fragmentation']
radius_classes = [20,40,60]
fragment_classes = [5,10,15]


#Names of the various mine classes
mine_class_names = ['Worthless', 'Scrap', 'Cheap', 'Okay', 'Cool', 'Hot', 'Noble', 'King', 'Emperor', 'Tyrant', 'Transcendent']


def generateMine(mine_class):
	'''Returns a mine of the given class.'''
	#Start by randomly generating a mine.
	mine = MineLayer(None)
	#Calculate the class of the mine.
	actual_class = mine.getMineClass()
	#print 'mine is class '+mine_class_names[actual_class]+' ('+str(actual_class)+') but should be class '+mine_class_names[mine_class]+' ('+str(mine_class)+')'
	#print 'mine name: '+mine.getMineName()
	#Now nudge the mine in the direction of the desired mine class.
	#randomly select an attribute of the mine
	randatt = rd.randint(0, num_mine_attributes-1)
	#while the mine is above the selected class...
	while actual_class > mine_class:
		#Decrement selected attribute
		mine.decrementAttribute(randatt)
		#move to the next mine attribute
		randatt = (randatt+1)%num_mine_attributes
		#Calculate the class of the mine.
		actual_class = mine.getMineClass()
		#print 'Mine is now class '+mine_class_names[actual_class]+' ('+str(actual_class)+') but should be class '+mine_class_names[mine_class]+' ('+str(mine_class)+')'
		#print 'Mine name: '+mine.getMineName()
	#randomly select an attribute of the mine
	randatt = rd.randint(0, num_mine_attributes-1)
	#while the mine is below the selected class...
	while actual_class < mine_class:
		#Increment selected attribute
		mine.incrementAttribute(randatt)
		#move to the next mine attribute
		randatt = (randatt+1)%num_mine_attributes
		#Calculate the class of the mine.
		actual_class = mine.getMineClass()
		#print 'Mine is now class '+mine_class_names[actual_class]+' ('+str(actual_class)+') but should be class '+mine_class_names[mine_class]+' ('+str(mine_class)+')'
		#print 'Mine name: '+mine.getMineName()
	#print 'Final mine is class '+mine_class_names[actual_class]+' ('+str(actual_class)+') but should be class '+mine_class_names[mine_class]+' ('+str(mine_class)+')'
	#print 'Final mine name: '+mine.getMineName()+'\n'
	mine.initialize()
	return mine


#_names arrays
longevity_names = ['Winking','','','Undying']
damage_names = ['Needle', 'Javelin','','','Missile','Torpedo']
refire_names = ['Cold','Mirthful','','Wrathful','Furious'] #maybe reduce this down to just 2 names
ammo_names = ['Tooth','','','','Epiphany'] #Maybe don't incorporate this in the name.
blast_names = ['','Fragmentation']
blast_radius_names = ['Bitter','','Ravenous']


class MineLayer():
	def __init__(self, shooter, name='default'):
		self.longevity_index = rd.randint(0, len(longevity_classes)-1)
		self.damage_index = rd.randint(0, len(damage_classes)-1)
		self.refire_index = rd.randint(0, len(refire_classes)-1)
		self.ammo_index = rd.randint(0, len(ammo_classes)-1)
		self.blast_index = rd.randint(0, len(blast_classes)-1)
		self.blast_radius_index = rd.randint(0, len(radius_classes)-1)

		self.name=name
		self.refire_rate=10 #Fires once every refire_rate frames
		self.cooldown=0 #How long until next shot
		self.shooter = shooter
		self.attack_angle = 10 #if within this angle to target, can shoot at target
		self.is_a = 'mine'


	def initialize(self):
		self.name=self.getMineName()
		self.longevity = longevity_classes[self.longevity_index]
		self.damage = damage_classes[self.damage_index]
		self.refire_rate = refire_classes[self.refire_index]
		#ammo_classes[self.ammo_index] [1,5,10,25,50]
		#blast_classes[self.blast_index] #['Area of effect', 'Fragmentation']
		#radius_classes[self.blast_radius_index] #[20,40,60]
		#fragment_classes[self.blast_radius_index] #[5,10,15]


	def cool(self):
		if self.cooldown > 0:
			self.cooldown -= 1

	def shoot(self):
		tempmine = Mine(self.shooter)
		#Add mine to the sprite groups
		globalvars.tangibles.add(tempmine)
		#Add it to whiskerables so enemy ships will avoid it.
		globalvars.whiskerables.add(tempmine)
		self.cooldown=self.refire_rate

	def toStringArray(self):
		str_array = [self.name,
			'Refire rate: '+str(self.refire_rate)]
		return str_array


	def decrementAttribute(self, attribute_index):
		if attribute_index == 0:
			if self.blast_index > 0: self.blast_index -= 1
		elif attribute_index == 1:
			if self.longevity_index > 0: self.longevity_index -= 1
		elif attribute_index == 2:
			if self.blast_radius_index > 0: self.blast_radius_index -= 1
		elif attribute_index == 3:
			if self.damage_index > 0: self.damage_index -= 1
		elif attribute_index == 4:
			if self.refire_index > 0: self.refire_index -= 1
		elif attribute_index == 5:
			if self.ammo_index > 0: self.ammo_index -= 1
		else:
			print 'ERROR in mine.decrementAttribute. Exiting'; exit()


	def incrementAttribute(self, attribute_index):
		if attribute_index == 0:
			if self.blast_radius_index < len(radius_classes)-1:
				self.blast_radius_index += 1
		elif attribute_index == 1:
			if self.longevity_index < len(longevity_classes)-1:
				self.longevity_index += 1
		elif attribute_index == 2:
			if self.blast_index < len(blast_classes)-1:
				self.blast_index += 1
		elif attribute_index == 3:
			if self.damage_index < len(damage_classes)-1:
				self.damage_index += 1
		elif attribute_index == 4:
			if self.refire_index < len(refire_classes)-1:
				self.refire_index += 1
		elif attribute_index == 5:
			if self.ammo_index < len(ammo_classes)-1:
				self.ammo_index += 1
		else:
			print 'ERROR in mine.incrementAttribute. Exiting'; exit()


	def getMineName(self):
		'''Since this is too many attributes, only give keywords for the extreme high and low values and then have these trump other attributes when naming the mine.'''
		name = ''
		if len(longevity_names[self.longevity_index]) > 0:
			name += longevity_names[self.longevity_index]+' '
		if len(refire_names[self.refire_index]) > 0:
			name += refire_names[self.refire_index]+' '
		if len(blast_radius_names[self.blast_radius_index]) > 0:
			name += blast_radius_names[self.blast_radius_index]+' '

		if len(blast_names[self.blast_index]) > 0:
			name += blast_names[self.blast_index]+' '

		elif len(damage_names[self.damage_index]) > 0:
			name += damage_names[self.damage_index]+' '
		elif len(ammo_names[self.ammo_index]) > 0:
			name += ammo_names[self.ammo_index]+' '
		return name


	def getMineClassName(self):
		return mine_class_names[self.getMineClass()]


	def getMineClass(self):
		'''Current range of Mine ratings solely based on the numbers in this method is -8 to 13 inclusive.
		I changed the return value to map these into the range 0-10 inclusive.'''
		rating = 0
		rating += self.longevity_index #0-3
		
		rating += self.damage_index-1 #0-5

		rating += self.refire_index-2 #0-4

		if self.ammo_index == 0:
			rating -= 5
		elif self.ammo_index == 1:
			rating -= 4
		elif self.ammo_index == 2:
			rating -= 2
		elif self.ammo_index == 3:
			pass
		else:
			rating += 2

		rating += self.blast_radius_index #0-2

		return (rating+8)/2


#def testing():
#	for i in range(len(mine_class_names)):
#		generateMine(i)
#testing()
#exit()
