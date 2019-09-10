#!/usr/bin/env python
# vim: set ft=python ts=4 sw=4 et ai:

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
import os,sys


class TextBox(Gtk.ScrolledWindow):
    def __init__(self,fname=None):
        Gtk.ScrolledWindow.__init__(self)
        self.set_hexpand(True)
        self.set_vexpand(True)
        self.fname = fname

        self.textview = Gtk.TextView( )
        self.buffer = self.textview.get_buffer( )
        self.add(self.textview)
        

    def set_text(self):
        with open(self.fname) as txtfile:
            self.txt = txtfile.readlines( )
        self.buffer.set_text(self.txt)

    def clear_text(self):
        self.buffer.set_text('')

    def get_header(self):
        return (self.txt.splitlines( )[:6])
