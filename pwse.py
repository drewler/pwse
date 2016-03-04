# Embedded file name: pwse.py
import os
import pygtk
pygtk.require('2.0')
import gtk
import gobject
import sys
import dircache
import mesutils
import scriptutils
import os.path
import decomp
import imp
import tempfile
import zipfile
name = 'PWSE'
version = '0.2-alpha'
author = 'deufeufeu'
website = 'http://deufeufeu.free.fr'
date = '2007'

class unzip:

    def __init__(self, verbose = False, percent = 10):
        self.verbose = verbose
        self.percent = percent

    def extract(self, file, dir):
        if not dir.endswith(':') and not os.path.exists(dir):
            os.mkdir(dir)
        zf = zipfile.ZipFile(file)
        self._createstructure(file, dir)
        num_files = len(zf.namelist())
        percent = self.percent
        divisions = 100 / percent
        perc = int(num_files / divisions)
        for i, name in enumerate(zf.namelist()):
            if self.verbose == True:
                print 'Extracting %s' % name
            elif perc > 0 and i % perc == 0 and i > 0:
                complete = int(i / perc) * percent
                print '%s%% complete' % complete
            if not name.endswith('/'):
                outfile = open(os.path.join(dir, name), 'wb')
                outfile.write(zf.read(name))
                outfile.flush()
                outfile.close()

    def _createstructure(self, file, dir):
        self._makedirs(self._listdirs(file), dir)

    def _makedirs(self, directories, basedir):
        """ Create any directories that don't currently exist """
        for dir in directories:
            curdir = os.path.join(basedir, dir)
            if not os.path.exists(curdir):
                os.mkdir(curdir)

    def _listdirs(self, file):
        """ Grabs all the directories in the zip structure
        This is necessary to create the structure before trying
        to extract the file to it. """
        zf = zipfile.ZipFile(file)
        dirs = []
        for name in zf.namelist():
            if name.endswith('/'):
                dirs.append(name)

        dirs.sort()
        return dirs


def extract_mes(a):
    dlg = gtk.FileChooserDialog(title='Script archive to open', action=gtk.FILE_CHOOSER_ACTION_OPEN, buttons=(gtk.STOCK_CANCEL,
     gtk.RESPONSE_CANCEL,
     gtk.STOCK_OPEN,
     gtk.RESPONSE_OK))
    response = dlg.run()
    if response == gtk.RESPONSE_OK:
        archive = dlg.get_filename()
    else:
        dlg.destroy()
        return
    dlg.destroy()
    dlg = gtk.FileChooserDialog(title='Select a directory to extract scripts to', action=gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER, buttons=(gtk.STOCK_CANCEL,
     gtk.RESPONSE_CANCEL,
     gtk.STOCK_OPEN,
     gtk.RESPONSE_OK))
    response = dlg.run()
    if response == gtk.RESPONSE_OK:
        folder = dlg.get_filename()
    else:
        dlg.destroy()
        return
    dlg.destroy()
    mesutils.extract_mes(archive, folder)


def convert_to_text(a):
    dlg = gtk.FileChooserDialog(title='Script binary to open', action=gtk.FILE_CHOOSER_ACTION_OPEN, buttons=(gtk.STOCK_CANCEL,
     gtk.RESPONSE_CANCEL,
     gtk.STOCK_OPEN,
     gtk.RESPONSE_OK))
    response = dlg.run()
    if response == gtk.RESPONSE_OK:
        scriptbin = dlg.get_filename()
    else:
        dlg.destroy()
        return
    dlg.destroy()
    dlg = gtk.FileChooserDialog(title='Script text to save to', action=gtk.FILE_CHOOSER_ACTION_SAVE, buttons=(gtk.STOCK_CANCEL,
     gtk.RESPONSE_CANCEL,
     gtk.STOCK_OPEN,
     gtk.RESPONSE_OK))
    folder, f = os.path.split(scriptbin)
    dlg.set_current_folder(folder)
    dlg.set_current_name(f[:-4] + '.txt')
    response = dlg.run()
    if response == gtk.RESPONSE_OK:
        scripttext = dlg.get_filename()
    else:
        dlg.destroy()
        return
    dlg.destroy()
    if scripttext[-4:] != '.txt':
        scripttext += '.txt'
    tmp = scripttext[:-3] + 'dec'
    tmpf = file(tmp, 'wb')
    script = file(scriptbin, 'rb')
    tmpf.write(decomp.decomp_file(script))
    script.close()
    tmpf.close()
    scriptutils.convert_to_text(tmp, scripttext)
    os.remove(tmp)


