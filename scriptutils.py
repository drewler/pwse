# Embedded file name: scriptutils.pyc
import sys
from struct import unpack, pack
from decomp import decomp_file, Stream
import os
codes = {}
codes[0] = ('noop', 0, 'Does absolutely nothing.Note that in the script, this code is normally found only after pointerlabels (and indeed is *always* found after pointer labels).  Seeing itanywhere else likely indicates that a nearby control code swallowedtoo many or not enough arguments (due to an error in this file).')
codes[1] = ('b', 0, 'Linebreak.This switches from the top line to the bottom line within a textbox.  Withina fullscreen display (e.g. when asking a 2-option or 3-option question), itgoes down one line.  It is not used to change textbox: see <p> immediatelybelow and others for that.')
codes[2] = ('p', 0, 'Paragraph break.Switches to a new textbox, but requesting a keypress from the player(with the little moving arrow at the bottom-center of the box).  Notethat this is not the only way to change box (see later codes).')
codes[3] = ('color', 1, 'Shorthand: %0 = white           %1 = red           %2 = blue           %3 = greenChanges the color of the foreground text.Note that after using this code, it is always necessary to use it again soonafterwards to switch back to white, or your text will remain permanently thewrong color.')
codes[4] = ('pause', 0, 'Pause the game until a button is pressed.Note that this code is rarely used in the script.')
codes[5] = ('music', 2, 'Change music.')
codes[6] = ('sound', 2, 'Emit sound effect. ("bang!", "ding!", etc)')
codes[7] = ('fullscreen_text', 0, 'Switches to fullscreen display mode.Usually used in combination with the following codes:')
codes[8] = ('finger_choice_2args_jmp', 2, 'Uses the hand symbol to select an option out of 2.The arguments are pointers to where you jump in the script depending onthe option chosen.  Always preceded by <fullscreen_text> (thoughit may be some time ago) and followed by <endjmp>.')
codes[9] = ('finger_choice_3args_jmp', 3, 'Uses the hand symbol to select an option out of 3.Similar to above.')
codes[10] = ('rejmp', 1, 'Give address to jump to for multiple choice selections failed once. (I think)Always followed by <endjmp>.')
codes[11] = ('speed', 1, 'Shorthand: /2Adjust text speed.  arg from 0 to F: 0 is instantaneous, F is very slow.Note that because there are more letters in an English text than there arecharacters in an equivalent Japanese text, this will always need to be setmuch higher in the translation than it was in the original script.  Irecommend using speed 2 most of the time.')
codes[12] = ('wait', 1, 'Shorthand: =0e (two hexadecimal) digitsWait a specified number of time units.  Waits usually range between roughly08 and 20.  Very commonly found in the script.')
codes[13] = ('endjmp', 0, 'Terminator of a jump statement.This code must always appears immediately after any of the other jumpstatements.')
codes[14] = ('name', 1, 'Change the name that appears in the top left corner of the text box.E.g. katakana "Naruhodo"')
codes[15] = ('testimony_box', 2, 'Always appears at the beginning of a block of testimony.')
codes[16] = ('10', 1, '???')
codes[17] = ('evidence_window_plain', 0, 'Make the evidence window appear (without life bar).Same as if the player pressed the "R" button.')
codes[18] = ('bgcolor', 3, 'Shorthand: &0 to flash the screen (<bgcolor 301 8 1f>)Always takes arguments of the form: <bgcolor n0m j x>, where n is 1, 2, 3 or4, m is 1, 2, or 4, j is 0 or 1, x is 08 or 1f.By far the most common combination is <bgcolor 301 8 1f>, whichflashes the screen briefly.Changes the background color. Possibly does some other fancy graphical effects...')
codes[19] = ('showphoto', 1, 'Make the little evidence photo appear at the top left of the screen(complete with sound effect).')
codes[20] = ('removephoto', 0, 'Remove the photo that was put on the screen with the previous code(complete with sound effect).')
codes[21] = ('special_jmp', 0, 'Jump used at the end of testimony boxes, for savepoints and game resets.Always followed by <endjmp>.')
codes[22] = ('savegame', 0, 'Makes the save-game screen appear.')
codes[23] = ('newevidence', 1, "Files a new piece of evidence in the court records, as well as outputtingcorresponding sound effect and sliding picture.Low byte of arg: object to add.High byte of arg: 00: Material evidence, no sliding picture and no sound                  40: Material evidence, sliding picture and sound                  80: Person, no sliding picture and no sound                  c0: Person, sliding picture and soundWhen testing translated scripts by jmp'ing into the middle of them, you canput a bunch of these at the beginning of the script to make sure you haveenough evidence to go forward in the game without getting stuck.")
codes[24] = ('18', 1, 'Outputs "new evidence" sound effect (same sound as previous code), butappears to do nothing else that I\'ve been able to detect.')
codes[25] = ('19', 2, '???')
codes[26] = ('swoosh', 4, '"Swoosh"es the camera from one side of the courtroom to the other.Note that in the original script this is always followed by a <wait 1e>.')
codes[27] = ('bg', 1, 'Change background image.')
codes[28] = ('hidetextbox', 1, 'RG1-MAPPINGS:0=on,1=offMake the textbox appear or disappear.  0=appear, 1=disappear.Note that this has no effect on whether you can write text, onlywhether the border is seen.')
codes[29] = ('1D', 1, 'shift the background (left=1, right=257)')
codes[30] = ('person', 3, 'Change the graphic of the person appearing in the middle of the screen.')
codes[31] = ('hideperson', 0, 'Make the person in the middle of the screen instantly disappear.')
codes[32] = ('20', 1, '???')
codes[33] = ('evidence_window_lifebar', 0, 'Make the evidence window appear (with life bar).')
codes[34] = ('fademusic', 2, 'Fades down music.  First arg: usually 0, second arg: time it takesto fade down completely.')
codes[35] = ('23', 2, '???')
codes[36] = ('reset', 0, "Reset to game's title screen.This is intentional, it's not a crash side effect.  It's used forexample when you are declared guilty.")
codes[37] = ('25', 1, '???')
codes[38] = ('26', 1, 'Toggle court record button display (0=display,1=no display)')
codes[39] = ('shake', 2, 'Shorthand: *0 for <shake 1e 0>, *1 for <shake 1e 1>, *2 for <shake 1e 2>,            which are the three shakes always used.Shake the screen.First arg is length of shaking, the second the intensity.  Very common code.Note that no sound is associated with the shaking: that has to be doneby a separate control code.')
codes[40] = ('testimony_animation', 1, 'Large "shougen kaishi" animation, with a swoosh.Argument remains mysterious to me.')
codes[41] = ('29', 1, 'Returns from a failed answer in the allcases script to the part of thetestimony where the "tsukitsukeru" happened.  Argument seems to alwaysbe 2.')
codes[42] = ('2A', 3, '???Always followed by <endjmp>.')
codes[43] = ('2B', 0, '???')
codes[44] = ('jmp', 1, 'The most basic, unconditional jump.Argument is the pointer number to jump to.Always followed by <endjmp>.')
codes[45] = ('nextpage_button', 0, "Paragraph break.Identical to 02 (<p>)?  I haven't been able to tell the difference yet.")
codes[46] = ('nextpage_nobutton', 0, 'Paragraph break, without player button press required.')
codes[47] = ('animation', 2, 'Displays one of many sprite animations, such as "IGI-ARI!" (OBJECTION!)')
codes[48] = ('30', 1, '???')
codes[49] = ('personvanish', 2, 'Makes character at the middle of the screen disappear.Arguments are good for...?')
codes[50] = ('32', 2, '???')
codes[51] = ('33', 2, 'Some sort of jump function.  Followed by <endjmp>.')
codes[52] = ('fadetoblack', 1, 'Fades screen to complete black.Arg function?')
codes[53] = ('35', 2, '???')
codes[54] = ('36', 0, '???, weird, args?')
codes[55] = ('37', 2, '???')
codes[56] = ('38', 1, '???')
codes[57] = ('littlesprite', 1, 'Make appear the little sprite representing characters on map in case 4.  1arg: high byte determines object (0 = green circle with "me" (eye), 1 = bluecircle with "hi" (victim), etc).  May also be used for other things.')
codes[58] = ('3A', 2, '??? ')
codes[59] = ('3B', 2, '???')
codes[60] = ('3C', 1, '???')
codes[61] = ('3D', 1, '???')
codes[62] = ('3E', 1, '???')
codes[63] = ('3F', 0, 'Some sort of jmp.Always precedes <endjmp>')
codes[64] = ('40', 0, '???')
codes[65] = ('41', 0, '???')
codes[66] = ('soundtoggle', 1, 'RG1-MAPPINGS:0=on,1=offToggles the typewriter/voice sound of the text.  0=on, 1=off.')
codes[67] = ('lifebar', 1, 'Slide in lifebar, no evidence window.')
codes[68] = ('guilty', 1, '"yuuzai" (guilty) animation')
codes[69] = ('45', 0, 'Jmp at the end of special messages in the allcases script (such asthe save game screen messages).')
codes[70] = ('bgtile', 1, 'Appears to change all background tiles to the value of the argument.')
codes[71] = ('47', 2, '???')
codes[72] = ('48', 2, '???')
codes[73] = ('wingame', 0, 'Goes to title screen, having won the game (i.e. all case selects become open)')
codes[74] = ('4A', 0, '???, crash')
codes[75] = ('4B', 1, '???')
codes[76] = ('4C', 0, '???')
codes[77] = ('4D', 2, '???, not yet tested')
codes[78] = ('wait_noanim', 1, 'Wait for arg amount of time, freezing character animation.')
codes[79] = ('4F', 7, '???')
codes[80] = ('50', 1, '???')
codes[81] = ('51', 2, '???')
codes[82] = ('52', 1, '???')
codes[83] = ('53', 0, '???')
codes[84] = ('lifebarset', 2, 'Toggles various lifebar-related values.')
codes[85] = ('55', 2, '???, crash')
codes[86] = ('56', 2, '???')
codes[87] = ('psycholock', 1, 'Chains & psycho lock appearance animation.Argument indicates number and positioning of locks (1-6)')
codes[88] = ('58', 0, '???')
codes[89] = ('59', 1, '???')
codes[90] = ('5A', 1, '???')
codes[91] = ('5B', 2, '???')
codes[92] = ('5C', 0, '???, crash')
codes[93] = ('5D', 1, '???')
codes[94] = ('5E', 1, '???')
codes[95] = ('5F', 3, '???')
codes[96] = ('60', 0, '???, crash')
codes[97] = ('61', 3, '???')
codes[98] = ('62', 0, '???')
codes[99] = ('63', 0, '???, crash')
codes[100] = ('64', 1, 'Some kind of special effect (glass-shattering, white screen) - needsmore testing to see if it always does this.')
codes[101] = ('65', 2, '???')
codes[102] = ('66', 2, '???')
codes[103] = ('67', 0, '???')
codes[104] = ('68', 0, '???')
codes[105] = ('bganim', 2, 'Special fullscreen animation.')
codes[106] = ('switchscript', 1, 'Loads a new script block into RAM and jumps to the beginning of it(instantly and unnoticeably for the player, without a save screen oranything).  E.g. <switchscript 1> is used to switch from case1-2 tocase1-3.')
codes[107] = ('6B', 3, '???, not yet tested')
codes[108] = ('6C', 1, '???')
codes[109] = ('6D', 1, '???')
codes[110] = ('6E', 1, '???')
codes[111] = ('6F', 1, '???')
codes[112] = ('70', 3, '???')
codes[113] = ('71', 3, '???')
codes[114] = ('72', 0, '???')
codes[115] = ('73', 0, '???')
codes[116] = ('74', 0, '???, crash')
codes[117] = ('75', 0, '???, crash')
codes[118] = ('76', 0, '???, crash')
codes[119] = ('77', 0, '???, crash')
codes[120] = ('78', 0, '???, crash')
codes[121] = ('79', 0, '???, crash')
codes[122] = ('7A', 0, '???, reset to "Capcom" pre-title screen animation (crash?)')
codes[123] = ('7B', 0, '???, crash')
codes[124] = ('7C', 0, '???, crash')
codes[125] = ('7D', 0, '???, reset to "Capcom" pre-title screen animation (crash?)')
codes[126] = ('7E', 0, '???, crash')
codes[127] = ('7F', 0, '???, crash')
chars = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!?'
table = list(chars)
for i in range(len(table), 256):
    table.append('{' + str(i) + '}')

