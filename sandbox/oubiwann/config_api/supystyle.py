import os
import md5
import sha 
import random
import time
import shutil
import UserDict
from itertools import ifilter
import string


class InsensitivePreservingDict(UserDict.DictMixin, object):

    def key(self, s):
        """Override this if you wish."""
        if s is not None:
            s = s.lower()
        return s

    def __init__(self, dict=None, key=None):
        if key is not None:
            self.key = key
        self.data = {}
        if dict is not None:
            self.update(dict)

    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__,
                           super(InsensitivePreservingDict, self).__repr__())

    def fromkeys(cls, keys, s=None, dict=None, key=None):
        d = cls(dict=dict, key=key)
        for key in keys:
            d[key] = s
        return d
    fromkeys = classmethod(fromkeys)

    def __getitem__(self, k):
        return self.data[self.key(k)][1]

    def __setitem__(self, k, v):
        self.data[self.key(k)] = (k, v)

    def __delitem__(self, k):
        del self.data[self.key(k)]

    def iteritems(self):
        return self.data.itervalues()

    def keys(self):
        L = []
        for (k, _) in self.iteritems():
            L.append(k)
        return L

    def __reduce__(self):
        return (self.__class__, (dict(self.data.values()),))

InsensitivePreservingDict = dict

def nonCommentLines(fd):
    for line in fd:
        if not line.startswith('#'):
            yield line

def nonEmptyLines(fd):
    return ifilter(str.strip, fd)
    
def nonCommentNonEmptyLines(fd):
    return nonEmptyLines(nonCommentLines(fd))

def mktemp(suffix=''):
    """Gives a decent random string, suitable for a filename."""
    r = random.Random()
    m = md5.md5(suffix)
    r.seed(time.time())
    s = str(r.getstate())
    period = random.random()
    now = start = time.time()
    while start + period < now:
        time.sleep() # Induce a context switch, if possible.
        now = time.time()
        m.update(str(random.random()))
        m.update(s)
        m.update(str(now))
        s = m.hexdigest()
    return sha.sha(s + str(time.time())).hexdigest() + suffix

class AtomicFile(file): 
    """Used for files that need to be atomically written -- i.e., if there's a
    failure, the original file remains, unmodified.  mode must be 'w' or 'wb'"""
    class default(object): # Holder for values.
        # Callables?
        tmpDir = None
        backupDir = None
        makeBackupIfSmaller = True
        allowEmptyOverwrite = True
    def __init__(self, filename, mode='w', allowEmptyOverwrite=None,
                 makeBackupIfSmaller=None, tmpDir=None, backupDir=None):
        if tmpDir is None: 
            tmpDir = '.'
        if backupDir is None:
            backupDir = '.'
        if makeBackupIfSmaller is None:
            makeBackupIfSmaller = '.'
        if allowEmptyOverwrite is None:
            allowEmptyOverwrite = '.'
        if mode not in ('w', 'wb'):
            raise ValueError, format('Invalid mode: %q', mode)
        self.rolledback = False
        self.allowEmptyOverwrite = allowEmptyOverwrite
        self.makeBackupIfSmaller = makeBackupIfSmaller
        self.filename = filename
        self.backupDir = backupDir
        if tmpDir is None:
            # If not given a tmpDir, we'll just put a random token on the end
            # of our filename and put it in the same directory.
            self.tempFilename = '%s.%s' % (self.filename, mktemp())
        else:
            # If given a tmpDir, we'll get the basename (just the filename, no
            # directory), put our random token on the end, and put it in tmpDir
            tempFilename = '%s.%s' % (os.path.basename(self.filename), mktemp())
            self.tempFilename = os.path.join(tmpDir, tempFilename)
        # This doesn't work because of the uncollectable garbage effect.
        # self.__parent = super(AtomicFile, self)
        super(AtomicFile, self).__init__(self.tempFilename, mode)

    def rollback(self):
        if not self.closed:
            super(AtomicFile, self).close()
            if os.path.exists(self.tempFilename):
                os.remove(self.tempFilename)
            self.rolledback = True
    def close(self):
        if not self.rolledback:
            super(AtomicFile, self).close()
            # We don't mind writing an empty file if the file we're overwriting
            # doesn't exist.
            newSize = os.path.getsize(self.tempFilename)
            originalExists = os.path.exists(self.filename)
            if newSize or self.allowEmptyOverwrite or not originalExists:
                if originalExists:
                    oldSize = os.path.getsize(self.filename)
                    if self.makeBackupIfSmaller and newSize < oldSize:
                        now = int(time.time())
                        backupFilename = '%s.backup.%s' % (self.filename, now)
                        if self.backupDir is not None:
                            backupFilename = os.path.basename(backupFilename)
                            backupFilename = os.path.join(self.backupDir,
                                                          backupFilename)
                        shutil.copy(self.filename, backupFilename)
                # We use shutil.move here instead of os.rename because
                # the latter doesn't work on Windows when self.filename
                # (the target) already exists.  shutil.move handles those
                # intricacies for us.

                # This raises IOError if we can't write to the file.  Since
                # in *nix, it only takes write perms to the *directory* to
                # rename a file (and shutil.move will use os.rename if
                # possible), we first check if we have the write permission
                # and only then do we write.
                fd = file(self.filename, 'a')
                fd.close()
                shutil.move(self.tempFilename, self.filename)

        else:
            raise ValueError, 'AtomicFile.close called after rollback.'

    def __del__(self):
        # We rollback because if we're deleted without being explicitly closed,
        # that's bad.  We really should log this here, but as of yet we've got
        # no logging facility in utils.  I've got some ideas for this, though.
        self.rollback()


