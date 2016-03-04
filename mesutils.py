# Embedded file name: mesutils.pyc
import sys
from struct import pack, unpack
import os
import dircache
import scriptutils

def aligned4(s):
    if s % 4 == 0:
        return s
    else:
        return s + (4 - s % 4)


def extract_mes(mes, folder, cmp_suffix = 'bin'):
    f = file(mes, 'rb')
    try:
        os.mkdir(folder)
    except:
        pass

    nfiles = unpack('<I', f.read(4))[0]
    files = []
    for i in range(nfiles):
        files.append(unpack('<II', f.read(8)))

    for i in range(nfiles):
        f.seek(files[i][0])
        comp = f.read(files[i][1])
        fo = file(folder + os.sep + 'script-%02d.%s' % (i, cmp_suffix), 'wb')
        fo.write(comp)
        fo.close()

    f.close()


def pack_mes(mes, filelist):
    fout = file(mes, 'wb')
    nfiles = len(filelist)
    startoff = 4 + 8 * nfiles
    fout.write(pack('<I', nfiles))
    off = startoff
    sizes = []
    for fn in filelist:
        f = file(fn, 'rb')
        f.seek(0, 2)
        size = f.tell()
        f.close()
        fout.write(pack('<II', off, size))
        off += aligned4(size)
        sizes.append(size)

    for i in range(len(filelist)):
        fout.write(file(filelist[i], 'rb').read())
        if sizes[i] % 4 != 0:
            fout.write('\x00' * (aligned4(sizes[i]) - sizes[i]))

    fout.close()


def pack_mes_folder(archive, folder):
    filelist = dircache.listdir(folder)
    d = os.getcwd()
    sys.path.append(folder)
    filestopack = []
    for f in filelist:
        ext = f[-3:]
        if ext == 'bin':
            if f[:-3] + 'txt' not in filelist:
                filestopack.append(folder + os.sep + f)
        elif ext == 'txt':
            nf = folder + os.sep + f
            scriptutils.convert_to_binary(nf, nf[:-3] + 'tmp')
            if 'winver' in dir(sys):
                gbalzss = '"' + d + os.sep + 'gbalzss"'
            else:
                gbalzss = 'gbalzss'
            os.system(gbalzss + ' ' + nf[:-3] + 'tmp ' + nf[:-3] + 'bin')
            os.remove(folder + os.sep + f[:-3] + 'tmp')
            filestopack.append(folder + os.sep + f[:-3] + 'bin')

    pack_mes(archive, filestopack)


if __name__ == '__main__':
    f = sys.argv[2]
    sys.path.append(os.getcwd() + os.sep + f)
    pack_mes_folder('..' + os.sep + sys.argv[1], f)