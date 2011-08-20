import game
import draw
import constants as C
import WConio as W
import logging
log = logging.getLogger('gameprompt')
log.debug("asf")

@game.on('prompt')
def do_prompt():
    W.textcolor(W.WHITE)
    W.gotoxy(0, C.height-3)
    print C.Characters.box_single.horiz * C.width

    draw.put_at(0, C.height - 1, '> ')


