"""
    'XConio' module.
    drop-in replacement for WConio that wraps to curses.
"""
import sys
#hack ourselves into a new name
sys.modules['WConio'] = sys.modules['XConio']

import logging
log = logging.getLogger('XConio')
#predefined constants

BLACK = 0
BLUE = 1
GREEN = 2
CYAN = 3
RED = 4
MAGENTA = 5
BROWN = 6
LIGHTGRAY = LIGHTGREY = 7
DARKGRAY = DARKGREY = 8
LIGHTBLUE = 9
LIGHTGREEN = 10
LIGHTCYAN = 11
LIGHTRED = 12
LIGHTMAGENTA = 13
YELLOW = 14
WHITE = 15

#functions
import curses
import itertools

W = curses.initscr()
curses.start_color()

import constants
bd = constants.Characters.box_double
conversion = {
    bd.horiz: curses.ACS_HLINE
}
def cursify(s):
    ret = []
    for c in s:
        c = ord(c)
        if c in conversion:
            ret.append(conversion[c])
        else:
            ret.append(c)
    return ret

def textmode():
    textattr(LIGHTGRAY)
    clrscr()
    setcursortype(1)

def textcolor(c):
    bgcolor = gettextinfo()[4] & 0x00F0
    textattr(c | bgcolor)

def textbackground(c):
    fgcolor = gettextinfo()[4] & 0x000F
    textattr((c << 4) | fgcolor)

def gettextinfo():
    return [0]*5

def clreol():
    W.clrtoeol()
    curses.doupdate()

def clrscr():
    W.erase()
    curses.doupdate()

def textattr(color):
    pass

def setcursortype(i):
    curses.curs_set(i)

def settitle(title):
    sys.stdout.write("\x1b]2;%s\x07" % title)

def puttext(left, top, right, bottom, buf):
    gotoxy(left, top)
    width = right - left +1
    height = bottom - top +1
    buf_text = buf[::2]
    row = 0
    log.debug('l: %s, t: %s, w: %s h: %s',left, top, width, height)
    log.debug(buf_text)
    while True:
        line = buf_text[row*width:(row+1)*width]
        log.debug("%i; %s", row, cursify(line))
        row += 1
        line = cursify(line)
        for i in range(len(line)):
            W.addch(top+row, left+i, line[i], curses.A_BOLD | curses.color_pair(10))
        if row >= height:
            break
    curses.doupdate()
    import time
    time.sleep(1)
    raise Exception()

def gotoxy(x, y):
    try:
        W.move(y, x)
    except:
        log.exception("x=%i,y=%i" % (x,y))
        raise

def cputs(msg):
    W.addstr(msg)
    curses.doupdate()

def getch():
    return (3,3)

def gettext(left, right, top, bottom):
    return ''

def resize(h, w):
    y,x = W.getmaxyx()
    if y < h or x < w:
        raise Exception("Your window is x=%s, y=%s. Minimum required is x=%s, y=%s" % (x, y, w, h))
    curses.resizeterm(h, w)
    W.resize(h, w)
    curses.nocbreak()
    curses.echo()
