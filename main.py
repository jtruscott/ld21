import logging
#logging.basicConfig(filename='debug.log', level=logging.INFO)
logger = logging.getLogger('')
hdlr = logging.FileHandler('debug.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr) 
logger.setLevel(logging.DEBUG)

import game
try:
    game.start()
except:
    import WConio
    #WConio.textmode()
    raise
finally:
    logger.debug("Shutting down")
    logging.shutdown()
