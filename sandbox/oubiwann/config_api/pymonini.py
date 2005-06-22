import os
from ConfigParser import SafeConfigParser as ConfigParser
from StringIO import StringIO

class StringFile(StringIO, object):
    '''
    >>> test_input = """
    ... line 1...
    ... line 2...
    ... line 3...
    ... """
    >>> f = StringFile()
    >>> f.write(test_input)
    >>> f.readline()
    ''
    >>> f.readline()
    'line 1...'
    >>> f.readline()
    'line 2...'
    '''
    def write(self, data):
        StringIO.write(self, data)
        self.lines = self.getvalue().split('\n')
    def readline(self):
        try:
            return self.lines.pop(0)
        except:
            return ''
    def readlines(self):
        return self.lines

class Levels(dict):
    '''
    >>> levels = ['a', 'b', 'c']
    >>> final_val = {'d': 'myval'}
    >>> l = Levels(levels, final_val)
    >>> l['a']['b']['c']['d']
    'myval'
    '''
    def __init__(self, items, final, firstRun=True):
        # 'items' is the list of sub-names that 
        # comprise the dotted config key
        if firstRun:
            items.reverse()
        while items:
            item = items.pop()
            data = Levels(items, final, firstRun=False)
            #print (item, final, data)
            #print 
            if data:
                value = data
            else:
                value = final
            self[item] = value

class IniConfig(dict):
    '''
    >>> ini_string = """
    ... [ system ]
    ... uid: pymon
    ... gid: pymon
    ... instance name: pymon test install
    ... 
    ... [ system > web ]
    ... port: 8080
    ... agent string: pymon Enterprise Monitoring (http://pymon.sf.net)
    ... 
    ... [ system > backups > state data ]
    ... interval: 300
    ... directory: data
    ... filename: backup.pkl
    ... """
    >>> 

    >>> f = StringFile()
    >>> f.write(ini_string)
    
    >>> cfg1 = IniConfig(f)
    >>> cfg1.source_type
    'StringFile'
    >>> cfg1.get('system').get('gid')
    'pymon'
    >>> cfg1.get('system').get('backups').get('state data').get('directory')
    'data'

    >>> cfg2 = IniConfig(ini_string)
    >>> cfg2.source_type
    'Raw string'

    '''
    def __init__(self, ini_source): 
        self.source = ini_source
        self.cfg = ConfigParser()
        self.parseSource()
        sections = self.cfg.sections()
        sections.sort(lambda x,y:  cmp(len(x), len(y)))
        for section in sections:
            levels = self.splitHeader(section)
            #print levels
            depth = len(levels)
            l = Levels(levels, dict(self.cfg.items(section)))
            k = l.keys()[0]
            v = l.values()[0]
            #print depth, k, v
            try:
                self.get(k).update(v)
            except:

                self.setdefault(k,v)

    def parseSource(self):
        self.source_type = None
        # check to see if it's a file-like object
        if isinstance(self.source, StringFile):
            # XXX this while-loop is a hack; for some reason
            # ConfigParser only reason one line per every read
            while self.source.lines:
                self.cfg.readfp(self.source)
                self.source_type = 'StringFile'
        elif isinstance(self.source, file):
            self.cfg.readfp(self.source)
            self.source_type = 'file handle'
        else:
            # check to see if it's a filename
            try:
                if os.path.isfile(self.source):
                    self.cfg.read([self.source])
                    self.source_type = 'filename'
            except TypeError:
                pass
            if not self.source_type:
                # check to see if it's a list of filenames
                if isinstance(self.source, list):
                    self.cfg.read(self.source)
                    self.source_type = 'list of filenames'
                # as a last resort, convert the string
                # to a file-like object
                else:
                    ini_file = StringFile()
                    ini_file.write(self.source)
                    # XXX this while-loop is a hack; for some reason
                    # ConfigParser only reason one line per every read
                    while ini_file.lines:
                        self.cfg.readfp(ini_file)
                    self.source_type = 'Raw string'
        if not self.source_type:
            raise 'Initilization Error: could not set source.'

    def splitHeader(self, header):
        levels = [ level.strip() for level in  header.split('>') ]
        return levels
        

def _test():
    import doctest, pymonini
    doctest.testmod(pymonini)

if __name__ == '__main__':
    _test()
