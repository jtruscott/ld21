import game
import draw
import constants as C
import WConio as W
from winsound import MessageBeep
import string
import logging
import terminal
log = logging.getLogger('gameprompt')

commands = []
old_matches = ''
def format_time(t, tv=False):
    if tv:
        tv = '+'
    else:
        tv = ''
    if t < 60:
        return '%im %s' % (t, tv)
    if t < 3600:
        return '%ih %im %s' % (t / 60, t % 60, tv)
    if t < 86400:
        return '%id %ih %im %s' % (t / 3600, t / 60 % 60, t % 60, tv)

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
    for command in commands:
        if command.command.startswith(msg) and not command.hide:
            matches.append(command)
    if matches:
        #limit our match count
        matches = matches[:5]
        if old_matches != matches:
            old_matches = matches
            W.gotoxy(0, C.height - 2)
            W.clreol()
        
            targetwidth = C.width / len(matches)
            W.textcolor(W.DARKGREY)
            for command in matches:
                W.cputs(('%s (%s)' % (command.command, format_time(command.time, command.time_variable))).center(targetwidth))
    return matches

def get_input():
    buf = []
    while True:
        msg = ''.join(buf)
        matches = display_suggestion(msg)

        W.gotoxy(0, C.height - 1)
        W.clreol()
        W.textcolor(W.GREEN)
        W.cputs(game.state.current_node.command_prompt + '$ '),
        W.textcolor(W.LIGHTGREEN)
        W.cputs(msg)

        if matches and len(matches) == 1:
            #show the argument help text
            match = matches[0]
            x = W.wherex()
            W.textcolor(W.DARKGREY)
            splitted = match.arguments.split()
            splitted = splitted[max(0, len(msg.split())-2):]
            W.cputs('  ' + ' '.join(splitted))
            W.textcolor(W.LIGHTGREEN)
            W.gotoxy(x, C.height - 1)
        else:
            match = None
        
        #Read input
        W.setcursortype(1)
        (chn, chs) = W.getch()
        W.setcursortype(0)

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
        if chn == 3:
            log.debug('took a ctrl-c')
            game.fire('specialkey', 'ctrlc')
            break

        if chn == 0 or chn == 224:
            #special keys come in two parts
            (chn2, _) = W.getch()
            if chn2 in W.__keydict:
                game.fire('specialkey', W.__keydict[chn2])
            continue

        if len(buf) >= C.width:
            #way too long now
            break
        
        if chs not in string.printable:
            #dont care
            continue

        buf.append(chs)
    return buf, match

def show_confirmation(line1=' ', line2=' '):
    line1 = terminal.Line.parse(line1)[0]
    line2 = terminal.Line.parse(line2)[0]
    width = max(14, max(line1.width, line2.width) + 2)
    height = 8
    left = (C.width - width) / 2
    top = (C.height - height) / 2
    previous_buf = W.gettext(left, top, left + width, top + height)
    btn_width = 7
    btn_height = 4
    btn_offset = 3
    try:
        container = draw.draw_box(left, top, width, height,
                                    border_color=W.LIGHTBLUE, border_background_color = W.BLUE)
        W.puttext(left+1, top + 1, left + line1.width, top + 1, line1.buf)
        W.puttext(left+1, top + 2, left + line2.width, top + 2, line2.buf)

        yes_button = draw.draw_box(left + btn_offset, top + height - btn_height, btn_width, btn_height,
                                    border_color=W.LIGHTBLUE, border_background_color = W.BLUE,
                                    corners = {'bl': 'teeup', 'br': 'teeup'})

        no_button = draw.draw_box(left + width - btn_offset - btn_width, top + height - btn_height, btn_width, btn_height,
                                    border_color=W.LIGHTBLUE, border_background_color = W.BLUE,
                                    corners = {'bl': 'teeup', 'br': 'teeup'})

        yes_text = draw.Text(W.DARKGREY, 1, 1, "YES".center(btn_width -2 ))
        no_text = draw.Text(W.WHITE, 1, 1, "NO".center(btn_width -2 ))
        yes_button.text.append(yes_text)
        no_button.text.append(no_text)
        selected_button = no_button

        while True:
            if selected_button == yes_button:
                yes_text.color = W.WHITE
                no_text.color = W.DARKGREY
            else:
                no_text.color = W.WHITE
                yes_text.color = W.DARKGREY
            draw.draw_box_text(yes_button)
            draw.draw_box_text(no_button)
            (chn, chs) = W.getch()
            #figure out if we're done
            if chs == '\r':
                #enter, exit
                break
            if chs == 'y':
                selected_button = yes_button
                break

            if chs == 'n':
                selected_button = no_button
                break

            if chn == 0 or chn == 224:
                #special keys come in two parts
                (chn2, _) = W.getch()
                if chn2 in W.__keydict:
                    name = W.__keydict[chn2]
                    if 'left' in name or 'right' in name:
                        selected_button = (selected_button == yes_button and no_button or yes_button)

        return (selected_button == yes_button and True or False)

    finally:
        #Restore what we scribbled on
        W.puttext(left, top, left + width, top + height, previous_buf)


@game.on('clear')
def prompt_hbar():
    W.textcolor(W.WHITE)
    W.gotoxy(0, C.height-3)
    print C.Characters.box_single.horiz * C.width

@game.on('prompt')
def do_prompt():
    command_line, match = get_input()
    game.fire('command', command_line, match)
   
