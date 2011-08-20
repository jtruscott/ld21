import logging
log = logging.getLogger('game')

class GameShutdown(Exception): pass

class state:
    pass


listeners = {}

def on(event):
    def wrapper(fn):
        log.debug('on %s: %s', event, fn.__name__)
        listeners.setdefault(event, [])
        listeners[event].append(fn)
        return fn
    return wrapper

def fire(event, *args):
    if event not in listeners:
        log.warn('fired event %s and nobody cared', event)
        return
    [f(*args) for f in listeners[event]]

@on('setup')
def setup_state():
    state.mission = 1
    state.time = 2500
    state.running = True

@on('shutdown')
def shutdown():
    log.debug('shutting down')
    state.running = False
    raise GameShutdown()

def take_time(time_taken):
    if time_taken is None:
        return
    state.time += time_taken
    fire('time_taken', time_taken)

def start():
    log.debug("Starting up")
    import draw, hud, gameprompt, terminal, nodes, commands

    fire('setup')
    fire('clear')
    while state.running:
        fire('tick')
        fire('prompt')
