from registry import globalRegistry
from Queue import Queue

class State(dict):
    pass

class History(Queue):

    def setLastRemoved(self, aItem):
        data = {'last':aItem}
        state = globalRegistry.getattr('state')
        state.update(data)

    def getLastRemoved(self):
        return globalRegistry.state.get('last')

    def add(self, aItem):
        try:
            self.put_nowait(aItem)
        except:
            self.removeItem()
            self.add(aItem)

    def removeItem(self):
        self.setLastRemoved(self.get())
        
            