class RegistryException(Exception):
    pass

class InvalidRegistryFile(RegistryException):
    pass

class InvalidRegistryName(RegistryException):
    pass

class InvalidRegistryValue(RegistryException):
    pass

class NonExistentRegistryEntry(RegistryException):
    pass

_cache = InsensitivePreservingDict()
_lastModified = 0

def open(filename, clear=False):
    """Initializes the module by loading the registry file into memory."""
    global _lastModified
    if clear:
        _cache.clear()
    _fd = file(filename)
    fd = nonCommentNonEmptyLines(_fd)
    acc = ''
    for line in fd:
        line = line.rstrip('\r\n')
        # XXX There should be some way to determine whether or not we're
        #     starting a new variable or not.  As it is, if there's a backslash
        #     at the end of every line in a variable, it won't be read, and
        #     worse, the error will pass silently.
        if line.endswith('\\'):
            acc += line[:-1]
            continue
        else:
            acc += line
        try:
            (key, value) = re.split(r'(?<!\\):', acc, 1)
            key = key.strip()
            value = value.strip()
            acc = ''
        except ValueError:
            raise InvalidRegistryFile, 'Error unpacking line %r' % acc
        _cache[key] = value
    _lastModified = time.time()
    _fd.close()

def close(registry, filename, private=True):
    first = True
    fd = AtomicFile(filename)
    for (name, value) in registry.getValues(getChildren=True):
        help = value.help()
        if help:
            lines = textwrap.wrap(value._help)
            for (i, line) in enumerate(lines):
                lines[i] = '# %s\n' % line
            lines.insert(0, '###\n')
            if first:
                first = False
            else:
                lines.insert(0, '\n')
            if hasattr(value, 'value'):
                if value._showDefault:
                    lines.append('#\n')
                    try:
                        x = value.__class__(value._default, value._help)
                    except Exception, e:
                        exception('Exception instantiating default for %s:',
                                  value._name)
                    try:
                        lines.append('# Default value: %s\n' % x)
                    except Exception, e:
                        exception('Exception printing default value of %s:',
                                  value._name)
            lines.append('###\n')
            fd.writelines(lines)
        if hasattr(value, 'value'): # This lets us print help for non-valued.
            try:
                if private or not value._private:
                    s = value.serialize()
                else:
                    s = 'CENSORED'
                fd.write('%s: %s\n' % (name, s))
            except Exception, e:
                exception('Exception printing value:')
    fd.close()

def normalizeWhitespace(s):
    """Normalizes the whitespace in a string; \s+ becomes one space."""
    return ' '.join(s.split())

def isValidRegistryName(name):
    # Now we can have . and : in names.  I'm still gonna call shenanigans on
    # anyone who tries to have spaces (though technically I can't see any
    # reason why it wouldn't work).  We also reserve all names starting with
    # underscores for internal use.
    return len(name.split()) == 1 and not name.startswith('_')

