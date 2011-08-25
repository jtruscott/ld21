import game
import gameprompt
import terminal
import nodes
import hud

import optparse
import logging
log = logging.getLogger('commands')
class CommandError(Exception):
    def __init__(self, msg="No Message"):
        self.msg = msg

class ArgumentError(CommandError): pass
class HelpError(CommandError): pass
class NoDefault: pass
ForbiddenError = nodes.ForbiddenError
AlreadyThere = nodes.AlreadyThere

class Command:
    hide = False
    description = None
    time_variable = False
    arguments = ""
    def __init__(self, command=None, arguments=None, time=None):
        if command:
            self.command = command
        if arguments:
            self.arguments = arguments
        if time:
            self.time = time

        self.make_parser()

    def make_parser(self):
        class Parser(optparse.OptionParser):
            def error(s, msg):
                log.warn("err %s" % msg)
                self.errors.extend(s.get_usage().splitlines())
                self.errors.append("<RED>ERROR: %s\n" % msg)
                raise ArgumentError(msg=self.errors)
            def exit(s, status=None, msg=None, help=False):
                if msg:
                    self.errors.append(msg)
                if help:
                    self.errors.extend(s.format_help().splitlines())
                    status = True
                if status:
                    raise ArgumentError(msg=self.errors)
                else:
                    raise HelpError()

            def print_help(s,f=None):
                self.errors.extend(s.format_help().splitlines())
                raise HelpError()
            def print_usage(s, f=None):
                self.errors.extend(s.get_usage().splitlines())
                raise HelpError()
            def print_version(s, f=None):
                pass

        self.parser = Parser(description=self.description, prog=self.command)
        self.add_options(self.parser)
    
    def add_options(self, parser):
        pass
    
    def parse(self, args):
        self.errors = []
        try:
            ret = self.parser.parse_args(args)
        except HelpError:
            pass
        if self.errors:
            raise ArgumentError(msg=self.errors)
        return ret

    def action(self, args, **kwargs):
        return self.time

class InternalCommand(Command):
    def __init__(self):
        self.command, self.arguments, self.time = ('', '', 0)

class UnknownCommand(InternalCommand):
    hide = True
    def action(self, args, command_line):
        terminal.add_line('<RED>ERROR:<LIGHTGREY> Unknown Command "%s"' % command_line)

class ErrorCommand(InternalCommand):
    hide = True
    error_type = "Syntax Error"
    def action(self, error, command_line):
        terminal.add_line(error)
        terminal.add_line()
'''
    Real commands.
'''
class LSCommand(Command):
    arguments = "[-la] [target_directory]"
    description = "Scan the current node for useful files. Some nodes have programs you can scavenge - the better the Storage, the more likely to have files, but also the longer to scan."
    time = 15
    time_variable = True

    def action(self, args, command_line):
        (options, args) = self.parse(args)
        terminal.add_line('Scanning for files...')
        try:
            time = game.state.current_node.scan_files()
            return time
        except ForbiddenError:
            terminal.add_line('<RED>ERROR:<LIGHTGREY> You must be root to scan for files!')

class ProgramsCommand(Command):
    command = "programs"
    description = "Display the list of your programs and ratings"
    time = 0

    def action(self, args, command_line):
        (options, args) = self.parse(args)
        terminal.add_line('<LIGHTGREY>PROGRAM   RATING')
        for program_name in ['attack', 'defense', 'hacking', 'stealth']:
            terminal.add_line("%s%i" % (program_name.capitalize().ljust(10), getattr(game.player,program_name)))
        

class DisarmCommand(Command):
    command = "disarm"
    description = "Disable any alarms on the current node"
    time = 5

    def action(self, args, command_line):
        (options, args) = self.parse(args)
        base = game.state.current_node
        try:
            if base.alarmed:
                base.disarm()
                terminal.add_line('Alarms disabled.')
            else:
                terminal.add_line('No alarms active on this node.')

        except ForbiddenError:
            terminal.add_line('<RED>ERROR:<LIGHTGREY> You must be root to disarm any alarms!')
        return self.time

