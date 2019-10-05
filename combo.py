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
            self.value.append(['---'])

    



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
            self.val_model.append(['---'])
            tagcombo.set_active(len(model)-1)
            self.value.set_active(len(model)-1)
       

    def on_val_entry_focus_out(self,entry,event,combo):
        self.on_value_entered(entry,combo)
        return

    def on_value_entered(self,entry,combo):
        val = entry.get_text( )
        self.val_model = combo.get_model( )
        tag_val = self.tagbox.get_child( ).get_text( )
        n = self.tagbox.get_active( )
        if n == -1:
            self.val_model.append([val])
            self.value.set_active(len(self.val_model)-1)
            tag_model = self.tagbox.get_model( )
            tag_model.append([self.tagbox.get_child( ).get_text( )])
        else:
            self.val_model[n][0] = val
            self.value.set_active(n)
        self.tag_dict.update({ tag_val:val })
        print (self.tag_dict)
        return
         
    def on_value_changed(self, combo):
        itr = combo.get_active_iter( )
        val = combo.get_child( ).get_text( )

        if itr != None:
            n = combo.get_active( )
            self.tagbox.set_active(n)
        return

    def popup_both(self,widget):
        self.tagbox.popup( )
        self.value.popup( )


#       the first signals get eaten by one dropdown,
#       so they have to be repeated for both I guess.  <doh>
#    def popdown_left(self,widget):
#        self.tagbox.popdown( )
         

#    def popdown_right(self,widget):
#        self.value.popdown( )
        
        

    def set_header(self,header):
        self.header = header

    def on_item_chosen(self,item,entry):
        entry.set_text(item.get_label( ))

    def on_menu(self,entry,event):
        if event.button == 1:
            if (event.state & Gtk.accelerator_get_default_mod_mask( )) == Gdk.ModifierType.META_MASK:
                menu = Gtk.Menu( )
                try:
                    for line in self.header:
                        item = Gtk.MenuItem(line)
                        menu.append(item)
                        item.connect('activate',self.on_item_chosen,entry)
                except AttributeError:
                    return
                
                menu.show_all( )
                menu.popup(None,None,None,event,event.button,event.time)
                return False

    def add_to_popup(self,entry,popup):
        popup.append(Gtk.SeparatorMenuItem( ))

        if self.combo_entry.get_text( ) == 'genre':
            header = ['Rock','Blues','Jazz','Jam','Funk']
        else:
            try:
                header = self.header
            except:
                return
        try:
            for line in header:
                item = Gtk.MenuItem(line)
                popup.append(item)
                item.connect('activate',self.on_item_chosen,entry)
        except AttributeError:
            return
        popup.show_all( )


    def __init__(self):
        self.tagbox = Gtk.ComboBox.new_with_entry( )
        self.value = Gtk.ComboBox.new_with_entry( )
        self.tag_dict = { }
        self.tag_itrs = { }
        
        val_entry = self.value.get_child( )
        val_model = Gtk.ListStore(str)
        self.value.set_model(val_model)
        self.combo_model = Gtk.ListStore(str)
        self.tagbox.set_model(self.combo_model)
        val_entry.connect('activate',self.on_value_entered, self.value)
        tag_entry = self.tagbox.get_child( )
        tag_entry.connect('activate', self.on_combo_entered,self.tagbox)

#        val_entry.connect('button-press-event',self.on_menu)
        val_entry.connect('populate-popup',self.add_to_popup)
        val_entry.connect('focus-out-event',self.on_val_entry_focus_out,self.value)

        self.tagbox.set_entry_text_column(0)
        self.value.set_entry_text_column(0)

        self.hbox = Gtk.HBox( )
        self.hbox.set_size_request(-1,-1)
        self.tags = ['artist','album','date','year','genre','comment','venue']
        self.vals = ['---']*7
        
        for tag in self.tags:
            self.combo_model.append([tag])
        
        for val in self.vals:
            val_model.append([val])
#            val_model.append(['---'])

       
        button = Gtk.Button( )
        button.set_size_request(10,10)
        button.connect('clicked',self.popup_both)
#        button.connect('clicked',self.popdown_left)
#        button.connect('clicked',self.popdown_right)
        self.tagbox.set_size_request(-1,26)
        self.value.set_size_request(-1,26)
        self.tagbox.connect('changed',self.on_combo_changed)
        self.value.connect('changed', self.on_value_changed)
        self.hbox.pack_start(self.tagbox,True,True,2)
        
        self.hbox.pack_start(button,False,False,2)

        self.hbox.pack_start(self.value,True,True,2)
        self.val_model = val_model
        self.tagbox.set_active(0)
        self.combo_entry = self.tagbox.get_child( )

if __name__=='__main__':
    tc = TagCombo( )
    tc.win.show_all( )
    Gtk.main( )