class Group(object):
    """A group; it doesn't hold a value unless handled by a subclass."""
    def __init__(self, help='', supplyDefault=False,
                 orderAlphabetically=False, private=False):
        self._help = normalizeWhitespace(help)
        self._name = 'unset'
        self._added = []
        self._children = InsensitivePreservingDict()
        self._lastModified = 0
        self._private = private
        self._supplyDefault = supplyDefault
        self._orderAlphabetically = orderAlphabetically
        OriginalClass = self.__class__
        class X(OriginalClass):
            """This class exists to differentiate those values that have
            been changed from their default from those that haven't."""
            def set(self, *args):
                self.__class__ = OriginalClass
                self.set(*args)
            def setValue(self, *args):
                self.__class__ = OriginalClass
                self.setValue(*args)
        self.X = X

    def __call__(self):
        raise ValueError, 'Groups have no value.'

    def __nonExistentEntry(self, attr):
        s = '%s is not a valid entry in %s' % (attr, self._name)
        raise NonExistentRegistryEntry, s

    def __makeChild(self, attr, s):
        v = self.__class__(self._default, self._help)
        v.set(s)
        v.__class__ = self.X
        v._supplyDefault = False
        v._help = '' # Clear this so it doesn't print a bazillion times.
        self.register(attr, v)
        return v
    def __getattr__(self, attr):
        if attr in self._children:
            return self._children[attr]
        elif self._supplyDefault:
            return self.__makeChild(attr, str(self))
        else:
            self.__nonExistentEntry(attr)

    def help(self):
        return self._help

    def get(self, attr):
        # Not getattr(self, attr) because some nodes might have groups that
        # are named the same as their methods.
        return self.__getattr__(attr)

    def setName(self, name):
        #print '***', name
        self._name = name
        if name in _cache and self._lastModified < _lastModified:
            #print '***>', _cache[name]
            self.set(_cache[name])
        if self._supplyDefault:
            for (k, v) in _cache.iteritems():
                if k.startswith(self._name):
                    rest = k[len(self._name)+1:] # +1 is for .
                    parts = split(rest)
                    if len(parts) == 1 and parts[0] == name:
                        try:
                            self.__makeChild(group, v)
                        except InvalidRegistryValue:
                            # It's probably supposed to be registered later.
                            pass

    def register(self, name, node=None):
        if not isValidRegistryName(name):
            raise InvalidRegistryName, name
        if node is None:
            node = Group()
        # We tried in any number of horrible ways to make it so that
        # re-registering something would work.  It doesn't, plain and simple.
        # For the longest time, we had an "Is this right?" comment here, but
        # from experience, we now know that it most definitely *is* right.
        if name not in self._children:
            self._children[name] = node
            self._added.append(name)
            names = split(self._name)
            names.append(name)
            fullname = join(names)
            node.setName(fullname)
        else:
            # We do this so the return value from here is at least useful;
            # otherwise, we're just returning a useless, unattached node
            # that's simply a waste of space.
            node = self._children[name]
        return node

    def unregister(self, name):
        try:
            node = self._children[name]
            del self._children[name]
            # We do this because we need to remove case-insensitively.
            name = name.lower()
            for elt in reversed(self._added):
                if elt.lower() == name:
                    self._added.remove(elt)
            if node._name in _cache:
                del _cache[node._name]
            return node
        except KeyError:
            self.__nonExistentEntry(name)

    def rename(self, old, new):
        node = self.unregister(old)
        self.register(new, node)

    def getValues(self, getChildren=False, fullNames=True):
        L = []
        if self._orderAlphabetically:
            self._added.sort()
        for name in self._added:
            node = self._children[name]
            if hasattr(node, 'value') or hasattr(node, 'help'):
                if node.__class__ is not self.X:
                    L.append((node._name, node))
            if getChildren:
                L.extend(node.getValues(getChildren, fullNames))
        if not fullNames:
            L = [(split(s)[-1], node) for (s, node) in L]
        return L


