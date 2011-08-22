import logging
log = logging.getLogger('game')

class GameShutdown(Exception): pass

class state:
    pass

class player:
    @staticmethod
    def lose_hp(amt, source):
        player.hp = max(0, player.hp - amt)
        if not player.hp:
            state.killer = source
            import gameprompt
            gameprompt.death_screen()

listeners = {}

def on(event):
    def wrapper(fn):
        log.debug('on %s: %s.%s', event, fn.__module__, fn.__name__)
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
    state.time = 24*60
    state.running = True
    state.tunnels = []
    state.aggregate_bandwidth = 0
    state.defended_node = None

    player.hp = player.max_hp = 12
    player.vulnerable = False
    player.attack = 2
    player.defense = 2
    player.hacking = 2
    player.stealth = 2

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
    import draw, hud, gameprompt, terminal, nodes, commands, npc

    fire('setup')
    fire('clear')
    while state.running:
        fire('tick')
        fire('prompt')
