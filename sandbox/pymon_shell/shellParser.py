from pyparsing import Word, Combine, Suppress, CharsNotIn, nums
from pyparsing import alphas, alphanums
from pyparsing import CaselessLiteral
import dispatch

class shellParser:

     def __init__(self, cmd):
         integer = Word(nums)
         ipAddress = Combine( integer + "." + integer + "." + integer + "." + integer )
         cmdStart = CaselessLiteral("show")
         cmdType = CaselessLiteral("status")
         monitor = Word( alphas, alphanums)
         cmdPattern =  cmdStart.setResultsName("cmdAction") + ipAddress.setResultsName("ipAddr") + monitor.setResultsName("monitor") + cmdType.setResultsName("cmdType")
         parsedTuple = cmdPattern.scanString(cmd)

         self.ipAddr = "";
         self.monitor = "";
         self.cmdAction = "";
         self.cmdType = "";
         for srvr, startloc, endloc in parsedTuple:
             self.ipAddr = srvr.ipAddr
             self.monitor = srvr.monitor
             self.cmdAction = srvr.cmdAction
             self.cmdType = srvr.cmdType

     [dispatch.generic()]
     def command(self):
         """generic method for cmd"""

     [command.when("self.cmdType == 'status'")]
     def commandStatus(self):
         return self.ipAddr, self.monitor, self.cmdAction, self.cmdType
