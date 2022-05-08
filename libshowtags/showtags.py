#!/usr/bin/env python3
# vim: set ft=python ts=4 sw=4 et ai:

import os
import sys
import re
import codecs
from subprocess import check_output
from .textview import TextBox
from tempfile import NamedTemporaryFile as NTF
from mutagen import File, MutagenError, apev2
from mutagen.flac import Picture
from .dragbox import DropImage
from .combo import TagCombo
from .dialogs import FileBrowser
from .ftitles import fnd
import gi
from glob import glob
from importlib import import_module
gi.require_version('Gtk', '3.0')
Gtk = import_module('gi.repository.Gtk')
Gdk = import_module('gi.repository.Gdk')
GdkPixbuf = import_module('gi.repository.GdkPixbuf')
# from gi.repository import Gtk
# from gi.repository import Gdk

class MyWindow(Gtk.Window):
    rescan_flag = False
    showpath = ''
    flacs = ''
    folder = ''

    def removables_changed(self, entry, data=None):
        remove = entry.get_text()
        for row in self.model:
            row[2] = row[3]
            for ch in remove:
                val = row[2]
                if ch in val:
                    row[2] = val.replace(ch, '')

    def on_clear_btn(self, button, flac_btn):
        self.model.clear()
        self.tc.val_model.clear()
        self.tc.combo_model.clear()
        for tag in self.tc.tags:
            self.tc.combo_model.append([tag])
        for val in self.tc.vals:
            self.tc.val_model.append(['---'])

        flac_btn.set_sensitive(True)
        button.set_sensitive(False)
        self.text_button.set_sensitive(False)
        self.tagging.set_sensitive(False)
        self.rename_button.set_sensitive(False)
        self.vbox1.set_sensitive(False)

        for col in self.tagview.get_columns():
            self.tagview.remove_column(col)
            del col
        self.textbox.clear_text()

    def on_string_entry(self, entry):
        s = entry.get_text()
        for row in self.model:
            if s == '':
                row[2] = row[3]
            else:
                textline = row[2].replace(s, '')
                if textline and len(textline) < len(row[2]):
                    row[2] = textline
                else:
                    try:
                        textline = re.sub(s, '', row[2])
                    except:
                        continue
                    if textline != '' and len(textline) < len(row[2]):
                        row[2] = textline

    def check_form_complete(self):
        model = self.tagview.get_model()
        for row in model:
            if not row[0] or not row[2]:
                self.tagging.set_sensitive(False)
                self.rename_button.set_sensitive(False)
                print('form not complete!')
                return False
        self.tagging.set_sensitive(True)
        self.rename_button.set_sensitive(True)
        return True

    def on_rename(self, widget):
        print('renaming')

        pattern = self.rename_pattern.get_text()
        fnames = [row[0] for row in self.model]
        pathnames = [os.path.join(self.showpath, fname) for fname in fnames]

        for n, pname in enumerate(pathnames):
            s = check_output(['pytaggr',
                              '--noconfirm',
                              '--justify',
                              '--tag2fn',
                              pattern,
                              pname])
            s = s.decode()
            s = s.splitlines()[0]
            self.model[n][0] = s 
            print(s)
    
    def do_tagging(self, widget):
        print('tagging')
        
        picture = Picture()
        if self.coverart.filename:
            print(self.coverart.filename)
            picture.type = 3
            picture.mime = self.coverart.mime
            picture.data = self.coverart.get_bytes() 
        for row in self.model:
            print(row[0])
            fpath = os.path.join(os.path.realpath(self.showpath), row[0])
            track = row[1]
            title = row[2]
            if os.path.exists(fpath) and track and title:
                mf = File(fpath)
                try:
                    mf.add_tags()
                except (MutagenError, apev2.error):
                    pass
                mf['tracknumber'] = track
                mf['title'] = title
                # get each item from the  combo
                for item in self.tc.tag_dict:
                    val = self.tc.tag_dict[item]
                    # don't save unset tag items
                    if val != '---':
                        mf[item] = val
                    # delete tag keys set to null string
                    if val == '':
                        mf.pop(item)

                # a folder.jpg etc has been dropped
                if hasattr(picture, 'data') and len(picture.data) > 60:
                    mf.clear_pictures()
                    mf.add_picture(picture)
                mf.save()
        print('done')

    def choose_txt(self, widget, folder, data=None):
        self.textfile_chooser.choose_txt(folder)
        if self.text:
            self.load_text_file()


    def choose_folder(self, widget, folder=''):
        self.folder_chooser.choose_folder(folder)
        if self.flacs:
            self.load_files_into_listview()
    
    def __init__(self, argv):
        Gtk.Window.__init__(self, title='ShowTags')
        self.connect('destroy', Gtk.main_quit)
        
        cwd = os.getcwd()
        if sys.stdin.isatty():
            folder = ''
            files = glob(cwd + '/*.flac')
            files.extend(glob(cwd + '/*.ape'))
                
        if files:
            folder = cwd
        if len(argv) > 1:
            if os.path.isdir(argv[1]):
                folder = argv[1]
        self.folder = folder
        self.argv = argv

        self.mainbox = Gtk.VBox()
        self.mainbox.set_size_request(600, 220)
        self.tagview = TagView()
        self.coverart = CoverArt()
        self.coverbox = self.coverart.frame
        self.model = Model()
        self.tagview.set_model(self.model)

        self.scrlwindow = ScrollArea()
        self.scrlwindow.add(self.tagview)

        self.mainbox.pack_start(self.scrlwindow, True, True, 6)

        self.textfile_chooser = FileBrowser(self, 'Choose Text File')
        self.folder_chooser = FileBrowser(self, 'Choose FLAC Folder') 
        self.text_button = Gtk.Button(label='Text File')
        self.text_button.connect('clicked', 
                self.choose_txt,
                self.folder
                )

        self.flac_button = Gtk.Button(label='FLAC folder')
        self.flac_button.connect('clicked', 
                self.choose_folder, 
                self.folder
                )
        self.reload_button = Gtk.Button(label='Rescan')
        self.reload_button.connect('clicked', self.rescan)
        self.reload_button.set_tooltip_text('Rescan for titles from\n\
the text in the TextView')
        self.tagging = Gtk.Button(label='Tag')
        self.tagging.connect('clicked', self.do_tagging)
        self.tagging.set_sensitive(False)

        vbox1 = Gtk.VBox()
        vbox2 = Gtk.VBox()
        vbox3 = Gtk.VBox()
        vbox1.set_size_request(200, -1)
        vbox2.set_size_request(200, -1)
        vbox3.set_size_request(200, -1)
        grid = Gtk.Grid()
        grid.set_size_request(600, -1)
        vbox2.pack_start(self.flac_button, True, True, 0)
        vbox2.pack_start(self.text_button, True, True, 0)
        vbox2.pack_start(self.reload_button, True, True, 0)
        grid.attach(vbox1, 1, 1, 1, 2)
        grid.attach_next_to(vbox2, vbox1, Gtk.PositionType.RIGHT, 2, 2)
        grid.attach_next_to(vbox3, vbox2, Gtk.PositionType.RIGHT, 2, 2)
        self.text_button.set_sensitive(False)
        hbox = Gtk.HBox()
        hbox.pack_start(grid, False, False, 2)
        vbox1.pack_start(Gtk.Label(
                         label='Characters to Remove from All Titles'),
                         True,
                         True,
                         4)
        removables = Gtk.Entry()
        removables.set_size_request(-1, 22)
        removables.connect('changed', self.removables_changed)
        vbox1.pack_start(removables, False, True, 2)
        removables.set_tooltip_text('Type a string of single\n\
characters to remove\n\
from all titles in which they exist')
        self.removables = removables

        strings = Gtk.Entry()
        strings.set_size_request(-1, 20)
        strings.connect('activate', self.on_string_entry)
        strings.set_tooltip_text('Type any word or group of characters\n\
and press Return to remove them from all\n\
titles in which they exist.  This is\n\
checked for a RegExp.  Enter an empty\n\
string to reset')
        self.strings = strings

        vbox1.pack_start(Gtk.Label(label='Strings to Remove'), False, True, 4)
        vbox1.pack_start(strings, False, True, 0)
        vbox3.pack_start(self.tagging, False, True, 0)
        rename_button = Gtk.Button(label='Rename')
        rename_button.connect('clicked', self.on_rename)
        
        rename_button.set_sensitive(False)
        
        vbox3.pack_start(rename_button, False, False, 0)
        rename_pattern = Gtk.Entry()
        rename_pattern.set_text('%n %t.flac')
        rename_pattern.set_has_frame(True)
        rename_pattern.connect('focus-out-event', self.on_pattern_focus_out)
        vbox3.pack_start(rename_pattern, False, False, 0)
        self.rename_pattern = rename_pattern
        rename_pattern.set_tooltip_text('\
pattern by which tags will be\n\
translated into filenames:\n\
%n = tracknumber\n\
%t = title\n\
%a = artist\n\
%b = album\n\
%d = date')
        
        clearall_button = Gtk.Button(label='Clear All')
        clearall_button.connect('clicked', self.on_clear_btn, self.flac_button)
        vbox3.pack_start(clearall_button, False, True, 0)
        self.mainbox.pack_start(hbox, True, True, 0)
        self.retry = Gtk.Button(label='Try 2nd Method')
        self.retry.connect('clicked', self.on_retry)
        self.retry2 = Gtk.Button(label='Try 1st Method')
        self.retry2.connect('clicked', self.on_retry2)
        vbox2.pack_start(self.retry, False, True, 0)
        self.retry.set_sensitive(False)
        stack = Gtk.Stack()
        stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        stack.set_transition_duration(600)
        switcher = Gtk.StackSwitcher()
        switcher.set_size_request(-1, -1)

        switcher.set_stack(stack)

        self.textbox = TextBox()
        self.textbox.set_size_request(-1, -1)
        self.textbox.buffer.connect('changed', self.text_changed)
        stack.add_titled(self.mainbox, 'mainbox', 'Main')
        stack.add_titled(self.textbox, 'textbox', 'Text')
        stack.add_titled(self.coverbox, 'coverbox', 'Artwork')
        stack.connect('notify::visible-child', self.switched)
        vbox = Gtk.VBox()
        vbox.pack_start(switcher, False, False, 2)
        vbox.pack_start(stack, True, True, 0)
        self.add(vbox)
        self.stack = stack
        self.reload_button.set_sensitive(False)
        self.flac_button.set_sensitive(True)
        self.tc = TagCombo()
        vbox.pack_start(self.tc.hbox, False, False, 2)
        vbox1.set_sensitive(False)
        self.vbox1 = vbox1
        self.vbox2 = vbox2
        self.vbox3 = vbox3
        clearall_button.set_sensitive(False)
        rename_button.set_sensitive(False)
        self.clearall_button = clearall_button
        self.rename_button = rename_button
        self.method = 1

    def on_retry(self, widget):
        self.method = 2
        self.rescan()
        self.check_form_complete()
        self.vbox2.remove(self.retry)
        self.vbox2.pack_end(self.retry2, False, True, 0)
        self.retry2.show_all()

    def on_retry2(self, widget):
        self.method = 1
        self.rescan()
        self.check_form_complete()
        self.vbox2.remove(self.retry2)
        self.vbox2.pack_end(self.retry, False, True, 0)
        self.retry.show_all()

    def on_pattern_focus_out(self, widget, event):
        return False

    def text_changed(self, d1, d2=None):
        self.rescan_flag = True
        self.check_form_complete()

    def switched(self, data=None, data2=None):
        if self.rescan_flag:
            self.rescan_flag = False
            self.reload_button.set_sensitive(True)

    def rescan(self, data=None):
        buf = self.textbox.buffer

        text = buf.get_text(buf.get_start_iter(),
                            buf.get_end_iter(),
                            True)

        self.header = text.splitlines()[:6]
        self.tc.set_header(self.header)

        fp = NTF(mode='w', delete=True)
        fp.write(text)
        fp.flush()
        tf = TitleFinder(fp.name)
        if self.method == 1:
            self.titles = tf.find_titles(self.numfiles)
        else:
            self.titles = tf.find_titles2()

        col_len = len(self.model)
        for n in range(col_len):
            self.model[n][2] = ''
            self.model[n][3] = ''
        for n, title in enumerate(self.titles):
            try:
                self.model[n][2] = title
                self.model[n][3] = title
            except IndexError:
                if title:
                    s = str(n+1).zfill(2)
                    self.model.append(['', s, title, title])

        fp.close()
        self.reload_button.set_sensitive(False)

    def detect_encoding(self, textfile):
        encodings = ['utf-8', 'windows-1250', 'windows-1252', 'ISO-8859',
                     'latin1', 'latin2', 'ascii']
        for e in encodings:
            try:
                fh = codecs.open(textfile, 'r', encoding=e)
                fh.read()
                fh.seek(0)
            except UnicodeDecodeError:
                print('got unicode error with %s,\
                      trying different encoding' % e)
            else:
                break
        return (e)

    


    def load_text_file(self):
        tf = TitleFinder(self.text[0])
        self.titles = tf.find_titles(self.numfiles)
        columns = self.tagview.get_columns()
        columns[2].set_visible(True)
        columns[1].set_visible(True)
        for n, row in enumerate(self.model):
            self.model[n][2] = ''
            self.model[n][3] = '' 
        for n, title in enumerate(self.titles):
            title = re.sub('^\s*', '', title)
            title = re.sub('\s*$', '', title)
            try:
                self.model[n][2] = title
                self.model[n][3] = title
            except IndexError:
                if title:
                    s = str(n+1).zfill(2)
                    self.model.append(['', s, title, title])
        e = self.detect_encoding(self.text[0])
        with open(self.text[0], 'r', encoding=e) as txtfile:
            self.text = txtfile.read()

        self.header = self.text.splitlines()[:6]
        self.tc.set_header(self.header)

        self.textbox.buffer.set_text(self. text)
        self.check_form_complete()
        if self.titles:
            self.vbox1.set_sensitive(True)
        
    
    def load_files_into_listview(self):
        filename = Gtk.CellRendererText()
        title = Gtk.CellRendererText()
        number = Gtk.CellRendererText()
        
        title.set_property('editable', True)
        title.connect('edited', self.on_edited)
        col = Gtk.TreeViewColumn('filenames', filename, text=0)
        col.set_sort_column_id(0)
        self.tagview.append_column(col)
        col = Gtk.TreeViewColumn('track #', number, text=1)
        self.tagview.append_column(col)
        col = Gtk.TreeViewColumn('title', title, text=2)
        self.tagview.append_column(col)
        self.model = self.tagview.get_model()
        for n, flac in enumerate(self.flacs):
            if flac:
                s = str(n+1).zfill(2)
                self.model.append([flac, s, '', ''])
                print(flac)

        self.text_button.set_sensitive(True)
        self.flac_button.set_sensitive(False)
        self.clearall_button.set_sensitive(True)
        self.read_tags(self.flacs)

        self.check_form_complete()

        model = self.tagview.get_model()
        sel = self.tagview.get_selection()
        itr = model.get_iter_first()
        sel.select_iter(itr)
        self.tagview.on_changed(sel)
        self.numfiles = len(self.model)
        self.retry.set_sensitive(True)

    def on_edited(self, d1=None, path=None, newtext=None):
        self.model[path][2] = newtext
        self.check_form_complete()

    def read_tags(self, flacs=[]):
        if not flacs:
            return
        itr = self.model.get_iter_first()
        mfs = []
        for flac in flacs:
            f = os.path.join(os.path.realpath(self.showpath), flac)
            if os.path.isfile(f):
                mfs.append(File(f))
        
        for mf in mfs:
            title = mf.get('title', [None])
            num = [None]
            num = mf.get('tracknumber', [None])
            if num[0] and len(num[0]) < 3 and mf.get('discnumber'):
                if len(num[0]) < 2:
                    num[0] = mf['discnumber'][0] + '0' + num[0]
                else:
                    num[0] = mf['discnumber'][0] + num[0]
            if num[0] and len(num[0]) < 2:
                num[0] = num[0].zfill(2)
            if title[0]:
                self.model[itr][2] = mf['title'][0]
            if num[0]:
                self.model[itr][1] = num[0]
                # self.model[itr][1] = mf['tracknumber'][0]
            itr = self.model.iter_next(itr)
            self.setcover(mf)
        # dropdowns
        key_model = self.tc.tagbox.get_model()
        val_model = self.tc.value.get_model()
        tags = []
        for n, row in enumerate(key_model):
            val_model[n] = mf.get(row[0], ['---'])
            tags.append(key_model[n][0])
        tags.extend(['tracknumber', 'title'])
        for n, key in enumerate(mf.keys()):
            if key not in tags:
                key_model.append([key])
                val_model.append([mf[key][0]])

        self.rename_button.set_sensitive(True)
        # if form is complete set tag and rename available
        for row in self.model:
            if not row[0] or not row[2]:
                self.rename_button.set_sensitive(False)
                self.tagging.set_sensitive(False)

    def setcover(self, mf):
        self.coverart.set_flac(mf)