class Value(Group):
    """Invalid registry value.  If you're getting this message, report it,
    because we forgot to put a proper help string here."""
    def __init__(self, default, help, setDefault=True,
                 showDefault=True, **kwargs):
        self.__parent = super(Value, self)
        self.__parent.__init__(help, **kwargs)
        self._default = default
        self._showDefault = showDefault
        self._help = normalizeWhitespace(help.strip())
        if setDefault:
            self.setValue(default)

    def error(self):
        if self.__doc__:
            s = self.__doc__
        else:
            s = """%s has no docstring.  If you're getting this message,
            report it, because we forgot to put a proper help string here."""%\
            self._name
        e = InvalidRegistryValue(normalizeWhitespace(s))
        e.value = self
        raise e

    def setName(self, *args):
        if self._name == 'unset':
            self._lastModified = 0
        self.__parent.setName(*args)
        self._lastModified = time.time()

    def set(self, s):
        """Override this with a function to convert a string to whatever type
        you want, and call self.setValue to set the value."""
        self.setValue(s)

    def setValue(self, v):
        """Check conditions on the actual value type here.  I.e., if you're a
        IntegerLessThanOneHundred (all your values must be integers less than
        100) convert to an integer in set() and check that the integer is less
        than 100 in this method.  You *must* call this parent method in your
        own setValue."""
        self._lastModified = time.time()
        self.value = v
        if self._supplyDefault:
            for (name, v) in self._children.items():
                if v.__class__ is self.X:
                    self.unregister(name)

    def __str__(self):
        return repr(self())

    def serialize(self):
        return str(self)

    # We tried many, *many* different syntactic methods here, and this one was
    # simply the best -- not very intrusive, easily overridden by subclasses,
    # etc.
    def __call__(self):
        if _lastModified > self._lastModified:
            if self._name in _cache:
                self.set(_cache[self._name])
        return self.value

def toBool(s):
    s = s.strip().lower()
    if s in ('true', 'on', 'enable', 'enabled', '1'):
        return True
    elif s in ('false', 'off', 'disable', 'disabled', '0'):
        return False
    else:
        raise ValueError, 'Invalid string for toBool: %s' % quoted(s)

class Boolean(Value):
    """Value must be either True or False (or On or Off)."""
    def set(self, s):
        try:
            v = toBool(s)
        except ValueError:
            if s.strip().lower() == 'toggle':
                v = not self.value
            else:
                self.error()
        self.setValue(v)

    def setValue(self, v):
        super(Boolean, self).setValue(bool(v))

class Integer(Value):
    """Value must be an integer."""
    def set(self, s):
        try:
            self.setValue(int(s))
        except ValueError:
            self.error()

class NonNegativeInteger(Integer):
    """Value must be a non-negative integer."""
    def setValue(self, v):
        if v < 0:
            self.error()
        super(NonNegativeInteger, self).setValue(v)

class PositiveInteger(NonNegativeInteger):
    """Value must be positive (non-zero) integer."""
    def setValue(self, v):
        if not v:
            self.error()
        super(PositiveInteger, self).setValue(v)

class Float(Value):
    """Value must be a floating-point number."""
    def set(self, s):
        try:
            self.setValue(float(s))
        except ValueError:
            self.error()

    def setValue(self, v):
        try:
            super(Float, self).setValue(float(v))
        except ValueError:
            self.error()

class PositiveFloat(Float):
    """Value must be a floating-point number greater than zero."""
    def setValue(self, v):
        if v <= 0:
            self.error()
        else:
            super(PositiveFloat, self).setValue(v)

class Probability(Float):
    """Value must be a floating point number in the range [0, 1]."""
    def __init__(self, *args, **kwargs):
        self.__parent = super(Probability, self)
        self.__parent.__init__(*args, **kwargs)

    def setValue(self, v):
        if 0 <= v <= 1:
            self.__parent.setValue(v)
        else:
            self.error()