special = {225: '.',
 226: 'hand',
 227: 'jopen',
 228: 'jclose',
 229: '(',
 230: ')',
 231: 'jjopen',
 232: 'jjclose',
 233: 'open',
 234: 'close',
 235: 'downarrow',
 236: 'uparrow',
 237: ':',
 238: '`',
 239: ',',
 240: '+',
 241: '/',
 242: '*',
 243: "'",
 244: '-',
 245: 'littlecross',
 246: 'circle',
 247: '%',
 248: '\xa8',
 249: '~',
 250: '<<',
 251: '>>',
 252: '&',
 253: 'star',
 254: 'note',
 255: ' '}
for i in special:
    if len(special[i]) == 1:
        table[i] = special[i]
    else:
        table[i] = '{' + special[i] + '}'

def replace(s):
    if s > 128:
        if s < 384:
            return table[s - 128]
        else:
            return table[s - 128 & 255]
    else:
        return '.'


def preprocess(f):

    def getuntil(c, included = False):
        cc = f.read(1)
        s = ''
        while cc != c:
            s += cc
            cc = f.read(1)

        if included:
            s += cc
        return s

    glob = globals()
    script = ''
    c = f.read(1)
    while c != '':
        if c == '#':
            getuntil('\n')
        elif c == '@':
            cd = f.read(1)
            if cd == '@':
                code = getuntil('@')
                if f.read(1) != '@':
                    print 'Warning : exec bloc closed with a single @'
                    f.seek(f.tell() - 1)
                exec code in glob
            else:
                code = cd + getuntil('@')
                script += str(eval(code, glob))
        elif c != '\n':
            script += c
        c = f.read(1)

    return script


