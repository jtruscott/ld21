import draw
import constants as C
import WConio as W
import game
import logging
log = logging.getLogger('hud')

class boxes:
    #container
    pass
def format_time(t):
     return 'Day %i, %02i:%02i' % (t / 2400, t % 2400 / 100, t % 100)

def draw_condition_bar(base):
    x, y = base.x + len(base.text), base.y
    hp, max_hp = game.player.hp, game.player.max_hp
    buf = []
    for i in range(1,max_hp+1):
        if hp >= i:
            color = draw.color_char(W.GREEN)
        else:
            color = draw.color_char(W.RED)
        buf.extend([C.Characters.half_box, color])

    buf = ''.join(buf)
    W.puttext(x, y, x+max_hp-1, y, buf)

@game.on('setup')
def setup():
    col_width = 26
    col_left = C.width - col_width

    boxes.topbar = draw.create_box(C.width, 3,
                            left = 0, top = 0,
                            interior_background_color = W.BLACK, draw_top=False)
    
    boxes.current_node = draw.create_box(col_width, 14,
                            left = col_left, top = 1,
                            interior_background_color = W.BLACK,
                            corners = {'tl': 'teedown', 'tr': 'teeleft'})

    boxes.home_node = draw.create_box(col_width, 14,
                            left = col_left, top = 14,
                            interior_background_color = W.BLACK,
                            corners = {'tl': 'teeright', 'tr': 'teeleft'})

    boxes.tunnel_list = draw.create_box(col_width, 33,
                            left = col_left, top = 27,
                            interior_background_color = W.BLACK,
                            corners = {'tl': 'teeright', 'tr': 'teeleft'})

@game.on('tick')
def topbar_tick():
    bar = boxes.topbar
    if not bar.text:
        bar.text.extend([
            draw.Text(W.WHITE, 5, 0, "Time: "),
            draw.Text(W.WHITE, 44, 0, "Condition: "),
            draw.Text(W.WHITE, 5, 0, "Mission: ", right_justify=True),
            ])
    timeText, conditionText, missionText = bar.text
    timeText.text = "Time: %s" % format_time(game.state.time)
    missionText.text = '' #"Mission: %i" % (game.state.mission)
    
    draw.draw_box_text(bar)
    draw_condition_bar(conditionText)

def draw_node_stats(bar, data, titleText = "CURRENT NODE:", highColor=W.YELLOW, lowColor=W.BROWN):
    if not bar.text:
        bar.text.extend([
            draw.Text(lowColor,  2, 2, titleText),
            draw.Text(highColor, 2, 4, "[ name ]"),
            draw.Text(highColor, 2, 5, "ip"),
            draw.Text(lowColor,  3, 7,  "PROCESSOR:"),
            draw.Text(lowColor,  3, 8,  "STORAGE:"),
            draw.Text(lowColor,  3, 9,  "BANDWIDTH:"),
            draw.Text(lowColor,  3, 10,  "SECURITY:"),
            draw.Text(lowColor,  3, 11,  "EXPOSURE:"),
            draw.Text(highColor, 3, 7, "", right_justify=True),
            draw.Text(highColor, 3, 8, "", right_justify=True),
            draw.Text(highColor, 3, 9, "", right_justify=True),
            draw.Text(highColor, 3, 10, "", right_justify=True),
            draw.Text(highColor, 3, 11, "", right_justify=True),
            ])
    _, nameText, ipText, _, _, _, _, _, processorText, storageText, bandwidthText, securityText, exposureText = bar.text
    nameText.text = data.name.center(bar.width-4)[:bar.width-4]
    ipText.text = data.ip_addr.center(bar.width-4)[:bar.width-4]

    processorText.text = ' %i' % data.processor
    storageText.text = ' %i' % data.storage
    bandwidthText.text = ' %i' % data.bandwidth
    securityText.text = ' %i' % data.security
    exposureText.text = ' %i' % data.exposure
    
    draw.draw_box_text(bar)   

def draw_tunnel_list(bar, data, highColor=W.YELLOW, lowColor=W.BROWN):
    draw.draw_box(box=bar)
    def draw_node(idx, node):
        max_width = bar.width - 4
        if idx is not None:
            name = "%i) %s" % (idx, node.name)
        else:
            name = "   %s" % node.name
        name = name[:max_width]
        texts.append(draw.Text(highColor,  2, y, name))
        texts.append(draw.Text(lowColor,  2, y+1, ("   %s" % node.ip_addr)[:max_width]))

    y = 4
    texts = [
        draw.Text(lowColor,  2, 2, "TUNNEL PATH:"),
    ]
    draw_node(None, game.state.home_node)
    y += 3
    start = max(0, len(data) - 7)
    i = start
    for node in data[start:]:
        i += 1
        draw_node(i, node)
        y += 3
    draw.draw_box_text(bar, text=texts)

@game.on('tick')
def nodebar_tick():
    draw_node_stats(boxes.current_node, game.state.current_node,
                    )
    draw_node_stats(boxes.home_node, game.state.home_node,
                    titleText = "HOME NODE:")

    draw_tunnel_list(boxes.tunnel_list, game.state.tunnels)

@game.on('clear')
def draw_hud():
    log.debug('draw_hud')
    for box in (boxes.topbar, boxes.current_node, boxes.home_node, boxes.tunnel_list):
        draw.draw_box(box=box)
    
@game.on('tick')
def hud_tick():
    log.debug('hud_tick')
    #draw_hud()