def safeEval(s, namespace={'True': True, 'False': False, 'None': None}):
    """Evaluates s, safely.  Useful for turning strings into tuples/lists/etc.
    without unsafely using eval()."""
    try:
        node = compiler.parse(s)
    except SyntaxError, e:
        raise ValueError, 'Invalid string: %s.' % e
    nodes = compiler.parse(s).node.nodes
    if not nodes:
        if node.__class__ is compiler.ast.Module:
            return node.doc
        else:
            raise ValueError, format('Unsafe string: %q', s)
    node = nodes[0]
    if node.__class__ is not compiler.ast.Discard:
        raise ValueError, format('Invalid expression: %q', s)
    node = node.getChildNodes()[0]
    def checkNode(node):
        if node.__class__ is compiler.ast.Const:
            return True
        if node.__class__ in (compiler.ast.List,
                              compiler.ast.Tuple,
                              compiler.ast.Dict):
            return all(checkNode, node.getChildNodes())
        if node.__class__ is compiler.ast.Name:
            if node.name in namespace:
                return True
            else:
                return False
        else:
            return False
    if checkNode(node):
        return eval(s, namespace, namespace)
    else:
        raise ValueError, format('Unsafe string: %q', s)

chars = string.maketrans('', '')

class String(Value):
    """Value is not a valid Python string."""
    def set(self, s):
        if not s:
            s = '""'
        elif s[0] != s[-1] or s[0] not in '\'"':
            s = repr(s)
        try:
            v = safeEval(s)
            if not isinstance(v, basestring):
                raise ValueError
            self.setValue(v)
        except ValueError: # This catches safeEval(s) errors too.
            self.error()

    _printable = string.printable[:-4]
    def _needsQuoting(self, s):
        return s.translate(chars, self._printable) and s.strip() != s

    def __str__(self):
        s = self.value
        if self._needsQuoting(s):
            s = repr(s)
        return s

class OnlySomeStrings(String):
    validStrings = ()
    def __init__(self, *args, **kwargs):
        assert self.validStrings, 'There must be some valid strings.  ' \
                                  'This is a bug.'
        self.__parent = super(OnlySomeStrings, self)
        self.__parent.__init__(*args, **kwargs)
        self.__doc__ = format('Valid values include %L.',
                              map(repr, self.validStrings))

    def help(self):
        strings = [s for s in self.validStrings if s]
        return format('%s  Valid strings: %L.', self._help, strings)

    def normalize(self, s):
        lowered = s.lower()
        L = list(map(str.lower, self.validStrings))
        try:
            i = L.index(lowered)
        except ValueError:
            return s # This is handled in setValue.
        return self.validStrings[i]

    def setValue(self, s):
        s = self.normalize(s)
        if s in self.validStrings:
            self.__parent.setValue(s)
        else:
            self.error()

class NormalizedString(String):
    def __init__(self, default, *args, **kwargs):
        default = self.normalize(default)
        self.__parent = super(NormalizedString, self)
        self.__parent.__init__(default, *args, **kwargs)
        self._showDefault = False

    def normalize(self, s):
        return normalizeWhitespace(s.strip())

    def set(self, s):
        s = self.normalize(s)
        self.__parent.set(s)

    def setValue(self, s):
        s = self.normalize(s)
        self.__parent.setValue(s)

    def serialize(self):
        s = str(self)
        prefixLen = len(self._name) + 2
        lines = textwrap.wrap(s, width=76-prefixLen)
        last = len(lines)-1
        for (i, line) in enumerate(lines):
            if i != 0:
                line = ' '*prefixLen + line
            if i != last:
                line += '\\'
            lines[i] = line
        ret = os.linesep.join(lines)
        return ret

class StringSurroundedBySpaces(String):
    def setValue(self, v):
        if v.lstrip() == v:
            v= ' ' + v
        if v.rstrip() == v:
            v += ' '
        super(StringSurroundedBySpaces, self).setValue(v)

class StringWithSpaceOnRight(String):
    def setValue(self, v):
        if v.rstrip() == v:
            v += ' '
        super(StringWithSpaceOnRight, self).setValue(v)

def perlReToPythonRe(s):
    """Converts a string representation of a Perl regular expression (i.e.,
    m/^foo$/i or /foo|bar/) to a Python regular expression.
    """
    sep = _getSep(s)
    splitter = _getSplitterRe(s)
    try:
        (kind, regexp, flags) = splitter.split(s)
    except ValueError: # Unpack list of wrong size.
        raise ValueError, 'Must be of the form m/.../ or /.../'
    regexp = regexp.replace('\\'+sep, sep)
    if kind not in ('', 'm'):
        raise ValueError, 'Invalid kind: must be in ("", "m")'
    flag = 0
    try:
        for c in flags.upper():
            flag |= getattr(re, c)
    except AttributeError:
        raise ValueError, 'Invalid flag: %s' % c
    try:
        return re.compile(regexp, flag)
    except re.error, e:
        raise ValueError, str(e)


