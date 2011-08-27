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

cc = constants.Characters
bd = constants.Characters.box_double
bs = constants.Characters.box_single
sb = constants.Characters.scrollbar

conversion = {
    #bd.horiz: ord('-'),
    #bd.vert: ord('|'),
    #bd.tl: ord('+'),
    #bd.bl: ord('+'),
    #bd.tr: ord('+'),
    #bd.br: ord('+'),
    #
    #bd.cross: ord('+'),
    #bd.teedown: ord('+'),
    #bd.teeleft: ord('+'),
    #bd.teeup: ord('+'),
    #bd.teeright: ord('+'),
    #
    #bs.horiz: ord('-'),
    #
    #sb.vert: ord('|'),
    #sb.cross: ord('+'),
    #sb.top: ord('-'),
    #sb.bottom: ord('-'),
    #
    #cc.bullet: ord('*'),
    #cc.half_box: ord('@'),
    #cc.box: ord('#'),
    #
    #179: ord('?'),
    #185: ord('?'),
    #186: ord('?'),
    #187: ord('?'),
    #188: ord('?'),
    #200: ord('?'),
    #201: ord('?'),
    #202: ord('?'),
    #203: ord('?'),
    #204: ord('?'),
    #205: ord('?'),
    #209: ord('?'),
    #221: ord('?'),

    179: ord('|'),
    185: ord('*'),
    186: ord('+'),
    187: ord('&'),
    188: ord('\\'),
    196: ord('='),
    200: ord('|'),
    201: ord('^'),
    202: ord('/'),
    203: ord('.'),
    204: ord(','),
    205: ord('-'),
    209: ord('%'),
    221: ord('#'),
}

def cursifychar(c):
    i = ord(c)
    j = conversion.get(i, i)
    if j < 32: raise Exception("got %r (%d)" % (c, i))
    if j > 126: raise Exception("got %r (%d)" % (c, i))
    return j

def cursifystr(s):
    return ''.join([chr(cursifychar(c)) for c in s])

def cursify(s):
    return [cursifychar(c) for c in s]

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
    log.debug('left=%r top=%r width=%r height=%r',left, top, width, height)
    #log.debug(repr(buf_text))
    while True:
        line = buf_text[row * width:(row + 1) * width]
        line2 = cursify(line)
        #log.debug("before(%i): %r", row, line)
        log.debug("after(%i):  %r", row, line2)
        row += 1
        line = line2
        for i in range(len(line)):
            W.addch(top+row, left+i, line[i], curses.A_BOLD | curses.color_pair(10))
        if row >= height:
            break
    W.noutrefresh()
    curses.doupdate() #xyz

def gotoxy(x, y):
    try:
        W.move(y, x)
    except:
        log.exception("x=%i,y=%i" % (x,y))
        raise

def cputs(msg):
    W.addstr(cursifystr(msg))
    W.noutrefresh()
    curses.doupdate() #xyz

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