class NeighborsCommand(Command):
    command = "neighbors"
    arguments = "[-s]"
    description = """Scan the networks attached to the current node and display a list of neighboring connected nodes"""
    time = 15
    time_variable = True
    def add_options(self, p):
        p.add_option('-s', '--stats', '--scan', dest='stats', action='store_true', help='Also probe each neighbor for node statistics (takes an additional 5m per unscanned neighbor)')
    
    def action(self, args, command_line):
        def format_stat(stat, width=5):
            color = '<DARKGREY>'
            if stat != '?':
                if stat >= 2: color = '<LIGHTGREY>'
                if stat >= 4: color = '<WHITE>'
                if stat >= 6: color = '<GREEN>'
            return color + str(stat).center(width) + '<LIGHTGREY>'

        (options, args) = self.parse(args)
        base = game.state.current_node
        t = self.time
        terminal.add_line('<LIGHTGREY># Processor Storage Security Bandwidth Exposure     Type          IPAddr          Name')
        i = -1
        for neighbor in base.links:
            i += 1
            if options.stats and not neighbor.stats_known:
                neighbor.scan_stats()
                t += 5

            if neighbor.stats_known:
                processor, storage, bandwidth, security, exposure = (
                    neighbor.processor, neighbor.storage, neighbor.bandwidth, neighbor.security, neighbor.exposure)
            else:
                processor, storage, bandwidth, security, exposure = ['?']*5

            stat_block = ''.join([
                ('%i)' % i).ljust(3),
                format_stat(processor, 8),' ',
                format_stat(storage, 7),' ',
                format_stat(security, 8),' ',
                format_stat(bandwidth, 9),' ',
                str(exposure).center(8),' ',
                neighbor.type_name.center(12),' ',
                neighbor.ip_addr.center(16),' ',
                neighbor.name
            ])
            terminal.add_line(stat_block)
        return t


class NeighborCommand(Command):
    arguments = "id"
    def action(self, args, command_line):
        (options, args) = self.parse(args)
        if not args or not len(args) == 1:
            self.parser.exit(help=True)
        try:
            neighborIndex = int(args[0])
        except:
            self.parser.error(msg="A numeric neighbor ID is required")
        base = game.state.current_node
        try:
            neighbor = base.links[neighborIndex]
        except IndexError:
            self.parser.error(msg="The Neighbor ID must be in the list of neighbors")
        
        try:
            return self.do_action(neighbor)
        except AlreadyThere:
            self.parser.error(msg="Cannot travel to a node you are already connected to")

class TunnelCommand(NeighborCommand):
    command = "tunnel"
    description = """Tunnel to an adjacent node as a guest user"""
    time = 15
    time_variable = True
    def do_action(self, neighbor):
        terminal.add_line("<LIGHTGREY>Traveling to <WHITE>%s<LIGHTGREY>..." % neighbor.ip_addr)
        try:
            neighbor.proxy()
        except ForbiddenError:
            terminal.add_line('<RED>ERROR:<LIGHTGREY> This node does not allow guest access.')
        return self.time

class HackCommand(NeighborCommand):
    command = "hack"
    description = """Hack into an adjacent node and gain root access"""
    time = 60
    time_variable = True
    def do_action(self, neighbor):
        terminal.add_line("<LIGHTGREY>Hacking into <WHITE>%s<LIGHTGREY>..." % neighbor.ip_addr)
        try:
            neighbor.hack()
        except ForbiddenError:
            terminal.add_line('<RED>ERROR:<LIGHTGREY> Hack failed! (try again?)')
        return self.time

class BackCommand(Command):
    command = "back"
    description = """Exit the current node"""
    time = 5
    def action(self, args, command_line):
        (options, args) = self.parse(args)
        base = game.state.current_node
        if base == game.state.home_node:
            self.parser.error(msg="Cannot disconnect from your home node without moving - you'd die!")
        base.back()

