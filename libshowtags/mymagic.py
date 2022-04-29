#!/usr/bin/python3
# magic wrapper
# MIT Kyechou
import magic as mgic

def magic(indata, mime=False):
    '''
    performs file magic while maintaining compatibility with
    different libraries
    '''
    try:
        if mime:
            mymagic = mgic.open(mgic.MAGIC_MIME_TYPE)
        else:
            mymagic = mgic.open(mgic.MAGIC_NONE)
        mymagic.load()
    except AttributeError:
        mymagic = mgic.Magic(mime)
        mymagic.file = mymagic.from_file
    return mymagic.file(indata)


