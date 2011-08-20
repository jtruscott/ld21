import game
import random
import logging
import constants as C
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
        self.connected_to = False
        self.links_known = False
        self.stats_known = False
        ip_mapping[ip_addr] = self

        self.user = 'root'
        self.command_prompt = '%s@"%s"' % (self.user, self.name)
        self.files = [
            'secure',
            'messages',
            'junk'
            ]
    def scan_stats(self):
        self.stats_known = True

    def travel_to(self):
        game.state.current_node = self

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
    type_name='Commlink'
    name_range = C.commlink_names
    processor_range = range(1,2)
    storage_range = range(1,2)
    security_range = range(1,3)
    bandwidth_range = range(1,3)
    exposure_mod = 2
    max_links = 4

class PC(Node):
    type_name='PC'
    name_range = ['PC']
    processor_range = range(1,3)
    storage_range = range(2,4)
    security_range = range(1,4)
    bandwidth_range = range(2,4)
    exposure_mod = 0
    max_links = 3

class Office(Node):
    type_name='Office'
    name_range = C.company_names
    processor_range = range(2,4)
    storage_range = range(2,4)
    security_range = range(3,5)
    bandwidth_range = range(2,4)
    exposure_mod = 1
    max_links = 3 #LAN not included

class Server(Node):
    type_name='Server'
    name_range = ['Server']
    processor_range = range(3,5)
    storage_range = range(2,6)
    security_range = range(3,5)
    bandwidth_range = range(2,4)
    exposure_mod = 1
    max_links = 3

class Laboratory(Node):
    type_name='Lab'
    name_range = ['Test Lab']
    processor_range = range(3,6)
    storage_range = range(2,4)
    security_range = range(2,4)
    bandwidth_range = range(1,3)
    exposure_mod = 0
    max_links = 1
          
class Datacenter(Node):
    type_name='Datacenter'
    name_range = ['Saeder-Krupp', 'Aztechnology', 'EVO Corp', 'Ares Macrotechnology',
                    'Horizon Entertainment', 'NeoNET', 'Renraku Computer Systems', 'Wuxing Inc']
    processor_range = range(4,5)
    storage_range = range(4,6)
    security_range = range(4,6)
    bandwidth_range = range(4,7)
    exposure_mod = 3
    max_links = 10

class Military(Node):
    type_name='Military'
    name_range = ['NORAD', 'NATO', 'CSTO', 'EURASEC']
    processor_range = range(7,14)
    storage_range = range(7,14)
    security_range = range(8,14)
    bandwidth_range = range(7,14)
    exposure_mod = -1
    max_links = 5

class MilitaryServer(Node):
    type_name='MilServer'
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
        source.links.append(target)
        target.links.append(source)
        source.exposure = source.exposure_mod + (len(source.links) / 3)
        target.exposure = target.exposure_mod + (len(target.links) / 3)
    
    def full(node):
        return len(node.links) > node.max_links

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
    homes = []
    for i in range(random.randint(150,250)):
        node = PC.create()
        commlink = random.choice(commlinks.values())
        if not full(commlink):
            log.debug('adding pc connection from %s to %s',node.ip_addr,commlink.ip_addr)
            link(node, commlink)
        homes.append(node)

    #Create office LANs
    offices = {}
    laboratories = []
    for company in Office.name_range:
        log.debug('creating office: %s', company)
        octet = random.randint(0,255)
        node = Office.create(name = company, octet=octet)
        #Create PCs behind offices
        for i in range(random.randint(2,16)):
            pc = PC.create(name = "%s - Workstation %i" % (company, i), octet=octet)
            link(node, pc)
            #randomly link some office PCs to commlinks
            if random.randint(0,5) == 0:
                commlink = random.choice(commlinks.values())
                if not full(commlink):
                    log.debug('adding officepc-commlink connection from %s to %s',pc.ip_addr,commlink.ip_addr)
                    link(pc, commlink)
            #and some to home PCs
            if random.randint(0,3) == 0:
                homepc = random.choice(homes)
                if not full(homepc):
                    log.debug('adding pc-pc connection from %s to %s',pc.ip_addr,homepc.ip_addr)
                    link(pc, homepc)
        
        #create Servers behind larger offices
        for j in range(i / 4):
            server = Server.create(name = "%s - Server %i" % (company, j), octet = octet)
        
        #create Labs in the big ones
        for k in range(i / 7):
            lab = Laboratory.create(name = "%s - Test Lab %i" % (company, k), octet = octet)
            link(node, lab)
            laboratories.append(lab)

        offices[company] = node            

    sparse_commlinks = sorted([(len(n.links),n) for n in commlinks.values()])
    sparse_homes = sorted([(len(n.links),n) for n in homes])
    sparse_offices = sorted([(len(n.links),n) for n in offices.values()])
    #add some militaries
    militaries = {}
    for mil in Military.name_range:
        log.debug('creating military: %s', mil)
        octet = random.randint(0,255)
        node = Military.create(name = mil, octet=octet)

        #create military servers
        for i in range(random.randint(8, 32)):
            server = MilitaryServer.create(name = "%s - Server %i" % (mil, i), octet=octet)
            link(server, node)
        militaries[mil] = node
        #link them to some of the sparsest commlinks and pcs each
        for i in range(random.randint(0,6)):
            commlink = sparse_commlinks.pop()[1]
            link(node, commlink)
        for i in range(random.randint(0,6)):
            pc = sparse_homes.pop()[1]
            link(node, pc)
        for i in range(random.randint(0,2)):
            office = sparse_offices.pop()[1]
            link(node, office)

    #Start the player in a random laboratory            
    start_node = random.choice(laboratories)
    #Staticize that lab's stats
    start_node.name = "Home Node"
    start_node.user = "self"
    start_node.connected_to = True
    start_node.command_prompt = '%s@"%s"' % (start_node.user, start_node.name)
    start_node.processor = 3
    start_node.storage = 3
    start_node.bandwidth = 3
    start_node.security = 2

    game.state.current_node = start_node
