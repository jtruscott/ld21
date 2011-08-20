import draw
import constants as C
import WConio as W
import game
import logging
log = logging.getLogger('hud')

class boxes:
    #container
    pass

@game.on('setup')
def setup():
    boxes.topbar = draw.create_box(C.width, 3,
                            left = 0, top = 0,
                            interior_background_color = W.BLACK, draw_top=False)
    
    boxes.current_node = draw.create_box(20, 13,
                            left = C.width - 20, top = 1,
                            interior_background_color = W.BLACK,
                            corners = {'tl': 'teedown', 'tr': 'teeleft'})

@game.on('tick')
def topbar_tick():
    bar = boxes.topbar
    if not bar.text:
        bar.text.extend([
            draw.Text(W.WHITE, 5, 0, "Time: "),
            draw.Text(W.WHITE, 5, 0, "Mission: ", right_justify=True),
            ])
    timeText, missionText = bar.text
    timeText.text = "Time: Day %i %02i:%02i" % (game.state.time / 2400, game.state.time % 2400 / 100, game.state.time % 100)
    missionText.text = "Mission: %i" % (game.state.mission)
    
    draw.draw_box_text(bar)

@game.on('tick')
def nodebar_tick():
    bar = boxes.current_node
    data = game.state.current_node
    if not bar.text:
        bar.text.extend([
            draw.Text(W.MAGENTA, 2, 1, "CURRENT NODE:"),
            draw.Text(W.LIGHTMAGENTA, 2, 3, "[ name ]"),
            draw.Text(W.LIGHTMAGENTA, 2, 4, "ip"),
            draw.Text(W.MAGENTA, 3, 6,  "PROCESSOR:"),
            draw.Text(W.MAGENTA, 3, 7,  "STORAGE:"),
            draw.Text(W.MAGENTA, 3, 8,  "BANDWIDTH:"),
            draw.Text(W.MAGENTA, 3, 9,  "SECURITY:"),
            draw.Text(W.MAGENTA, 3, 10,  "EXPOSURE:"),
            draw.Text(W.LIGHTMAGENTA, 3, 6, "", right_justify=True),
            draw.Text(W.LIGHTMAGENTA, 3, 7, "", right_justify=True),
            draw.Text(W.LIGHTMAGENTA, 3, 8, "", right_justify=True),
            draw.Text(W.LIGHTMAGENTA, 3, 9, "", right_justify=True),
            draw.Text(W.LIGHTMAGENTA, 3, 10, "", right_justify=True),
            ])
    _, nameText, ipText, _, _, _, _, _, processorText, storageText, bandwidthText, securityText, exposureText = bar.text
    nameText.text = data.name.center(bar.width-4)
    ipText.text = data.ip_addr.center(bar.width-4)

    processorText.text = ' %i' % data.processor
    storageText.text = ' %i' % data.storage
    bandwidthText.text = ' %i' % data.bandwidth
    securityText.text = ' %i' % data.security
    exposureText.text = ' %i' % data.exposure
    
    draw.draw_box_text(bar)   

@game.on('clear')
def draw_hud():
    log.debug('draw_hud')
    for box in (boxes.topbar, boxes.current_node):
        draw.draw_box(box=box)
    
@game.on('tick')
def hud_tick():
    log.debug('hud_tick')
    #draw_hud()
