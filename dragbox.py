#!/usr/bin/python3

import gi
import sys
import magic
from urllib.parse import urlparse, unquote_plus
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GdkPixbuf
from gi.repository import GObject

target_entry = Gtk.TargetEntry.new('text/uri-list', 0, 0)
mime = magic.Magic(mime=True)

class MyWin(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self)
        self.connect('destroy', Gtk.main_quit)
        self.set_size_request(300, 300)
        self.dropimage = DropImage()
        self.add(self.dropimage.frame)
        # self.dropimage.connect('dropped', self.on_cover_dropped)
        self.show_all()
    
    # def on_cover_dropped(self, *args):
    #     return
    #     print('cover dropped!')
    #     if self.get_child():
    #         self.remove(self.get_child())
    #     self.add(self.dropimage)
    #     self.show_all()


class DropImage(Gtk.Image):
    def __init__(self):
        Gtk.Image.__init__(self)
        self.set_size_request(300, 300)
        self.frame = Gtk.Frame(label=' ->Drop Cover Art')
        self.frame.set_size_request(306, 306)
        self.frame.add(self)
        self.drag_dest_set(Gtk.DestDefaults.DROP, [target_entry], Gdk.DragAction.COPY)
        self.drag_dest_add_uri_targets()
        self.connect('drag-motion', self.on_drag_motion)
        self.connect('drag-drop', self.on_drag_drop)
        self.connect('drag-data-received', self.on_drag_data_received)
        
    @GObject.Signal(name='dropped',
                        flags=GObject.SignalFlags.RUN_LAST,
                        return_type=bool,
                        arg_types=(str,str),
                        accumulator=GObject.signal_accumulator_true_handled)
    def dropped(self, *args):
        return

    def on_drag_motion(self, widget, drag_context, x, y, time):
        Gdk.drag_status(drag_context, Gdk.DragAction.COPY, time)
        return True

    def on_drag_drop(self, widget, drag_context, x, y, data):
        return True

    def on_drag_data_received(self, widget, drag_context, x, y, data, info, time):        
        uri = data.get_uris()[0]
        self.filepath = unquote_plus(urlparse(uri).path)
        self.mime = mime.from_file(self.filepath)
        mime0, mime1 = self.mime.split('/')[0], self.mime.split('/')[1]
        # print(filepath)
        # print(m)
        if mime0 == 'image':
            self.pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
                    self.filepath,
                    300, 
                    -1, 
                    True)
            self.set_from_pixbuf(self.pixbuf)
        Gtk.drag_finish(drag_context, True, False, time)
        self.emit('dropped', self.mime, self.filepath)

    def set_pixbuf(self, pixbuf):
        self.set_from_pixbuf(pixbuf)

    def get_pixbuf(self):
        return self.pixbuf

    def get_filepath(self):
        return self.filepath

    def get_bytes(self):
        try:
            with open(self.filepath, 'rb') as f:
                self.bytes = f.read()
        except OSError:
            return None
        return self.bytes

def main():
    MyWin()
    Gtk.main()

if __name__ == '__main__':
    sys.exit(main())
