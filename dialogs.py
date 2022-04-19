#!/usr/bin/env python3

import sys, os, re
import gi
from importlib import import_module
gi.require_version('Gtk', '3.0')
Gtk = import_module('gi.repository.Gtk')
Gdk = import_module('gi.repository.Gdk')

class FileBrowser(Gtk.FileChooserDialog):
    def __init__(self, parent, title):
        self.parent = parent
        if title == 'Choose FLAC Folder':
            action = Gtk.FileChooserAction.SELECT_FOLDER
            fltr = Gtk.FileFilter()
            fltr.set_name('flac folder')
            fltr.add_mime_type('inode/directory')
            fltr.add_pattern('*.flac')

        elif title == 'Choose Text File':
            action = Gtk.FileChooserAction.OPEN
            fltr = Gtk.FileFilter()
            fltr.set_name('text file')
            fltr.add_mime_type('text/plain')

        Gtk.FileChooserDialog.__init__(self,
                                       title=title,
                                       parent=parent,
                                       action=action)
        self.set_filter(fltr)
        self.set_transient_for(parent)
        self.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL)
        self.add_buttons(Gtk.STOCK_OPEN, Gtk.ResponseType.OK)
        print('hey!')

    def choose_folder(self, folder):
        # resp = self.run()
        # dialog = FileBrowser('Choose FLAC Folder')
        if folder:
            self.set_current_folder(folder)
        self.set_size_request(800, 600)
        # self.set_transient_for(widget)
        resp = self.run()
        if resp == Gtk.ResponseType.OK:
            fn = self.get_filename()
            self.parent.flacs = [f for f in os.listdir(fn) \
                    if f.endswith('.flac')]
            self.parent.flacs.sort()
            self.parent.showpath = fn
            # folder = (self.parent.showpath, self.parent.flacs)
            print(self.parent.showpath)
        self.hide()

    def choose_txt(self, folder):
        if folder:
            self.set_current_folder(folder)
        resp = self.run()
#        dialog = FileBrowser('Choose Text File')
#        resp = dialog.run()
        if resp == Gtk.ResponseType.OK:
            fn = self.get_filename()
            self.parent.text = [fn]
        else:
            self.parent.text = None
        self.hide()
