#!/usr/bin/env python
# vim: set ft=python ts=4 sw=4 et ai:

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from gi.repository import Gdk
from gi.repository import Gio

import os,sys
from subprocess import check_output
from textview import TextBox
from tempfile import NamedTemporaryFile as NTF
import re
from mutagen import File
import mutagen

class TagCombo(object):
    

#    self.item_model = Gtk.ListStore(str)
#    self.value_model = Gtk.ListStore(str)
    
    def on_combo_changed(self,combo):
        itr = combo.get_active_iter( )
        if itr is not None:
            self.store = combo.get_model( )
            self.item = self.store[itr][0]
        else:
            entry = combo.get_child( )
            self.item = entry.get_text( )
        n = combo.get_active( )
        try:
            self.value.set_active(n)
        except:
            self.value.append(['<null>'])

    def on_combo_entered(self, entry,tagcombo):
        item = entry.get_text( )
        model = tagcombo.get_model( )
        tack_on = 1
        for n,row in enumerate(model):
            if item == row[0]:
                tagcombo.set_active(n)
                self.value.set_active(n)
                tack_on = 0
                break
        if tack_on:
            model.append([item])
            self.val_model.append(['<null>'])
            tagcombo.set_active(len(model)-1)
            self.value.set_active(len(model)-1)
       


    def on_value_entered(self,entry,combo):
        val = entry.get_text( )
    
        self.val_model = combo.get_model( )
        
        tag_val = self.tagbox.get_child( ).get_text( )
        

        n = self.tagbox.get_active( )
        print ('n is ', n)
        if n == -1:
            print ('self.val_model ',self.val_model)
            self.val_model.append([val])
            self.value.set_active(len(self.val_model)-1)
            tag_model = self.tagbox.get_model( )
            tag_model.append([self.tagbox.get_child( ).get_text( )])
        else:
            self.val_model[n][0] = val
            self.value.set_active(n)
        return
         



        itr = combo.get_active_iter( )
        if itr is None:
            itr = self.val_model.append([val])
            combo.set_active(len(self.val_model)-1)
       
        tag_model = self.tagbox.get_model( )
        tag_itr = self.tagbox.get_active_iter( )
        if tag_itr is not None:
            tag_val = self.tagbox[tag_itr][0]
        else:
            tag_entry = self.tagbox.get_child( )
            tag_val = tag_entry.get_text( )

        self.tag_dict.update({ tag_val:val })

        



    def on_value_changed(self, combo):
        itr = combo.get_active_iter( )
        if itr != None:
            n = combo.get_active( )
            self.tagbox.set_active(n)

        return



        entry = combo.get_child( )
        val = entry.get_text( )
        self.val_model = combo.get_model( )
        val_itr = combo.get_active_iter( )
        if val_itr is None:
            val_itr = self.val_model.append([val])
            combo.set_active(len(self.val_model)-1)
        
#        tag_entry = self.tagbox.get_child( )
#        tag_val = tag_entry.get_text( )
#        tag_model = self.tagbox.get_model( )
#        for n,row in enumerate(tag_model):
#            if tag_val == row[0]:
#                break
#            else:
#                continue
#        if tag_val != row[0]:
#            tag_model.append([tag_val])
#            self.tagbox.set_active(len(tag_model)-1)
#        else:
#            self.tagbox.set_active(n)
#        val_itr = combo.get_active_iter( )
#        print ('val_itr is ', val_itr)


    def __init__(self):
        self.tagbox = Gtk.ComboBox.new_with_entry( )
        self.value = Gtk.ComboBox.new_with_entry( )
        self.tag_dict = { }
        self.tag_itrs = { }
        
        val_entry = self.value.get_child( )
        val_model = Gtk.ListStore(str)
        self.value.set_model(val_model)
        self.model = Gtk.ListStore(str)
        self.tagbox.set_model(self.model)
        val_entry.connect('activate',self.on_value_entered, self.value)
        tag_entry = self.tagbox.get_child( )
        tag_entry.connect('activate', self.on_combo_entered,self.tagbox)

        self.tagbox.set_entry_text_column(0)
#        renderer = Gtk.CellRendererText( )
#        self.tagbox.pack_start(renderer,True)
#        self.tagbox.add_attribute(renderer,'text',0)

        self.value.set_entry_text_column(0)
#        renderer = Gtk.CellRendererText( )
#        self.value.pack_start(renderer,True)
#        self.value.add_attribute(renderer,'text',0)

        self.hbox = Gtk.HBox( )
        self.tags = ['artist','album','date','year','venue']
        self.vals = [None]*5
        
        for tag in self.tags:
            self.model.append([tag])
        
        for val in self.vals:
            val_model.append(['<null>'])

        self.tagbox.connect('changed',self.on_combo_changed)
        self.value.connect('changed', self.on_value_changed)
        self.hbox.pack_start(self.tagbox,False,False,2)
        self.hbox.pack_start(self.value,False,False,2)
        self.val_model = val_model
        self.tagbox.set_active(0)
        

if __name__=='__main__':
    tc = TagCombo( )
    tc.win.show_all( )
    Gtk.main( )







