from nevow import rend
from nevow import loaders
from nevow import static

from formless import webform

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

    def __init__(self, state_data):
        self.state = state_data

    def child_states(self, context):
        return StatesPage(self.state)

    def child_statesdetail(self, context):
        return StatesDetailPage(self.state)

class StatesPage(rend.Page):
    """
    Service states are listed in this page.
    """
    docFactory = loaders.xmlfile('static/web/states.html')

    def __init__(self, state_data):
        self.state = state_data

class StatesDetailPage(StatesPage):
    docFactory = loaders.xmlfile('static/web/statesdetail.html')