class CoverArt(DropImage):
    pixbuf = None
    first_image = None
    displayed = False
    homogenous = None
    filename = None

    def __init__(self, mf=None):
        DropImage.__init__(self)
        self.pixbuf = self.get_cover_from_flac(mf)
        self.connect('dropped', self.on_file_dropped)

    def on_file_dropped(self, widget, mime, fpath):
        self.mime = mime
        if mime == 'audio/flac':
            mf = File(fpath)
            if self.flac_has_picture(mf):
                self.set_flac(mf)
            else:
                self.clear()
        elif mime.split('/')[0] == 'image':
            self.pixbuf = self.get_pixbuf()
            print(type(self.pixbuf))
            self.pixbuf = self.pixbuf.scale_simple(
                    600, 
                    600, 
                    GdkPixbuf.InterpType.BILINEAR)
            self.set_from_pixbuf(self.pixbuf)
            # artwork that has a filename can be used to tag
            # artwork that came from a flac doesn't work yet
            self.filename = fpath

    def flac_has_picture(self, mf=None):
        if not mf:
            return False
        elif not hasattr(mf, 'pictures'):
            return False
        elif not mf.pictures:
            return False
        try:
            if len(self.mf.pictures[0]) > 20:   # arbitrary
                return True
        except AttributeError as e:
            return False
        finally:
            return True

    def set_flac(self, mf=None, itr=None):
        if not self.flac_has_picture(mf):
            return
        else:
            self.homogenous = self.are_all_the_same(mf)
            print(self.homogenous)
        if not self.homogenous:
            self.clear()
            self.first_image = None
            self.displayed = False
        if self.displayed:
            return
        else:
            self.pixbuf = self.get_cover_from_flac(mf)
            if not self.pixbuf:
                return
            self.pixbuf = self.pixbuf.scale_simple(
                    600, 
                    600, 
                    GdkPixbuf.InterpType.BILINEAR)
            print('setting')
            self.set_from_pixbuf(self.pixbuf)
            self.displayed = True

    def get_cover_from_flac(self, mf):
        if not mf:
            return None
        elif not mf.pictures:
            return None
        elif not len(mf.pictures[0].data):
            return None
        else:
            pic = mf.pictures[0]
            pbloader = GdkPixbuf.PixbufLoader()
            pbloader.write(pic.data)
            pbloader.close()
            pixbuf = pbloader.get_pixbuf()
            return pixbuf

    def are_all_the_same(self, mf):
        if not self.first_image:
            self.first_image = mf.pictures[0]
            return True
        elif mf.pictures[0] != self.first_image:
            return False
        else:
            return True


