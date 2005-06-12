import application
import configuration
import monitors
import states
from registry import globalRegistry
from time import sleep

cfg = configuration.Configuration()
state = states.State()
history = states.History(4)
print history.__dict__

globalRegistry.add('state', state)
globalRegistry.add('history', history)
globalRegistry.add('config', cfg)

app = application.Application()
app.setConfiguration(cfg)
app.setState(state)

globalRegistry.add('app', app)

while True:
  mon = monitors.Monitor()
  mon.run()
  sleep(5)
