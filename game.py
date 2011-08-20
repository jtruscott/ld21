import functools
import logging, sys
import random
log = logging.getLogger('game')

listeners = {}

class Node:
    def __init__(self, name, ip_addr, processor, storage, bandwidth, exposure):
        (self.name, self.ip_addr, self.processor, self.storage, self.bandwidth, self.exposure) = (name, ip_addr, processor, storage, bandwidth, exposure)

class state:
    mission = 1
    time = 2500
    current_node = Node('Test Node', '10.0.0.1', *[random.randint(1,6) for _ in range(4)])

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
    fire('clear')
    fire('tick')
    fire('prompt')

    logging.shutdown()