class ScrollArea(Gtk.ScrolledWindow):
    def __init__(self):
        Gtk.ScrolledWindow.__init__(self)
        self.set_size_request(400, 500)


class TagView(Gtk.TreeView):

    def __init__(self):
        self.tagvalues = Model()
        Gtk.TreeView.__init__(self, model=self.tagvalues)
        self.set_size_request(320, -1)
        self.limit = 99
        self.connect('button-press-event', self.on_tagview_clicked)
        self.connect('key-press-event', self.on_delete)
        
    def on_delete(self, tagview, event):
        # delete a whole row on DEL key
        if event.type == Gdk.EventType.KEY_PRESS and \
                        event.keyval == 0xffff:
            sel = self.get_selection()
            model, itr = sel.get_selected()
            if not itr:
                return
            model.remove(itr)
        self.get_toplevel().check_form_complete()

    def on_tagview_clicked(self, tagview, event):
        if event.type == Gdk.EventType.BUTTON_PRESS and \
                        event.button == 3:

            pthinfo = self.get_path_at_pos(event.x, event.y)
            path = pthinfo[0]
            self.get_selection().connect('changed', self.on_changed)
            if pthinfo is not None:
                path, col, cellx, celly = pthinfo
                self.grab_focus()
                self.set_cursor(path, col, 0)
            
            menu = Gtk.Menu()
            item = Gtk.MenuItem(label='Insert')
            item.connect('activate', self.on_insert)
            menu.append(item)
            item = Gtk.MenuItem(label='Remove')
            item.connect('activate', self.on_remove)
            menu.append(item)
            item = Gtk.MenuItem(label='Number all\nsequentially')
            item.connect('activate', self.on_sequential)
            menu.append(item)
            menu.show_all()
            menu.popup(None, None, None, None, event.button, event.time)

    def on_sequential(self, selection):
        for n, row in enumerate(self.get_model()):
            row[1] = str(n+1).zfill(2)

    def on_changed(self, sel):
        # print('on_changed')
        (model, itr) = sel.get_selected()
        self.sel = sel
        self.itr = itr
        self.vlist = []

    def on_insert(self, menuitem):
        # print('on_insert')
        self.sel = self.get_selection()
        model, self.sel_itr = self.sel.get_selected()
        itr = self.sel_itr
        vlist = self.vlist
        last = len(model)
        # model.append(['', str(last+1), '', ''])
        values = []
        while itr:
            values.append(model[itr][2])
            itr = model.iter_next(itr)
        itr = self.sel_itr
        model[itr][2] = ''
        itr = model.iter_next(itr)
        values.reverse()
        while itr and values:
            model[itr][2] = values.pop()
            itr = model.iter_next(itr)
        self.get_toplevel().check_form_complete()

    def on_remove(self, widget):
        print('on_remove')
        try:
            model, itr = self.sel.get_selected()
        except AttributeError:
            print('make a selection first!')
            return
        while True:
            nxt_iter = model.iter_next(itr)
            if not nxt_iter:
                break
            model[itr][2] = model[nxt_iter][2]
            itr = nxt_iter
        if not model.get_value(itr, 0):
            model.remove(itr)
        else:
            model[itr][2] = ''
        self.get_toplevel().check_form_complete()

class Model(Gtk.ListStore):
    def __init__(self):
        Gtk.ListStore.__init__(self, str, str, str, str)

class TitleFinder(object):
    def __init__(self, textfile_name):
        self.textfile = textfile_name
        self.titles = []
        self.pth = os.path.abspath(__file__)
        self.pth = os.path.join(os.path.split(self.pth)[0], 'find_titles')

    def find_titles(self, numfiles):
        # titles = check_output([self.pth, self.textfile])
        # title_list = titles.splitlines()
        self.titles = fnd(self.textfile, numfiles)
        return self.titles

    def find_titles2(self):
        self.titles = check_output([self.pth, self.textfile])
        self.titles = self.titles.splitlines()
        self.titles = [title.decode() for title in self.titles]
        return self.titles

def main():
    win = MyWindow(sys.argv)
    win.connect('destroy', Gtk.main_quit)
    win.show_all()
    Gtk.main()


if __name__=='__main__':
    sys.exit(main())