class Regexp(Value):
    """Value must be a valid regular expression."""
    def __init__(self, *args, **kwargs):
        kwargs['setDefault'] = False
        self.sr = ''
        self.value = None
        self.__parent = super(Regexp, self)
        self.__parent.__init__(*args, **kwargs)

    def error(self, e):
        self.__parent.error('Value must be a regexp of the form %s' % e)

    def set(self, s):
        try:
            if s:
                self.setValue(perlReToPythonRe(s), sr=s)
            else:
                self.setValue(None)
        except ValueError, e:
            self.error(e)

    def setValue(self, v, sr=None):
        parent = super(Regexp, self)
        if v is None:
            self.sr = ''
            parent.setValue(None)
        elif sr is not None:
            self.sr = sr
            parent.setValue(v)
        else:
            raise InvalidRegistryValue, \
                  'Can\'t setValue a regexp, there would be an inconsistency '\
                  'between the regexp and the recorded string value.'

    def __str__(self):
        self() # Gotta update if we've been reloaded.
        return self.sr

class SeparatedListOf(Value):
    List = list
    Value = Value
    sorted = False
    def splitter(self, s):
        """Override this with a function that takes a string and returns a list
        of strings."""
        raise NotImplementedError

    def joiner(self, L):
        """Override this to join the internal list for output."""
        raise NotImplementedError

    def set(self, s):
        L = self.splitter(s)
        for (i, s) in enumerate(L):
            v = self.Value(s, '')
            L[i] = v()
        self.setValue(L)

    def setValue(self, v):
        super(SeparatedListOf, self).setValue(self.List(v))

    def __str__(self):
        values = self()
        if self.sorted:
            values = sorted(values)
        if values:
            return self.joiner(values)
        else:
            # We must return *something* here, otherwise down along the road we
            # can run into issues showing users the value if they've disabled
            # nick prefixes in any of the numerous ways possible.  Since the
            # config parser doesn't care about this space, we'll use it :)
            return ' '

class SpaceSeparatedListOf(SeparatedListOf):
    def splitter(self, s):
        return s.split()
    joiner = ' '.join

class SpaceSeparatedListOfStrings(SpaceSeparatedListOf):
    Value = String

class SpaceSeparatedSetOfStrings(SpaceSeparatedListOfStrings):
    def __init__(self):
        SpaceSeparatedListOfStrings.__init__(self)
        self.List = self.set

class CommaSeparatedListOfStrings(SeparatedListOf):
    Value = String
    def splitter(self, s):
        return re.split(r'\s*,\s*', s)
    joiner = ', '.join

def isChannel(s, chantypes='#&+!', channellen=50):
    """s => bool
    Returns True if s is a valid IRC channel name."""
    return s and \
           ',' not in s and \
           '\x07' not in s and \
           s[0] in chantypes and \
           len(s) <= channellen and \
           len(s.split(None, 1)) == 1


conf = Group()
conf.setName('test configuration registry')

def registerGroup(Group, name, group=None, **kwargs):
    if kwargs:
        group = registry.Group(**kwargs)
    return Group.register(name, group)

def registerGlobalValue(group, name, value):
    value.channelValue = False
    return group.register(name, value)

def registerChannelValue(group, name, value):
    value._supplyDefault = True
    value.channelValue = True
    g = group.register(name, value)
    gname = g._name.lower()
    for name in registry._cache.iterkeys():
        if name.lower().startswith(gname) and len(gname) < len(name):
            name = name[len(gname)+1:] # +1 for .
            parts = registry.split(name)
            if len(parts) == 1 and parts[0] and isChannel(parts[0]):
                # This gets the channel values so they always persist.
                g.get(parts[0])()

def get(group, channel=None):
    if group.channelValue and \
       channel is not None and isChannel(channel):
        return group.get(channel)()
    else:
        return group()



def _test():
    import doctest, supystyle
    doctest.testmod(supystyle)

if __name__ == '__main__':
    _test()
