import sys
sys.path.append('code')
import game
from scenarios import testScenario00
if __name__=="__main__":
	print 'Using flip instead of dirty rectangles can be set with -flip. For example:\n'+\
		'   python playGame.py -flip\n'+\
		'The default value is to use dirty.\n'
	if '-flip' in sys.argv:
		game.useDirty = False

	#Initial test scenario
	testScenario00()

	game.run()

