import game
import draw
import constants as C
import WConio as W
from winsound import MessageBeep
import string
import logging
log = logging.getLogger('gameprompt')
log.debug("asf")
commands = [
    ('ls', 1, None),
    ('dir', 1, None),
    ('things', 10, None),
    ('other things', 100, None),
    ('hats', 1000, None),
    ('hack the gibson', 10000, None),
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
    for command, time, _ in commands:
        if command.startswith(msg):
            matches.append((command, time))
    if matches:
        #limit our match count
        matches = matches[:5]
        if old_matches != matches:
            old_matches = matches
            W.gotoxy(0, C.height - 2)
            W.clreol()
        
            targetwidth = C.width / len(matches)
            W.textcolor(W.DARKGREY)
            for command, time in matches:
                W.cputs(('%s (%s)' % (command, format_time(time))).center(targetwidth))
    return matches

def get_input():
    buf = []
    while True:
        msg = ''.join(buf)
        display_suggestion(msg)
        W.gotoxy(0, C.height - 1)
        W.clreol()
        W.textcolor(W.GREEN)
        W.cputs('root@linksys$ '),
        W.textcolor(W.LIGHTGREEN)
        W.cputs(msg)
        #Read characters and autocomplete
        (chn, chs) = W.getch()

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
            W.getch()
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

   
