import weapon
import engine
#Each method in this file takes a physical object and sets a profile for the object. For example, bulletProfile(pObject) will set pObject to have bullet characteristics. Then the bullet will call bulletProfile on itself. This, I think, will clean the code and reduce redundancy and voodoo constants.

def shipProfile(ship, profile='default'):
	#Give enemy a random weapon
	temp = weapon.generateWeapon(rd.randint(0, len(weapon.weapon_class_names)-1))
	temp.shooter = ship
	ship.gun = temp
	#Give enemy an engine
	ship.engine = engine.Engine()
	engine.setProfile('mk1', ship.engine)
	#return 'destroyer' #Return the image to use

