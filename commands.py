import game
import gameprompt
import terminal
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

class Command:
    hide = False
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
            def exit(s, status=None, msg=None):
                if msg:
                    self.errors.append(msg)
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

        self.parser = Parser(prog=self.command)
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
    arguments = "[target_directory]"
    time = 5
    def add_options(self, p):
        p.add_option('-l', dest='long', action='store_true', help='Provide long listings')
        p.add_option('-a', dest='all', action='store_true', help='Show even hidden files')

    def action(self, args, command_line):
        (options, args) = self.parse(args)
        files = game.state.current_node.files
        terminal.add_line('<LIGHTGREY>      User     Type     Security  Filename')
        for file_name in files:
            terminal.add_line('      <DARKGREY>%s%s%s<WHITE>%s' % (
                'root'.ljust(9),
                'dir'.ljust(9),
                'none'.ljust(10),
                file_name
            ))

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
    else:
        game.take_time(time_taken)

    terminal.add_line(' ')
    terminal.scroll_to_end()

@game.on('specialkey')
def on_specialkey(key):
    if key == 'ctrlc':
        game.fire('shutdown')
commands = dict(
    ls=LSCommand('ls'),
    dir=LSCommand('dir'),
    things=Command('things', '', 10),
    other=Command('other things', '', 100),
    hats=Command('hats', '[style]', 1000),
    hack=Command('hack', '[the] [gibson]', 10000),
    
    _unknown=UnknownCommand(),
    _error=ErrorCommand(),
)

gameprompt.commands.extend(
    [v for k,v in sorted(commands.items())]
)
