import WConio as W
import constants as C
from collections import namedtuple
import game
import logging
log = logging.getLogger('draw')

Box = namedtuple('Box', 'width height left top buf text interior_background_color')

class Text:
    def __init__(self, color=W.WHITE, x=1, y=1, text = '', right_justify=False):
        (self.text, self.color, self.x, self.y, self.right_justify) = (text, color, x, y, right_justify)

@game.on('setup')
def setup():
    #setup the screen
    log.debug('setting up screen')
    import subprocess
    subprocess.call(['mode', 'con', 'lines=%i' % (C.height+1), 'cols=%i' % C.width], shell=True)
    W.textmode()

def color_char(fg=W.WHITE,bg=W.BLACK):
    return chr(fg + (bg << 4))

def create_box(width, height,
            left = None, top = None,
            boxtype=C.Characters.box_double,
            border_color=W.WHITE, border_background_color=W.BLACK,
            interior_color=W.WHITE, interior_background_color=W.BLACK, interior_char=' ',
            draw_top=True, draw_bottom=True,
            corners=None):
    #setup
    BC = color_char(border_color, border_background_color)
    BG = color_char(interior_color, interior_background_color)
    
    height_adj = int(draw_top) + int(draw_bottom)
    real_height = height - 2 + height_adj
    (tl, tr, bl, br) = (boxtype.tl, boxtype.tr, boxtype.bl, boxtype.br)
    if corners:
        if 'tl' in corners: tl = getattr(boxtype, corners['tl'])
        if 'tr' in corners: tr = getattr(boxtype, corners['tr'])
        if 'bl' in corners: bl = getattr(boxtype, corners['bl'])
        if 'br' in corners: br = getattr(boxtype, corners['br'])

    #Build up a buffer
    buf = []
    #draw the top
    if draw_top:
        buf.extend([tl, BC])
        buf.extend([boxtype.horiz, BC] * (width-2))
        buf.extend([tr, BC])

    #draw the sides
    for _ in range(real_height - height_adj):
        buf.extend([boxtype.vert, BC])
        buf.extend([interior_char, BG] * (width-2))
        buf.extend([boxtype.vert, BC])

    #draw the bottom
    if draw_bottom:
        buf.extend([bl, BC])
        buf.extend([boxtype.horiz, BC] * (width-2))
        buf.extend([br, BC])

    buf = ''.join(buf)
    return Box(width, real_height, left, top, buf, [], interior_background_color)

def draw_box(left=None, top=None, width=None, height=None,  box=None, **kwargs):
    if width is None and box:
        #box is a Box namedtuple
        width = box.width
        height = box.height
    if left is None and box:
        #and can also have positioning
        left = box.left
        top = box.top

    if box is None and width:
        #or you can just give w/h and let it make you one
        box = create_box(width, height, **kwargs)
    
    W.puttext(left, top, left+width-1, top+height-1, box.buf)
    return box

def draw_box_text(box):
    W.textbackground(box.interior_background_color)
    for line in box.text:
        W.textcolor(line.color)
        if line.right_justify:
            W.gotoxy(box.left + box.width - line.x - len(line.text), box.top + line.y)
        else:
            W.gotoxy(box.left + line.x, box.top + line.y)
        W.cputs(line.text)

def clear():
    W.clrscr()
    game.on('clear')

def put_at(x, y, msg, color=None):
    if color:
        W.textcolor(color)

    if len(msg) + x > C.width:
        log.debug('put_at: truncating %s by %i', msg, len(msg) + x - C.width)
        msg = msg[:C.width - x - 1]
    W.gotoxy(x, y)
    W.cputs(msg)
