import functools
import logging, sys
import pdb
log = logging.getLogger('game')

listeners = {}

def on(event):
    def wrapper(fn):
        log.debug('on %s: %s', event, fn.__name__)
        listeners.setdefault(event, [])
        listeners[event].append(fn)
        return fn
    return wrapper

def fire(event):
    [f() for f in listeners[event]]

def start():
    log.debug("Starting up")
    import draw, hud, gameprompt

    draw.setup()
    hud.setup()
    fire('tick')
    fire('prompt')

    logging.shutdown()