def pack_mes(btn, l):
    dlg = gtk.FileChooserDialog(title='Select a directory of text script to compact as archive', action=gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER, buttons=(gtk.STOCK_CANCEL,
     gtk.RESPONSE_CANCEL,
     gtk.STOCK_OPEN,
     gtk.RESPONSE_OK))
    response = dlg.run()
    if response == gtk.RESPONSE_OK:
        folder = dlg.get_filename()
    else:
        dlg.destroy()
        return
    dlg.destroy()
    dlg = gtk.FileChooserDialog(title='Script archive to save to', action=gtk.FILE_CHOOSER_ACTION_SAVE, buttons=(gtk.STOCK_CANCEL,
     gtk.RESPONSE_CANCEL,
     gtk.STOCK_OPEN,
     gtk.RESPONSE_OK))
    dlg.set_current_name('mes_all.bin')
    response = dlg.run()
    if response == gtk.RESPONSE_OK:
        archive = dlg.get_filename()
    else:
        dlg.destroy()
        return
    dlg.destroy()
    mesutils.pack_mes_folder(archive, folder)


def rm_rf(path):
    if not os.path.isdir(path):
        return
    files = os.listdir(path)
    for x in files:
        fullpath = os.path.join(path, x)
        if os.path.isfile(fullpath):
            os.remove(fullpath)
        elif os.path.isdir(fullpath):
            rm_rf(fullpath)
            os.rmdir(fullpath)


def apply_modif(folder, pw2_rom, output_rom = '', verbose = True):
    os.environ['PATH'] += ';' + os.getcwd()
    f, pathname, descr = imp.find_module('config', [folder])
    config = imp.load_module('config', f, pathname, descr)
    f.close()
    if output_rom == '':
        output_rom = os.getcwd() + os.sep + config.rom_name + '.nds'
        dlg = gtk.FileChooserDialog(title='Save modified rom to', action=gtk.FILE_CHOOSER_ACTION_SAVE, buttons=(gtk.STOCK_CANCEL,
         gtk.RESPONSE_CANCEL,
         gtk.STOCK_OPEN,
         gtk.RESPONSE_OK))
        fold, rom = os.path.split(output_rom)
        dlg.set_current_folder(fold)
        dlg.set_current_name(rom)
        response = dlg.run()
        if response == gtk.RESPONSE_OK:
            output_rom = dlg.get_filename()
        else:
            dlg.destroy()
            return
        dlg.destroy()
    if verbose:
        dlg = gtk.Dialog(title='Applying modifications')
        lbl = gtk.Label()
        lbl.set_text('Applying : %s [%s] by %s\n' % (config.name, config.version, config.author))
        dlg.vbox.pack_start(lbl)
        dlg.show_all()
        dlg.present()

        def append_line(s):
            lbl.set_text(lbl.get_text() + s + '\n')
            dlg.queue_draw()
            while gtk.events_pending():
                gtk.main_iteration()

    sys.path.append(folder)
    tempdir = tempfile.mkdtemp()
    scriptsdir = tempdir + os.sep + 'scripts'
    os.mkdir(scriptsdir)
    if verbose:
        append_line('Creating temp directory')
    curpath = os.getcwd()
    if verbose:
        append_line('Extracting rom data')
    if 'winver' in dir(sys):
        ndstool = curpath + os.sep + 'ndstool'
    else:
        ndstool = 'ndstool'
    datadir = tempdir + os.sep + 'data'
    ndstool = '"' + ndstool + '"'
    command = 'temp.nds -9 arm9.bin -7 arm7.bin -y overlay ' + '-data data -h header.bin -t banner.bin ' + '-y7 y7.bin -y9 y9.bin'
    extract = ndstool + ' -x ' + command
    intract = ndstool + ' -c ' + command
    debug = file('debug.txt', 'w')
    debug.write('Running : ' + extract + '\n')
    debug.write('Running : ' + intract + '\n')
    debug.close()
    os.chdir(tempdir)

    def file_copy(fnin, fnout):
        fin = file(fnin, 'rb')
        fout = file(fnout, 'wb')
        fout.write(fin.read())
        fout.close()
        fin.close()

    file_copy(pw2_rom, 'temp.nds')
    os.system(extract)
    if verbose:
        append_line('Extracting scripts')
    os.chdir(curpath)
    mesutils.extract_mes(datadir + os.sep + 'mes_all.bin', scriptsdir)
    for script in config.scripts:
        n = config.scripts[script]
        f = file(folder + os.sep + script, 'r')
        fo = file(scriptsdir + os.sep + 'script-%02d.txt' % n, 'w')
        fo.write(f.read())
        f.close()
        fo.close()

    if verbose:
        append_line('Converting back scripts')
    os.chdir(curpath)
    mesutils.pack_mes_folder(datadir + os.sep + 'mes_all.bin', scriptsdir)
    if verbose:
        append_line('Building the new rom')
    os.chdir(tempdir)
    os.system(intract)
    file_copy('temp.nds', output_rom)
    if verbose:
        append_line('Cleaning up')
    rm_rf(tempdir)
    if verbose:
        dlg.destroy()
    os.chdir(curpath)


