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

import WConio as W
defaultcolor = W.gettextinfo()[4]

import game
try:
    game.start()
except:
    #WConio.textmode()
    raise
finally:
    logger.debug("Shutting down")
    logging.shutdown()
    W.clreol()
    W.textattr(defaultcolor)

