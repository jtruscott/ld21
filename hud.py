import draw
import constants as C
import WConio as W
import game
import logging
log = logging.getLogger('hud')

boxes = {}

def setup():
    topbar = draw.create_box(C.width, 3,
                            left = 0, top = 0,
                            interior_background_color = W.BLACK, draw_top=False)
    topbar.text.extend([
        draw.Text(W.WHITE, 5, 0, "Time: Day 0 + 1400"),
        draw.Text(W.WHITE, 5, 0, "Mission: 0", right_justify=True),
        ])
    boxes['topbar'] = topbar

    currentnode = draw.create_box(20, 10,
                            left = C.width - 20, top = 1,
                            interior_background_color = W.BLACK,
                            corners = {'tl': 'teedown', 'tr': 'teeleft'})
    currentnode.text.extend([
        draw.Text(W.MAGENTA, 2, 1, "CURRENT NODE:"),
        draw.Text(W.LIGHTMAGENTA, 2, 2, "[ Linksys 8829 ]"),
        draw.Text(W.MAGENTA, 3, 4,  "PROCESSOR: 1"),
        draw.Text(W.MAGENTA, 3, 5,  "STORAGE:   3"),
        draw.Text(W.MAGENTA, 3, 6,  "BANDWIDTH: 2"),
        draw.Text(W.MAGENTA, 3, 7,  "EXPOSURE: 1"),
        ])
    boxes['currentnode'] = currentnode

def draw_hud():
    log.debug('draw_hud')
    for box in (boxes['topbar'], boxes['currentnode']):
        draw.draw_box(box=box)
        draw.draw_box_text(box)
    
@game.on('tick')
def hud_tick():
    log.debug('hud_tick')
    draw_hud()
