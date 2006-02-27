import os

from nevow import rend
from nevow import loaders
from nevow import static
from nevow import inevow

from formless import webform

from pymon.config import cfg
from pymon.registry import globalRegistry

pref = cfg.prefix
web = os.path.join(*cfg.web.doc_root.split('/'))

class TestPage(rend.Page):
    addSlash = True
    docFactory = loaders.xmlfile(os.path.join(
        pref, web, 'testpage.html'))
    child_styles = static.File(os.path.join(
        pref, web, 'styles'))
    child_images = static.File(os.path.join(
        pref, web, 'images'))
    child_webform_css = webform.defaultCSS

class Root(rend.Page):
    """
    Root pymon page class.
    """
    addSlash = True
    docFactory = loaders.xmlfile(os.path.join(
        pref, web, 'main.html'))

    child_styles = static.File(os.path.join(
        pref, web, 'styles'))
    child_images = static.File(os.path.join(
        pref, web, 'images'))
    child_icons = static.File(os.path.join(
        pref, web, 'icons'))
    child_js = static.File(os.path.join(
        pref, web, 'javascript'))

    child_webform_css = webform.defaultCSS

    def child_states(self, context):
        return StatesPage()

    def child_statesdetail(self, context):
        return StatesDetailPage()

class StatesPage(rend.Page):
    """
    Service states are listed in this page.
    """
    docFactory = loaders.xmlfile(os.path.join(
        pref, web, 'states.html'))

    def data_getStates(self, context, data):
        monitors = globalRegistry.factories
        idxs = sorted(monitors)
        return [ monitors[mon].state for mon in idxs ]

class StatesDetailPage(StatesPage):
    docFactory = loaders.xmlfile(os.path.join(
        pref, web, 'statesdetail.html'))

