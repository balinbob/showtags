#!/usr/bin/env python3

import re
import sys
import codecs

def detect_encoding(textfile):
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



def fnd(txtfile=None, ntitles=None):
    patterns = ['[ds]?[0-9]t?[0-9]{0,2}[.: ](?P<title>.*?)(\[.*\])?$']
    patterns.append('[ds]?[0-9]t?[0-9]{0,2}[.:\)\-\] ](?P<title>.*?)(\[.*\])?$')
    
    title_list = []
    e = detect_encoding(txtfile)

    with open(txtfile, 'r', encoding=e) as f:
        lines = f.readlines()
    for pattern in patterns:
        for line in lines:
            line = line.strip()
            if line.endswith('.wav') or \
                line.endswith('.flac') or \
                line.endswith('.shn'):
                    continue
            mo = re.match(pattern, line)
            if mo:
                line = mo.group('title').strip()
                # from shntool
                mo = re.search('\([0-9]{1,2} files\)', line)
                if mo:  continue
                # date
                mo = re.search('\d\d\-\d\d\-\d\d', line)
                if mo:  continue
                # duration
                line = re.sub('\d{1,3}\:\d{1,2}\.?\d{0,2}', '', line)
                if mo:  continue
                line = re.sub('^ ?[ds]\dt\d\d? ?', '', line)
                if line:
                    title_list.append(line.strip())

        if len(title_list) >= ntitles-2:
            break
    return title_list

if __name__ == '__main__':
    args = sys.argv
    fnd(args[1])