def convert_to_text(fnbin, fntext):
    f = file(fnbin, 'rb')
    fo = file(fntext, 'w')
    f.seek(0, 2)
    length = f.tell()
    f.seek(0)
    npointers = unpack('<I', f.read(4))[0]
    pointers = []
    for i in range(npointers):
        pointers.append(unpack('<I', f.read(4))[0])

    start = f.tell()
    shorts = []
    s = ''
    dec = 60
    while f.tell() < length - 2:
        if f.tell() in pointers:
            s += '\n[%d]' % pointers.index(f.tell())
        token = unpack('<H', f.read(2))[0]
        if token >= 128:
            if token < 384:
                c = table[token - 128]
            else:
                c = '{%d}' % token
        else:
            name, args, docs = codes[token]
            argsr = ''
            if args > 0:
                argsr = unpack('<' + 'H' * args, f.read(2 * args))
            if args == 0:
                c = '<%s>' % name
            elif args == 1:
                c = '<%s:%d>' % (name, argsr[0])
            else:
                c = '<%s:%s>' % (name, ','.join(map(str, argsr)))
        s += c
        if len(s) > dec:
            if s[-1] in ']>} ':
                fo.write(s + '\n')
                s = ''
            else:
                ns = ''
                while s[-1] not in ']>} ':
                    ns = s[-1] + ns
                    s = s[:-1]

                fo.write(s + '\n')
                s = ns

    fo.close()
    f.close()


