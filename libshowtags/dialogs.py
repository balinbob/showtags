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
            fltr.add_pattern('*.ape')

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
        self.set_size_request(700, 500)

    def choose_folder(self, folder):
        if folder:
            self.set_current_folder(folder)
        resp = self.run()
        if resp == Gtk.ResponseType.OK:
            fn = self.get_filename()
            self.parent.flacs = [f for f in os.listdir(fn) \
                    if f.lower().endswith('.flac') or 
                    f.lower().endswith('.ape')]
            self.parent.flacs.sort()
            self.parent.showpath = fn
            print(self.parent.showpath)
        self.hide()

    def choose_txt(self, folder):
        if folder:
            self.set_current_folder(folder)
        resp = self.run()
        if resp == Gtk.ResponseType.OK:
            fn = self.get_filename()
            self.parent.text = [fn]
        else:
            self.parent.text = None
        self.hide()
