import sys
import unittest
import doctest

sys.path.extend(['./lib', '../lib'])
from registry import globalRegistry
from application import State, History

globalRegistry.add(pymoncfg.global_names.state, State())
globalRegistry.add(pymoncfg.global_names.history, History())

# to add a new module to the test runner,
# simply include is in the list below:
modules = [
    'application',
    #'clients.factory',
    'registry',
    'utils',
]

suite = unittest.TestSuite()
for modname in modules:
    mod = __import__(modname)
    components = modname.split('.')
    #print mod, components, components[1:]
    if len(components) == 1:
        suite.addTest(doctest.DocTestSuite(mod))
    else:
        for comp in components[1:]:
            mod = getattr(mod, comp)
            #print "Adding mod '%s'..." % mod
            suite.addTest(doctest.DocTestSuite(mod))
runner = unittest.TextTestRunner()
runner.run(suite)
