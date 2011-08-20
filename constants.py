height = 60
width = 120

#Box drawing characters for cp437
class Characters:
    class box_double:
        horiz = chr(0xCD)
        vert = chr(0xBA)
        tl = chr(0xC9)
        bl = chr(0xC8)
        tr = chr(0xBB)
        br = chr(0xBC)

        cross = chr(0xCE)
        teedown = chr(0xCB)
        teeleft = chr(0xB9)
        teeup = chr(0xCA)
        teeright = chr(0xCC)

    class box_single:
        horiz = chr(0xC4)

    class scrollbar:
        vert = chr(0xB3)
        cross = chr(0xD8)
        top = chr(0xD1)
        bottom = chr(0xCF)
    bullet = chr(0xF9)
