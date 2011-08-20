import WConio as W
import constants as C

import math
import re

import game
import draw
import logging
log = logging.getLogger('terminal')
class Line:
    colorRE = re.compile(r'([^<]*)<([\w]*)>')
    def __init__(self, buf, width):
        self.buf = buf
        self.width = width

    @classmethod
    def parse(self, raw_msg):
        items = filter(None, self.colorRE.split(raw_msg))
        lines = []
        color = [draw.color_char(W.LIGHTGREY)]
        xpos = [0]
        def make_line(item):
            if not item:
                #colors give None, for example
                return
            #make the new line
            #log.debug('making line %s', repr(item))
            buf = ''.join(['%s%s' % (a,b) for a,b in item])
            lines.append(Line(buf, len(item)))
            #clear our pos
            xpos[0] = 0

        def process(item, tmp_buf=None):
            if tmp_buf is None:
                tmp_buf = []

            #log.debug('item: %s', item)
            if hasattr(W, item):
                #it's a color
                color[0] = draw.color_char(getattr(W, item))
            else:
                #it's text, process it
                tmp_buf += [[c, color[0]] for c in item]
                xpos[0] += len(item)

            return tmp_buf

        p = None
        for i in items:
            p = process(i, p)
        make_line(p)

        return lines

class Terminal:
    top = 3
    left = 1
    width = (97 - 1)
    height = 54

    scroll_offset = 0
    buffer = []
    clearBuffer = ''
    initial_msg = """
Welcome to the game!
There will be some kind of <RED>DRAMATIC<LIGHTGREY> and possibly even <YELLOW>OMINOUS<LIGHTGREY> introduction here
before this is released. Hopefully. Maybe not.

Anywho, commands you run will find their output displayed here.
You can use up/down/home/end to scroll about.

There's a line over here, and it's incredibly long! whee-ooh-whee-ooh-whee-ooh-whee-ooh-whee-ooh-whee-ooh-whee-ooh
There's a line over here too, and it's incredibly long<MAGENTA>! whee-ooh-whee-ooh-whee-ooh-<BLUE>whee-ooh-whee-ooh-whee-ooh-whee-ooh
additionally

there
are
many
many
lines
and
you
can
keep
adding
more
and
see
what
happens

there
are
many
many
lines
and
you
can
keep
adding
more
and
see
what
happens

there
are
many
many
lines
and
you
can
keep
adding
more
and
see
what
happens

there
are
many
many
lines
and
you
can
keep
adding
more
and
see
what
happens
"""

class Scrollbar:
    arr = []
    pos = 0
    top = 2
    left = 98

def draw_terminal():
    y = Terminal.top
    W.puttext(Terminal.left, y, Terminal.left + Terminal.width -1, y + Terminal.height -1, Terminal.clear_buffer)

    for line in Terminal.buffer[Terminal.scroll_offset:Terminal.scroll_offset+Terminal.height]:
        W.puttext(Terminal.left, y, min(Terminal.width, Terminal.left + line.width - 1), y, line.buf)
        y += 1


def draw_scrollbar():
    buf = ''.join(['%s%s' % (a,b) for a,b in Scrollbar.arr])
    W.puttext(Scrollbar.left, Scrollbar.top, Scrollbar.left, Scrollbar.top + Terminal.height - 1, buf)

def update_scrollbar():
    Scrollbar.arr[Scrollbar.pos] = [C.Characters.scrollbar.vert,draw.color_char(W.DARKGREY)]
    scroll_pct = Terminal.scroll_offset / float(len(Terminal.buffer)-1)
    new_pos = int(math.ceil(scroll_pct * Terminal.height))
    new_pos = min(Terminal.height-1, max(0, new_pos))
    char = C.Characters.scrollbar.cross
    if new_pos == 0:
        char = C.Characters.scrollbar.top
    if new_pos == Terminal.height-1:
        char = C.Characters.scrollbar.bottom
    
    Scrollbar.arr[new_pos] = [char, draw.color_char(W.WHITE)]
    Scrollbar.pos = new_pos
    draw_scrollbar()

@game.on('setup')
def setup_terminal():
    initial = Terminal.initial_msg.splitlines()
    lines = []
    for line in initial:
        lines.extend(Line.parse(line))
    
    log.info(len(lines))
    Terminal.buffer = lines
    Terminal.clear_buffer = ''.join([' %s' % draw.color_char(W.BLACK)]*Terminal.height*Terminal.width)

    Scrollbar.arr = [[C.Characters.scrollbar.vert, draw.color_char(W.DARKGREY)]] * Terminal.height

@game.on('specialkey')
def on_specialkey(key):
    scrolled = False
    if 'up' in key:
        scrolled = True
        Terminal.scroll_offset -= 1
    elif 'down' in key:
        scrolled = True
        Terminal.scroll_offset += 1
    elif 'home' in key:
        scrolled = True
        Terminal.scroll_offset = 0
    elif 'end' in key:
        scrolled = True
        Terminal.scroll_offset = len(Terminal.buffer)
        
    if scrolled:
        Terminal.scroll_offset = max(0, min(len(Terminal.buffer)-1, Terminal.scroll_offset))
        update_scrollbar()
        draw_terminal()
    
@game.on('clear')
def on_clear():
    draw_terminal()
    update_scrollbar()

