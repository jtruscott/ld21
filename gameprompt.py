import game
import draw
import constants as C
import WConio as W
from winsound import MessageBeep
import string
import logging
log = logging.getLogger('gameprompt')
log.debug("asf")
class Command:
    def __init__(self, command, arguments, time, action):
        (self.command, self.arguments, self.time, self.action) = (command, arguments, time, action)
commands = [
    Command('ls', '[target_directory]', 1, None),
    Command('dir', '[target_directory]', 1, None),
    Command('things', '', 10, None),
    Command('other things', '', 100, None),
    Command('hats', '[style]', 1000, None),
    Command('hack', '[the] [gibson]', 10000, None),
]
old_matches = ''
def format_time(t):
    if t < 60:
        return '%is' % t
    if t < 3600:
        return '%im %is' % (t / 60, t % 60)
    if t < 86400:
        return '%ih %im %is' % (t / 3600, t / 60 % 60, t % 60)
    return '%id %ih %im %is' % (t / 86400, t / 3600 % 60, t / 60 % 60, t % 60)

def display_suggestion(msg):
    global old_matches
    matches = []
    if not msg or not msg.strip():
        if old_matches != matches:
            W.gotoxy(0, C.height - 2)
            W.clreol()
            old_matches = matches
        return
    msg = msg.split()[0]
    for command in commands:
        if command.command.startswith(msg):
            matches.append(command)
    if matches:
        #limit our match count
        matches = matches[:5]
        if old_matches != matches:
            old_matches = matches
            W.gotoxy(0, C.height - 2)
            W.clreol()
        
            targetwidth = C.width / len(matches)
            W.textcolor(W.DARKGREY)
            for command in matches:
                W.cputs(('%s (%s)' % (command.command, format_time(command.time))).center(targetwidth))
    return matches

def get_input():
    buf = []
    while True:
        msg = ''.join(buf)
        matches = display_suggestion(msg)

        W.gotoxy(0, C.height - 1)
        W.clreol()
        W.textcolor(W.GREEN)
        W.cputs('root@linksys$ '),
        W.textcolor(W.LIGHTGREEN)
        W.cputs(msg)

        if matches and len(matches) == 1:
            #show the argument help text
            match = matches[0]
            x = W.wherex()
            W.textcolor(W.DARKGREY)
            splitted = match.arguments.split()
            splitted = splitted[max(0, len(msg.split())-2):]
            W.cputs('  ' + ' '.join(splitted))
            W.textcolor(W.LIGHTGREEN)
            W.gotoxy(x, C.height - 1)

        
        #Read input
        W.setcursortype(1)
        (chn, chs) = W.getch()
        W.setcursortype(0)

        #figure out if we're done
        if chs == '\r':
            #enter, exit
            break

        if chn == 8: 
            #backspace
            if len(buf):
                buf.pop()
            else:
                MessageBeep()
            continue
        if chn == 0 or chn == 224:
            #special keys come in two parts
            (chn2, _) = W.getch()
            if chn2 in W.__keydict:
                game.fire('specialkey', W.__keydict[chn2])
            continue

        if len(buf) >= C.width:
            #way too long now
            break
        
        if chs not in string.printable:
            #dont care
            continue

        buf.append(chs)
    return buf

@game.on('clear')
def prompt_hbar():
    W.textcolor(W.WHITE)
    W.gotoxy(0, C.height-3)
    print C.Characters.box_single.horiz * C.width

@game.on('prompt')
def do_prompt():
    command = get_input()

   
