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
    
commlink_names = """Meta Link
CMT Clip
Sony Emperor
Renraku Sensei
Novatech Airware
Erika Elite
Hermes Ikon
Fairlight Caliban
Transys Avalon""".splitlines()

company_names = [n.capitalize() for n in """zugia
fakia
xape
rocax
pemee
efiz
pekax
dijudda
cardinalpound
fuggih
youngrat
liftyards
upbass
ancientallegro
leccib
waterflash
naxoko
ozeh
vottof
ochreleopard
jazetu
apaf
panoramicgallon
xuhovi
nastydecimeter
jixxib
jukkoz
jegegu
zigux
overbaritone
rootduck
zitavi
ceaselesssnipe
ilec
olib
nuco
bibod
rapix
mixux
muvvur
excitedquart
adis
dikila
goodleopard
loraa
universedata
vizzeb
dibi
napsa
zopsi
bojoo
atuj
zexix
mogki
brightmillenium
bladefoot
Atomtheory
garrulouspower
deepsheep
goldstorage
endurablenote
fieldscanner
excitedfiction
brightdragon
decisivepython
olivinedeer""".splitlines()]