def convert_to_binary(fntext, fnbin):
    f = file(fntext, 'r')
    script = preprocess(f)
    f.close()
    pointers = {}
    enc = ''
    while script != '':
        if script[0] == '<':
            i = 1
            while script[i] != '>':
                i += 1

            control = script[1:i]
            if ':' not in control:
                command = control
                args = []
            elif ',' not in control:
                command, arg = script[1:i].split(':')
                args = [arg]
            else:
                command, args = script[1:i].split(':')
                args = args.split(',')
            script = script[i + 1:]
            for k in codes:
                if codes[k][0] == command:
                    if len(args) == codes[k][1]:
                        enc += pack('<H', k)
                        for arg in args:
                            val = int(arg)
                            enc += pack('<H', val)

                    else:
                        print 'Error expecting %d args for command %s and got %d' % (codes[k][1], str(command), len(args))
                        raise IndexError
                    break

        elif script[0] == '[':
            i = 1
            while script[i] != ']':
                i += 1

            pointers[int(script[1:i])] = len(enc)
            script = script[i + 1:]
        elif script[0] == '{':
            i = 1
            while script[i] != '}':
                i += 1

            try:
                enc += pack('<H', 128 + table.index(script[:i + 1]))
            except ValueError:
                enc += pack('<H', int(script[1:i]))

            script = script[i + 1:]
        else:
            try:
                enc += pack('<H', 128 + table.index(script[0]))
            except ValueError:
                pass

            script = script[1:]

    npointers = len(pointers)
    fo = file(fnbin, 'wb')
    fo.write(pack('<I', npointers))
    plen = 4 + 4 * npointers
    for p in pointers:
        fo.write(pack('<I', plen + pointers[p]))

    fo.write(enc)
    fo.close()


if __name__ == '__main__':
    usage = sys.argv[0] + ' : '
    usage += 'ACTION [PARAMETERS]\nactions :\n -h : display commands basic help\n '
    usage += '-t script-binary script-text : convert to human readable text script-binary\n and'
    usage += ' store it in script-text\n -p script-text1 script-text2 : preprocess any '
    usage += 'python code found in \n script-text1 and output the result in script-text2\n '
    usage += '-b script-text script-binary : convert script to binary format\n'
    if len(sys.argv) <= 1:
        print usage
    elif sys.argv[1] == '-h':
        for ncode in codes:
            command, narg, doc = codes[ncode]
            print '[%X] ##<%s>## (%d args) : %s' % (ncode,
             command,
             narg,
             doc)

        print 'A lot of these doc is courtesy of http://comebackcourt.sourceforge.net/'
    elif sys.argv[1] == '-t':
        convert_to_text(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == '-p':
        f = file(sys.argv[2], 'r')
        fo = file(sys.argv[3], 'w')
        fo.write(preprocess(f))
        fo.close()
        f.close()
    elif sys.argv[1] == '-b':
        convert_to_binary(sys.argv[2], sys.argv[3])
    else:
        print usage
        print 'ERROR : wrong command invocation'