class HealCommand(Command):
    command = "heal"
    description = """Repair one damage to your condition monitor. """
    time = 60
    def action(self, args, command_line):
        (options, args) = self.parse(args)
        game.player.hp = min(game.player.max_hp, game.player.hp + 1)
        return self.time

class ReHomeCommand(Command):
    command = "rehome"
    description = """Move your consciousness to a new home node. This is a dangerous process - you are extremely vulnerable while it resolves"""
    time = 60*12
    time_variable = True
    def action(self, args, command_line):
        (options, args) = self.parse(args)
        base = game.state.current_node
        if base == game.state.home_node:
            self.parser.error("This node is already your home.")
        if base.user != "root":
            self.parser.error("You must have root access to change homes")

        aggregate_bandwidth = game.state.aggregate_bandwidth
        calculated_time = self.time * 2 / aggregate_bandwidth
        confirmation = gameprompt.show_confirmation("Are you <WHITE>sure<LIGHTGREY> you want to transfer your consciousness to this node?",
                                    'Transferring to <YELLOW>%s<LIGHTGREY> "<YELLOW>%s<LIGHTGREY>" while take %s at Bandwidth %i' % (
                                base.ip_addr, base.name, gameprompt.format_time(calculated_time), aggregate_bandwidth)
                        )
        if not confirmation:
            self.parser.error("Action Canceled")
        game.fire('rehome', base)    
        base.rehome()

        return calculated_time

class ExitCommand(Command):
    command = "exit"
    description = """Exit the game."""
    time = 0
    def action(self, args, command_line):
        #game.state.killer = "Shadow Team"; gameprompt.death_screen();
        if gameprompt.confirm_exit():
            game.fire('shutdown')

class HelpCommand(Command):
    command = "help"
    description = """Print some help text"""
    time = 0
    def action(self, args, command_line):
        (options, args) = self.parse(args)
        if 'combat' in args:
            terminal.add_line("<WHITE>Combat Primer")
            terminal.add_line("<WHITE>--------------------------------------")
            terminal.add_line("<WHITE>Enemy<LIGHTGREY> players will try to hunt you down and destroy you.")
            terminal.add_line("They will do this by searching for and hacking into nodes they find you present in")
            terminal.add_line("and trying to <WHITE>Purge<LIGHTGREY> the node. If they purge your home node, you're")
            terminal.add_line("gone. If they purge a node you are connected through, your connection will be severed")
            terminal.add_line("and you will take damage from the shock.")
            terminal.add_line()
            terminal.add_line("You can, however, fight back. You can passively '<LIGHTGREEN>defend<LIGHTGREY>' a single node at")
            terminal.add_line("any time. Defended nodes cannot be purged; instead, the adversary must fight you in")
            terminal.add_line("<WHITE>Cybercombat<LIGHTGREY>. Additionally, you can '<LIGHTGREEN>attack<LIGHTGREY>' other users who are")
            terminal.add_line("logged into nodes, damaging them. During Cybercombat, you will likely take damage as well -")
            terminal.add_line("use the '<LIGHTGREEN>heal<LIGHTGREY>' command to repair yourself at the cost of time.")
        elif 'programs' in args:
            terminal.add_line("<WHITE>Programs")
            terminal.add_line("<WHITE>--------------------------------------")
            terminal.add_line("You will find various <WHITE>Programs<LIGHTGREY> during your exploration of the Net. There are")
            terminal.add_line("four types of program: <WHITE>Attack, Defend, Hacking, and Stealth<LIGHTGREY>. Sometimes enemies")
            terminal.add_line("defeated in cybercombat will have salveageable programs; you can also scan for them")
            terminal.add_line("on nodes with the '<LIGHTGREEN>dir<LIGHTGREY>' command. Higher ratings have greater chances of success")
        else:
            terminal.add_line("<WHITE>Commands:")
            terminal.add_line("<WHITE>--------------------------------------")
            for cmd in gameprompt.commands:
                if cmd.hide:
                    continue
                terminal.add_line("    <WHITE>%s" % cmd.command)
            terminal.add_line("Use '<LIGHTGREEN>command --help<LIGHTGREY>' for more info, or see subtopics at '<LIGHTGREEN>help combat<LIGHTGREY>' and '<LIGHTGREEN>help programs<LIGHTGREY>'")

