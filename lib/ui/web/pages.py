from nevow import rend
from nevow import loaders
from nevow import static
from nevow import inevow

from formless import webform

from pymon.registry import globalRegistry

class TestPage(rend.Page):
    addSlash = True
    docFactory = loaders.xmlfile('static/web/testpage.html')
    child_styles = static.File('static/web/styles')
    child_images = static.File('static/web/images')
    child_webform_css = webform.defaultCSS

class Root(rend.Page):
    """
    Root pymon page class.
    """
    addSlash = True
    docFactory = loaders.xmlfile('static/web/home.html')
    child_styles = static.File('static/web/styles')
    child_images = static.File('static/web/images')
    child_icons = static.File('static/web/icons')
    child_webform_css = webform.defaultCSS

    def child_states(self, context):
        return StatesPage()

    def child_statesdetail(self, context):
        return StatesDetailPage()

class StatesPage(rend.Page):
    """
    Service states are listed in this page.
    """
    docFactory = loaders.xmlfile('static/web/states.html')

    def __init__(self):
        self.monitors = globalRegistry.factories

    def data_host(self, context, data):
        return self.monitors

    def render_getMonitors(self, context, data):
        idxs = sorted(self.monitors)
        pat = inevow.IQ(context).patternGenerator('monitorList')
        return [ pat(data=mon) for mon in idxs ]

    def render_getStates(self, context, data):
        idxs = sorted(self.monitors)
        pat = inevow.IQ(context).patternGenerator('stateList')
        return [ pat(data=self.monitors[mon].state) for mon in idxs ]

    def data_getMonitors(self, context, data):
        return str(self.monitors)

class StatesDetailPage(StatesPage):
    docFactory = loaders.xmlfile('static/web/statesdetail.html')