def apply_zip_modif(btn, pw2_rom):
    dlg = gtk.FileChooserDialog(title='Select the modification zip', action=gtk.FILE_CHOOSER_ACTION_OPEN, buttons=(gtk.STOCK_CANCEL,
     gtk.RESPONSE_CANCEL,
     gtk.STOCK_OPEN,
     gtk.RESPONSE_OK))
    response = dlg.run()
    if response == gtk.RESPONSE_OK:
        zipmodif = dlg.get_filename()
    else:
        dlg.destroy()
        return
    dlg.destroy()
    tdir = tempfile.mkdtemp()
    unzip().extract(zipmodif, tdir)
    apply_modif(tdir, pw2_rom)
    rm_rf(tdir)


def apply_folder_modif(btn, pw2_rom):
    dlg = gtk.FileChooserDialog(title='Select the modification folder', action=gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER, buttons=(gtk.STOCK_CANCEL,
     gtk.RESPONSE_CANCEL,
     gtk.STOCK_OPEN,
     gtk.RESPONSE_OK))
    response = dlg.run()
    if response == gtk.RESPONSE_OK:
        folder = dlg.get_filename()
    else:
        dlg.destroy()
        return
    dlg.destroy()
    apply_modif(folder, pw2_rom)


def select_rom():
    dlg = gtk.FileChooserDialog(title='Select Phoenix Wright 2 (US) rom', action=gtk.FILE_CHOOSER_ACTION_OPEN, buttons=(gtk.STOCK_CANCEL,
     gtk.RESPONSE_CANCEL,
     gtk.STOCK_OPEN,
     gtk.RESPONSE_OK))
    response = dlg.run()
    if response == gtk.RESPONSE_OK:
        rom_name = dlg.get_filename()
    else:
        dlg.destroy()
        return ''
    dlg.destroy()
    return rom_name


if __name__ == '__main__':

    def show_advanced_commands(btn, (vbox, advbox)):
        if btn.get_active():
            vbox.pack_end(advbox)
            vbox.reorder_child(advbox, -2)
        else:
            vbox.remove(advbox)
        vbox.show_all()
        vbox.queue_draw()


    if os.path.isfile('config.py'):
        f, pathname, descr = imp.find_module('config', ['.'])
        pwse_config = imp.load_module('config', f, pathname, descr)
        f.close()
    else:
        rom_name = select_rom().replace('\\', '\\\\')
        if rom_name == '':
            exit()
        f = file('config.py', 'w')
        f.write("pw2_rom = '" + rom_name + "'\n")
        f.close()
        f, pathname, descr = imp.find_module('config', ['.'])
        pwse_config = imp.load_module('config', f, pathname, descr)
        f.close()
    win = gtk.Window()
    win.set_title('%s [%s]' % (name, version))
    win.connect('delete-event', gtk.main_quit)
    vbox = gtk.VBox()
    advbox = gtk.VBox()
    advanced_commands = gtk.CheckButton('Show advanced commands')
    advanced_commands.connect('toggled', show_advanced_commands, (vbox, advbox))
    l = gtk.Label('%s [%s] by %s [%s] (%s)' % (name,
     version,
     author,
     website,
     date))
    extractmes = gtk.Button('Extract script archive to a folder')
    advbox.pack_start(extractmes)
    extractmes.connect('clicked', extract_mes)
    converttotext = gtk.Button('Convert binary script to text')
    advbox.pack_start(converttotext)
    converttotext.connect('clicked', convert_to_text)
    packmes = gtk.Button('Make a script archive from a folder')
    advbox.pack_start(packmes)
    packmes.connect('clicked', pack_mes, l)
    vbox.pack_start(gtk.Label('Apply modification :'))
    hbox = gtk.HBox()
    apply_zip_modif_btn = gtk.Button('From .zip')
    apply_zip_modif_btn.connect('clicked', apply_zip_modif, pwse_config.pw2_rom)
    hbox.pack_start(apply_zip_modif_btn)
    apply_folder_modif_btn = gtk.Button('From folder')
    apply_folder_modif_btn.connect('clicked', apply_folder_modif, pwse_config.pw2_rom)
    hbox.pack_start(apply_folder_modif_btn)
    vbox.pack_start(hbox)
    vbox.pack_start(gtk.HSeparator())
    vbox.pack_start(advanced_commands)
    vbox.pack_end(l)
    vbox.pack_end(gtk.HSeparator())
    win.add(vbox)
    win.show_all()
    gtk.main()