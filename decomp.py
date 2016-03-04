# Embedded file name: decomp.pyc
import sys
from struct import unpack
import os

class Stream:

    def __init__(self, string):
        self.string = string

    def read(self, n):
        s = self.string[:n]
        self.string = self.string[n:]
        return s

    def empty(self):
        return self.string == ''


def decomp_file(f):
    header = unpack('<I', f.read(4))[0]
    length = header >> 8
    firstbyte = header & 255
    if firstbyte != 16:
        print 'First byte error, note lzss encoded'
        raise IndexError
    decomp = ''
    while length > 0:
        d = ord(f.read(1))
        for i in range(8):
            if d & 128:
                r = map(ord, f.read(2))
                offset = ((r[0] & 15) << 8) + r[1]
                nlength = (r[0] >> 4) + 3
                start = len(decomp) - offset - 1
                for k in range(nlength):
                    decomp += decomp[start + k]
                    length -= 1
                    if length == 0:
                        break

            else:
                decomp = decomp + f.read(1)
                length -= 1
            d = d << 1
            if length == 0:
                break

    return decomp


def decomp_string(string):
    return decomp_file(Stream(string))


if __name__ == '__main__':
    f = file(sys.argv[1], 'rb')
    fo = file(sys.argv[2], 'wb')
    fo.write(decomp_file(f))
    fo.close()
    f.close()