import game
import random

class Node:
    def __init__(self, name, ip_addr, processor, storage, bandwidth, security, exposure):
        self.name = name
        self.ip_addr = ip_addr
        self.processor = processor
        self.storage = storage
        self.bandwidth = bandwidth
        self.security = security
        self.exposure = exposure

        self.user = 'root'
        self.command_prompt = '%s@"%s"' % (self.user, self.name)
@game.on('setup')
def setup_nodes():
    game.state.current_node = Node('Test Node', '10.0.0.1', *[random.randint(1,6) for _ in range(5)])
