import logging
#logging.basicConfig(filename='debug.log', level=logging.INFO)
logger = logging.getLogger('')
#clear the log
with open('debug.log', 'w') as dbglog:
    dbglog.write('')

hdlr = logging.FileHandler('debug.log')
formatter = logging.Formatter('%(asctime)s %(name)s:%(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr) 
logger.setLevel(logging.DEBUG)

import sys
import os
if 'nt' not in sys.argv:
    import XConio
    import curses
    import game
    game.start = curses.wrapper(game.start)
import WConio as W
defaultcolor = W.gettextinfo()[4]

import game
try:
    game.start()
except game.GameShutdown:
    W.textmode()
    pass
except KeyboardInterrupt:
    W.textmode()
    raise
except:
    raise
finally:
    logger.debug("Shutting down")
    logging.shutdown()
    W.clreol()
    W.textattr(defaultcolor)
    W.setcursortype(1)
