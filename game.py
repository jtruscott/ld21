import logging
log = logging.getLogger('game')

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

def start():
    log.debug("Starting up")
    import draw, hud, gameprompt, terminal, nodes

    fire('setup')
    fire('clear')
    fire('tick')
    fire('prompt')

    logging.shutdown()
