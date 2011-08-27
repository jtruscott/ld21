"""
    'XConio' module.
    drop-in replacement for WConio that wraps to curses.
"""
import sys
#hack ourselves into a new name
sys.modules['WConio'] = sys.modules['XConio']

import logging
log = logging.getLogger('XConio')
#log.setLevel(logging.DEBUG)
import curses
import constants
#predefined constants

#encode the bolditude in a bit curses coloring doesnt use, as a filthy hack
HACK_BOLD = 0x8

BLACK = curses.COLOR_BLACK
BLUE = curses.COLOR_BLUE
GREEN = curses.COLOR_GREEN
CYAN = curses.COLOR_CYAN
RED = curses.COLOR_RED
MAGENTA = curses.COLOR_MAGENTA
BROWN = curses.COLOR_YELLOW

LIGHTGRAY = LIGHTGREY = curses.COLOR_WHITE
DARKGRAY = DARKGREY = curses.COLOR_BLACK | HACK_BOLD
LIGHTBLUE = curses.COLOR_BLUE | HACK_BOLD
LIGHTGREEN = curses.COLOR_GREEN | HACK_BOLD
LIGHTCYAN = curses.COLOR_CYAN | HACK_BOLD
LIGHTRED = curses.COLOR_RED | HACK_BOLD
LIGHTMAGENTA = curses.COLOR_MAGENTA | HACK_BOLD
YELLOW = curses.COLOR_YELLOW | HACK_BOLD
WHITE = curses.COLOR_WHITE | HACK_BOLD


#functions
import itertools

W = curses.initscr()
curses.start_color()


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
    216: ord('+'),
    221: ord('#'),
}

input_conversion = {
    #newline
    '\n': '\r',
    #backspace
    chr(127): chr(8),
}

color_pairs = {
}
next_pair = 0
def color_attr(chr):
    global next_pair

    if isinstance(chr, basestring):
        byte = ord(chr)
    else:
        byte = chr

    #note: we don't use bg color atm
    _bg, fg = (byte & 0x00F0, byte & 0x000F)
    if fg not in color_pairs:
        log.debug("creating fg: %s", bin(fg))
            
        fgcolor, bold = (fg & 0x7, fg & 0x8)
        color = fgcolor
        next_pair += 1

        curses.init_pair(next_pair, color, curses.COLOR_BLACK)
        color_pair = curses.color_pair(next_pair)
        if bold:
            color_pair |= curses.A_BOLD
        
        color_pairs[fg] = color_pair
    return color_pairs[fg]

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

CURR_COLOR = -1
def textcolor(c):
    global CURR_COLOR
    CURR_COLOR = color_attr(c)

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
    buf_color = buf[1::2]
    row = 0
    #log.debug('left=%r top=%r width=%r height=%r',left, top, width, height)
    #log.debug(repr(buf_text))
    while True:
        line = buf_text[row * width:(row + 1) * width]
        line_color = buf_color[row * width:(row + 1) * width]
        line2 = cursify(line)
        #log.debug("before(%i): %r", row, line)
        #log.debug("after(%i):  %r", row, line2)
        row += 1
        line = line2
        for i in range(len(line)):
            W.addch(top+row, left+i, line[i], color_attr(line_color[i]))
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

def wherex():
    return W.getyx()[1]

def wherey():
    return W.getyx()[0]

def cputs(msg):
    W.addstr(cursifystr(msg), CURR_COLOR)
    W.noutrefresh()
    curses.doupdate() #xyz

__keydict = {
    #this was an ord-to-name translation table but the details dont matter. so make it ansi-key to name.
    'A': 'up',
    'B': 'down',
    'C': 'right',
    'D': 'left',
}
LOOKING_FOR_SPECIAL = False
def getch():
    global LOOKING_FOR_SPECIAL
    key = W.getkey()
    log.info("key: '%s' (%i)", key, ord(key))
    if LOOKING_FOR_SPECIAL:
        LOOKING_FOR_SPECIAL = False
        #parsing ansi is a goddamn pain
        buf = [key]
        while key in '0123456789;':
            key = W.getkey()
            log.info("key2: '%s' (%i)", key, ord(key))
            buf.append(key)
        key = ''.join(buf)
        log.info("returning special key value: '%s'", key)
        return (key, key)
        return 
    #normal key
    if key in [chr(27)]:
        #ansi escape gobbledeygook
        #swallow a [
        key = W.getkey()
        if key != chr(91):
            #wtf!?
            return (-1, '')
        
        LOOKING_FOR_SPECIAL = True
        return (0, '')

    if key in input_conversion:
        key = input_conversion[key]
        log.info("converted key: %s", key)
    if len(key) > 1:
        raise KeyboardInterrupt("key is %s" % key)
    return (ord(key), key)

def gettext(left, right, top, bottom):
    return ''

def resize(h, w):
    y,x = W.getmaxyx()
    if y < h or x < w:
        raise Exception("Your window is x=%s, y=%s. Minimum required is x=%s, y=%s" % (x, y, w, h))
    curses.resizeterm(h, w)
    W.resize(h, w)
    #curses.nocbreak()
    #curses.echo()
    W.keypad(False)
