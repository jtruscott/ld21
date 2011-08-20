import game
import random
import logging
log = logging.getLogger('nodes')

random_ids = range(1000)
random.shuffle(random_ids)

ip_mapping = {}
def random_ip(octet=None):
    while True:
        if octet is None:
            start = random.randint(0,255)
        else:
            start = octet
        ip_addr = "%s.%s.%s.%s" % (start, random.randint(0,255), random.randint(0,255), random.randint(0, 255))
        if ip_addr not in ip_mapping:
            break
    return ip_addr
    

class Node:
    name_range = ["Test Node"]

    def __init__(self, name, ip_addr, processor, storage, bandwidth, security, exposure):
        self.name = name
        self.ip_addr = ip_addr
        self.processor = processor
        self.storage = storage
        self.bandwidth = bandwidth
        self.security = security
        self.exposure = exposure

        self.links = []
        ip_mapping[ip_addr] = self

        self.user = 'root'
        self.command_prompt = '%s@"%s"' % (self.user, self.name)
        self.files = [
            'secure',
            'messages',
            'junk'
            ]

    @classmethod
    def create(cls, name=None, octet=None):
        if name is None:
            name = random.choice(cls.name_range) + " %s" % random_ids.pop()
        return cls(
            name = name,
            ip_addr = random_ip(octet),
            processor = random.choice(cls.processor_range),
            storage = random.choice(cls.storage_range),
            bandwidth = random.choice(cls.bandwidth_range),
            security = random.choice(cls.security_range),
            exposure = cls.exposure_mod
        )

class Commlink(Node):
    name_range = ['Commlink']
    processor_range = range(1,2)
    storage_range = range(1,2)
    security_range = range(1,3)
    bandwidth_range = range(1,3)
    exposure_mod = 2
    max_links = 4

class PC(Node):
    name_range = ['PC']
    processor_range = range(1,3)
    storage_range = range(2,4)
    security_range = range(1,4)
    bandwidth_range = range(2,4)
    exposure_mod = 0
    max_links = 3

class Office(Node):
    name_range = C.company_names
    processor_range = range(2,4)
    storage_range = range(2,4)
    security_range = range(3,5)
    bandwidth_range = range(2,4)
    max_links = 3 #LAN not included

class Server(Node):
    name_range = ['Server']
    processor_range = range(3,5)
    storage_range = range(2,6)
    security_range = range(3,5)
    bandwidth_range = range(2,4)
    exposure_mod = 1
    max_links = 3
          
class Datacenter(Node):
    name_range = ['Saeder-Krupp', 'Aztechnology', 'EVO Corp', 'Ares Macrotechnology',
                    'Horizon Entertainment', 'NeoNET', 'Renraku Computer Systems', 'Wuxing Inc']
    processor_range = range(4,5)
    storage_range = range(4,6)
    security_range = range(4,6)
    bandwidth_range = range(4,7)
    exposure_mod = 3
    max_links = 10

class Military(Node):
    name_range = ['NORAD', 'NATO', 'CSTO', 'EURASEC']
    processor_range = range(7,14)
    storage_range = range(7,14)
    security_range = range(8,14)
    bandwidth_range = range(7,14)
    exposure_mod = -1
    max_links = 5

class MilitaryServer(Node):
    name_range = ['Military-Grade Server']
    processor_range = range(6,12)
    storage_range = range(6,12)
    security_range = range(6,12)
    bandwidth_range = range(6,12)
    exposure_mod = 0
    max_links = 3

@game.on('setup')
def setup_nodes():
    '''
        Generate the world map.
    '''
    def link(source, target):
        if target in source.links:
            log.warn('relinking %s and %s',source.ip_addr,target.ip_addr)
            return
        target.links.append(source)
        source.links.append(target)
    
    def full(node):
        return len(node.links) > node.max_links

    nodes = []
    #Create commlinks on a grid
    commlinks = {}
    for i in range(600):
        x,y = random.randint(0,200), random.randint(0,200)
        commlinks[(x,y)] = Commlink.create()
    
    #Randomly Link commlinks together by physical proximity
    for i in range(random.randint(400,600)):
        log.debug('i: %i', i)

        x,y = random.choice(commlinks.keys())
        source = commlinks[(x,y)]
        
        log.debug('trying to link commlink %s at %i,%i',source.ip_addr,x,y)
        if full(source):
            log.debug('source already full')
            continue

        #try to make a link
        tries = 0
        maxtries = 25
        while tries < maxtries:
            tries += 1
            nx, ny = (x + random.randint(-4, 4), y + random.randint(-4, 4))
            if (nx,ny) in commlinks:
                target = commlinks[(nx,ny)]
                log.debug('found target %s at %i,%i',target.ip_addr, nx,ny)
                if full(target):
                    log.debug('target already full')
                    continue
                log.debug('linking target on try %i', tries)
                link(source, target)
                break

        if tries == maxtries:
            log.debug('gave up')

    #Create datacenter rings
    datacenters = {}
    for corp in Datacenter.name_range:
        log.debug('creating corp datacenter %s', corp)
        octet = random.randint(0,255)
        nodes = []
        for i in range(random.randint(3,8)):
            nodes.append(Datacenter.create(name="%s - %i" % (corp, i), octet=octet))
        #link the rings together
        for i in range(len(nodes)):
            link(nodes[i],nodes[i-1])        
        
        #Randomly link datacenter nodes to commlinks
        for node in nodes:
            log.debug('linking datacenter node %s', node.ip_addr)
            while not full(node):
                commlink = random.choice(commlinks.values())
                if full(commlink):
                    log.debug('commlink %s is full', commlink.ip_addr)
                    continue
                link(commlink, node)
        datacenters[corp] = nodes

    #Create home PCs 
    #Randomly link home PCs to single commlinks
    homes = {}
    for 
    #Create office LANs
    offices = {}
    for company in Office.name_range:
        log.debug('creating office: %s', company)
        node = Office.create(name = company)
        octet = random.randint(0,255)
        #Create PCs behind offices
        for i in range(random.randint(2,16)):
            pc = PC.create(name = "%s - Workstation %i" % (company, i), octet=octet)
            link(node, pc)
            #randomly link some office PCs to commlinks
            if random.randint(0,5) == 0:
                commlink = random.choice(commlinks.values())
                if not full(commlink):
                    log.debug('adding pc connection from %s to %s',pc.ip_addr,commlink.ip_addr)
                    link(pc, commlink)
        
        #create Servers behind larger offices
        for j in range(i / 4):
            server = Server.create(name = "%s - Server %i" % (company, j), octet = octet)

        offices[company] = node            

    #add some militaries
    #link them to the 3 sparsest commlinks each
    game.state.nodes = nodes

    game.state.current_node = Node('Test Node', '10.0.0.1', *[random.randint(1,6) for _ in range(5)])
