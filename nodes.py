import game
import random

class Node:
    def __init__(self, name, ip_addr, processor, storage, bandwidth, security, exposure):
        (self.name, self.ip_addr, self.processor, self.storage, self.bandwidth, self.security, self.exposure) = (name, ip_addr, processor, storage, bandwidth, security, exposure)

@game.on('setup')
def setup_nodes():
    game.state.current_node = Node('Test Node', '10.0.0.1', *[random.randint(1,6) for _ in range(5)])
