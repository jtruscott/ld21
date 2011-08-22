import game
import nodes
import constants as C
import random
import logging
import terminal
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
        if node:
            self.node = node
            self.node.add_npc(self)
    
    def fight(self):
        self.attack()
        self.defend(counter=True)

    def attack(self):
        defense_roll = nodes.dice(game.state.home_node.processor + game.player.defense)
        attack_roll = nodes.dice(self.power)
        if attack_roll > defense_roll:
            damage = attack_roll - defense_roll + 1
            terminal.add_line("<MAGENTA>COMBAT:<LIGHTGREY> %s attacks you for <LIGHTRED>%i<LIGHTGREY> damage!" % (self.name, damage))
            game.player.lose_hp(damage, self.name)
        else:
            terminal.add_line("<MAGENTA>COMBAT:<LIGHTGREY> %s misses you!" % (self.name))

    def defend(self,counter=False):
        attack_roll = nodes.dice(game.state.home_node.processor + game.player.attack)
        defense_roll = nodes.dice(self.power)
        if counter:
            counter = 'counter'
        else:
            counter = ''

        if attack_roll > defense_roll:
            damage = attack_roll - defense_roll + 1
            terminal.add_line("<MAGENTA>COMBAT:<LIGHTGREY> you %sattack %s for <LIGHTRED>%i<LIGHTGREY> damage!" % (counter, self.name, damage))
            self.hp -= damage
            if self.hp <= 0:
                self.defeated()
        else:
            terminal.add_line("<MAGENTA>COMBAT:<LIGHTGREY> you %sattack %s, but miss!" % (counter, self.name))
    
    def defeated(self):
        terminal.add_line("<MAGENTA>COMBAT:<LIGHTGREY> you defeat %s in cybercombat!" % (self.name))
        self.state = 'dead'
        self.go_to(None)
        self.delay = 10000

        if random.randint(0,2) == 0:
            program = random.choice(['attack', 'defense', 'hacking', 'stealth'])
            if getattr(game.player, program) < self.power:
                terminal.add_line("<LIGHTGREEN>PROGRAM:<LIGHTGREY> you salved a <WHITE>Rating %i %s<LIGHTGREY> program off your foe!" % (self.power, program))
                setattr(game.player, program, self.power)


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
                if game.state.defended_node == self.node:
                    #fight!
                    self.fight()
                    self.delay += random.randint(8,15)
                    return
                else:
                    #purge!
                    self.node.purge(self)
            self.delay += random.randint(5,15)
            self.state = 'idle'
            return

        if self.state == 'dead':
            self.delay += 100000

class Faction:
    def __init__(self, key, name, competence, members):
        self.key = key
        self.name = name
        self.competence = competence
        self.members = []
        self.spawn_clock = 24 * 60
        self.name_index = 0
        for i in range(members):
            self.spawn_member()
    
    def spawn_member(self):
        if self.key == 'bbeg':
            node = random.choice(nodes.ip_mapping.values())
        else:
            node = random.choice(nodes.corp_nodes[self.key])
        self.members.append(NPC(
            node,
            "%s %s" % (self.name, C.nato_alphabet[self.name_index]),
            self.competence - random.uniform(0, 0.2),
        ))
        self.name_index += 1
        if self.name_index >= len(C.nato_alphabet):
            self.name_index = 0

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
    faction.spawn_clock -= t
    if faction.spawn_clock < 0:
        faction.spawn_clock = 23 * 60 + random.randint(0, 120)
        faction.competence += random.uniform(0.1, 0.2)
        faction.spawn_member()