class IPCommand(Command):
    arguments = "tunnel_id/node_ip/home"
    def action(self, args, command_line):
        (options, args) = self.parse(args)
        if not args or not len(args) == 1:
            self.parser.exit(help=True)
        arg = args[0]
        if 'home' in arg:
            node = game.state.home_node
        elif arg in nodes.ip_mapping:
            #ip
            node = nodes.ip_mapping[arg]
            if node not in game.state.tunnels and node != game.state.home_node:
                self.parser.error(msg="The Node IP must be one that you are connected to")
        elif '.' in arg:
            self.parser.error("The IP address must be valid")
        else:
            try:
                idx = int(arg) - 1
            except:
                self.parser.error(msg="A numeric tunnel ID is required")
            if idx == -1:
                node = game.state.home_node
            else:
                if idx >= len(game.state.tunnels):
                    self.parser.error(msg="A numeric ID that maps to a tunnel entry is required")
                node = game.state.tunnels[idx]
        return self.do_action(node)

class DefendCommand(IPCommand):
    command = "defend"
    description = "Defend a node against intruders logging in. You may only defend one node at a time."
    time = 5
    def do_action(self, node):
        terminal.add_line("You are now defending <GREEN>%s (%s)<LIGHTGREY>" % (node.name, node.ip_addr))
        game.state.defended_node = node
        return self.time

class AttackCommand(IPCommand):
    command = "attack"
    description = "Attack all intruders currently on a node."
    time = 10
    def do_action(self, node):
        if not node.npcs:
            terminal.add_line("There's nobody to attack!")
        for npc in node.npcs:
            npc.defend()
        return self.time


'''
    Parser bits
'''
@game.on('command')
def parse_command(command_line, match):
    if not command_line:
        return
    #it comes in as a list
    command_line = ''.join(command_line)
    
    splitted = command_line.split()
    if not len(splitted):
        return

    cmd, args = splitted[0], splitted[1:]
    if match is None:
        command = commands['_unknown']
    else:
        command = match

    terminal.add_line('<DARKGREY>%s' % hud.format_time(game.state.time))
    terminal.add_line('<DARKGREY>%s: <GREEN>%s' % (game.state.current_node.command_prompt, command_line))

    try:
        time_taken = command.action(args, command_line=command_line)
    except HelpError, e:
        terminal.add_line(e.msg)
    except CommandError, e:
        commands['_error'].action(e.msg, command_line)
    except game.GameShutdown:
            raise
    except Exception, e:
        terminal.add_line('<LIGHTRED>INTERNAL EXCEPTION: %s' % repr(e))
    else:
        game.take_time(time_taken)

    terminal.add_line(' ')
    terminal.scroll_to_end()

@game.on('specialkey')
def on_specialkey(key):
    if key == 'ctrlc':
        if gameprompt.confirm_exit():
            game.fire('shutdown')

commands = dict(
    ls=LSCommand('ls'),
    dir=LSCommand('dir'),
    neighbors=NeighborsCommand(),
    tunnel=TunnelCommand(),
    hack=HackCommand(),
    heal=HealCommand(),
    back=BackCommand(),
    rehome=ReHomeCommand(),
    exit=ExitCommand(),
    help=HelpCommand(),
    disarm=DisarmCommand(),
    defend=DefendCommand(),
    attack=AttackCommand(),
    programs=ProgramsCommand(),

    _unknown=UnknownCommand(),
    _error=ErrorCommand(),
)

gameprompt.commands.extend(
    [v for k,v in sorted(commands.items())]
)
