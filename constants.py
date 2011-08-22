height = 64
width = 128

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
    half_box = chr(0xDD)
    box = chr(0xDB)

initial_msg = """
<WHITE>You are an AI, granted sentience by the winds of fate.

Your purpose is unclear.
You innately know how to use the programs built into your former existence.
You also know that you are being hunted.

<RED>A single thought drives you to act.
<LIGHTRED>ESCAPE!

-----------------------------------------------------------------------------

"""
help_msg = """
Welcome to the <WHITE>Net<LIGHTGREY>!
The Net is filled with nodes of varied types and attributes.
You will interact with it by entering <WHITE>commands<LIGHTGREY> into the console.

Your consciousness always resides in a single node at a time, designated
as your <WHITE>Home Node<LIGHTGREY>.

You can transfer to a different <WHITE>Home Node<LIGHTGREY> via
the '<LIGHTGREEN>rehome<LIGHTGREY>' command, but the process is very time-consuming.

Outside of your home node, you can <WHITE>Tunnel<LIGHTGREY> between connected nodes.
The '<LIGHTGREEN>neighbors<LIGHTGREY>' command allows you to view a node's connections.
By using the '<LIGHTGREEN>--scan<LIGHTGREY>' option,
you can probe those connections for statistics.

Most nodes on the Net, but not all, allow for anonymous connections
via the '<LIGHTGREEN>tunnel<LIGHTGREY>' command.

However, sometimes you want to do more than anonymous access permits.
For that, you need to <WHITE>Hack<LIGHTGREY> the target node.
Use the '<LIGHTGREEN>hack<LIGHTGREY>' command to gain <WHITE>root<LIGHTGREY> user access.
Nodes with a higher <WHITE>Security<LIGHTGREY> attribute will be more difficult to hack into.
Failed hacking attempts may trigger <WHITE>Alarms<LIGHTGREY>. (Those are <RED>bad<LIGHTGREY>)

Your existence begins in a laboratory.

"""

commlink_names = """Meta Link
CMT Clip
Sony Emperor
Renraku Sensei
Novatech Airware
Erika Elite
Hermes Ikon
Fairlight Caliban
Transys Avalon""".splitlines()

corp_names = ['Saeder-Krupp', 'Aztechnology', 'EVO Corp', 'Ares Macrotechnology',
                    'Horizon Entertainment', 'NeoNET', 'Renraku Computer Systems', 'Wuxing Inc']
nato_alphabet = 'Alpha Bravo Charlie Delta Echo Foxtrot Golf Hotel India Juliet Kilo Lima Mike November Oscar Papa Quebec Romeo Sierra Tango Uniform Victor Whiskey X-ray Yankee Zulu'.split()
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
olivinedeer
ludum
daresys
initech
skynet
""".splitlines()]
