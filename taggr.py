# vim: ts=4 sw=4 et:
import re
from os.path import sep

class Subster(object):
    def __init__(self,pattern='',mode='' ) :
        self.pattern = pattern or ''
        if mode == 'tag2fn':
            self.tag2fn = pattern or ''
        elif mode == 'fn2tag':
            self.fn2tag = pattern or ''
        self.mode = mode

        self.keydict =            { 'a':'artist',
                                    'l':'album',
                                    'n':'tracknumber',
                                    't':'title',
                                    'd':'date',
                                    'g':'genre',
                                    'c':'composer',
                                    'j':'junk',
                                    'i':'discnumber' }

        

        
        


        keystr  = ''.join( self.keydict.keys( ) )
        keypat  = '%['+ keystr +']'
        keypat  = re.compile( keypat )
#        self.keys  = re.findall( keypat,self.pattern )
        self.keys = [mp[1] for mp in re.findall(keypat,self.pattern)]
        self.lits  = re.split( keypat,self.pattern )

#        print self.keys

#        print self.lits

        
        




    def pathstrip( self, ptn, pth ) :
        n=len( ptn.strip(sep).split(sep) )
        pthlist=pth.strip(sep).split(sep)[-n:]
        return sep.join( pthlist )

    def _get_regex( self, reg, lit ) :
        if reg == 'n' :
            return ( '[0-9]+?'+lit )
        else:
            return ( '.+?'+lit )
    
    def init( self ) :
        self.keyiter  = iter( self.keys )
        self.literals = iter( self.lits )
        if self.lits[0] == '':
            literal = self.literals.next( )
        try:
            self.fname = self.fname[ len(literal): ]
        except AttributeError:
            pass
        except ValueError:
            raise ValueError

    def nextpair( self ) :
        try :
            key = self.keyiter.next( )
        except StopIteration :
            raise StopIteration
        try:
            lit = self.literals.next( )
        except StopIteration :
            lit = ''
        matchpat = self._get_regex( key, lit )
        mo = re.match( matchpat, self.fname )
        if mo:
            val = mo.group( )[ : -len( lit ) ]
            self.fname = self.fname[ len( lit+val ): ]
            keyname = self.keydict[ key ]
            return {keyname:val}
        else:
            raise ValueError
        
    def getdict( self,fname ):
        self.fname = self.pathstrip( self.pattern,fname )
        try:
            self.init( )
        except ValueError:
            return { }
        gdict = { }
        while True:
            try:
                gdict.update( self.nextpair( ) )
            except ValueError:
                return { }
            except StopIteration:
                break
        return gdict
   
    def getfnlist( self ):
        fnlist = []      
        self.keyiter  = iter( self.keys )
        self.literals = iter( self.lits )

        while True:
            try:
                fnlist.append( self.literals.next( ))
                fnlist.append( self.keydict[self.keyiter.next( )].lower( ) )
            except StopIteration:
                break
        return fnlist



