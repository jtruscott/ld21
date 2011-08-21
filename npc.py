import game
import nodes
import constants as C
import random
import logging
log = logging.getLogger("corps")

corps = {}
class NPC:
    def __init__(self, node, name, competence):
        self.hp = int(random.uniform(5, 8) * competence)
        self.power = int(random.uniform(3,6) * competence)
        self.name = name
        self.delay = random.randint(90,180)
        self.node = None
        self.go_to(node)
        self.state = 'idle'
    
    def go_to(self, node):
        if self.node:
            self.node.remove_npc(self)
        self.node = node
        self.node.add_npc(self)

    def act(self):
        log.debug('state: %s',self.state)
        def start_hack(target):
            self.state = 'hacking'
            self.delay += 15
            self.target = target
            self.tries = 0
            target.start_npc_hack(self)

        if self.state == 'idle':
            #scan nearby nodes for interesting things
            for neighbor in self.node.links:
                if neighbor.user:
                    #oh shit the PC is there
                    start_hack(neighbor)
                    return
            
            #drain interest
            self.node.interest = max(self.node.interest - 0.5, 0.0)
            if self.node.alarmed:
                self.node.npc_disarm()

            #nope, hack to a random node based on what looks interesting
            interestingNodes = [(node.interest, node) for node in nodes.ip_mapping.values()]
            interestingNodes.sort(reverse=True)
            target = random.choice(interestingNodes[:20])[1]
            start_hack(target)
            return

        if self.state == 'hacking':
            self.tries += 1
            if self.tries == 5:
                self.state = 'idle'
                return

            self.delay += 60
            if self.target.npc_hack(self, self.power):
                self.go_to(self.target)
                self.state = 'scan'
                return

        if self.state == 'scan':
            if self.node.user:
                #found 'em!
                self.node.purge(self)
            self.delay += random.randint(5,15)
            self.state = 'idle'
            return

class Faction:
    def __init__(self, key, name, competence, members):
        self.key = key
        self.name = name
        self.competence = competence
        self.members = []
        for i in range(members):
            if key == 'bbeg':
                node = random.choice(nodes.ip_mapping.values())
            else:
                node = random.choice(nodes.corp_nodes[key])
            self.members.append(NPC(
                node,
                name,
                competence - random.uniform(0, 0.2),
            ))
    
    def tick(self):
        pass
    def time(self, elapsed):
        pass

@game.on('setup')
def npc_setup():
    #create corp npcs
    for corp in C.corp_names:
        corps[corp] = Faction(key=corp, name=corp + " Security",
                        competence=random.uniform(0.5, 1.5), members = random.randint(2, 4))

    corps['bbeg'] = Faction(key='bbeg', name="Shadow Team",
                        competence=1.7, members = 4)

@game.on('tick')
def npc_tick():
    for faction in corps.values():
        faction.tick()

@game.on('time_taken')
def npc_time(t):
    #hardcoding time
    faction = corps['bbeg']
    for npc in faction.members:
        npc.delay -= t
        while npc.delay < 0:
            npc.act()
