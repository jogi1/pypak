#!/usr/bin/python -u
import sys
import array
import re
import os
import getopt
import struct


class PakHandler:
    def __init__(self, file):
        self.valid = True
        try:
            self.file = open(file, 'rb')
        except IOError:
            print('Error Opening file: ' + file)
            self.valid = False
        if not self.valid:
            return
        self.buffer = self.file.read()
        self.file.seek(0, 0)
        self.id = str(self.file.read(4))
        if self.id  != 'PACK':
            self.valid = False
            return
        dirofs = str(self.file.read(4))
        self.dirOffset = array.array('I', dirofs)[0]
        dirlen = str(self.file.read(4))
        self.dirLength = array.array('I', dirlen)[0]
        self.fileCount = self.dirLength/(56 +4 *2)
        self.files = []
        self.file.seek(self.dirOffset)
        for x in xrange(self.fileCount):
            file = {}
            file['name'] = ''
            cpos = self.file.tell()
            while True:
                s = self.file.read(1)
                if s == '\0':
                    break
                else:
                    file['name'] += s
            self.file.seek(cpos + 56, 0)
            file['position'] = struct.unpack('I', self.file.read(4))[0]
            file['length'] = struct.unpack('I', self.file.read(4))[0]
            self.files.append(file)

    def list(self, regexp = None):
        data = [['name', 'size']]
        if regexp:
            regexpc = re.compile(regexp)
        for file in self.files:
            if (regexp and regexpc.match(file['name'])) or regexp == None:
                data.append([file['name'], str(file['length']/1000.0) + 'kb'])
        col_width = max(len(word) for row in data for word in row) + 2  # padding
        for row in data:
            print "".join(word.ljust(col_width) for word in row)
        return

    def unpack(self, regexp = None):
        if regexp:
            regexpc = re.compile(regexp)
        lpath = ''
        print 'unpacking:'
        for file in self.files:
            if (regexp and regexpc.match(file['name'])) or regexp == None:
                print file['name']
                path = file['name'].rsplit('/', 1)
                if len(path) > 1 and not os.path.exists(path[0]):
                    try:
                        os.makedirs(path[0])
                    except:
                        print 'could not create path: ' + path[0]
                        return
                try:
                    f = open(file['name'], 'wb')
                except:
                    print 'could not open file: ' + file['name']
                    return
                self.file.seek(file['position'])
                f.write(self.file.read(file['length']))
                f.close()


def usage():
    print "pypak.py [OPTION] [FILE]"
    print "will without any options list all pak files"
    print "-u		 unpack all files"
    print "-r regex	 regular expression for listing and unpacking"

def handleArguments(arguments):
    options, args = getopt.getopt(arguments, 'hlur:')
    if len(args) == 0:
        usage()
        return
    regexp = None
    unpack = False
    for o, a in options:
        if o == '-u':
            unpack = True
        if o == '-r':
            regexp = a

    pfile = PakHandler(args[0])
    if unpack:
        pfile.unpack(regexp)
    else:
        pfile.list(regexp)
    return 

handleArguments(sys.argv[1:])
