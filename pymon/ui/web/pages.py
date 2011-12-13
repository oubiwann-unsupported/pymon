import os
from urllib2 import urlparse

import simplejson

from nevow import rend
from nevow import tags
from nevow import loaders
from nevow import static
from nevow import inevow

from formless import webform

from pymon.config import cfg
from pymon.application import globalRegistry


web = os.path.join(*cfg.web.doc_root.split('/'))

staticPath = os.path.join(*cfg.web.doc_root.split('/'))
templates = "%s/%s" % (staticPath, 'templates')
styles = "%s/%s" % (staticPath, 'css')
images = "%s/%s" % (staticPath, 'images')
icons = "%s/%s" % (staticPath, 'icons')
javascript = "%s/%s" % (staticPath, 'js')


# convenience function
def template(filename):
    return loaders.xmlfile(os.path.join(templates, filename))


# slots
class BaseSlot(rend.Fragment):

    def data_nbsp(self, context, data):
        return tags.xml("&nbsp;")

    def render_copyright(self, context, data):
        return tags.xml("&copy;")


class HTMLHeadSlot(BaseSlot):

    docFactory = template('htmlhead.html')

    def __init__(self, title):
        self.title = title

    def data_getPageTitle(self, context, data):
        return self.title


class PageHeaderSlot(BaseSlot):
    docFactory = template('pageheader.html')


class NavMenuSlot(BaseSlot):
    docFactory = template('navmenu.html')


class PageFooterSlot(BaseSlot):
    docFactory = template('pagefooter.html')


# pages
class TestPage(rend.Page):

    addSlash = True
    docFactory = template('testpage.html')
    child_styles = static.File(styles)
    child_images = static.File(images)
    child_webform_css = webform.defaultCSS


class BasePage(rend.Page):

    addSlash = True
    child_styles = static.File(styles)
    child_images = static.File(images)
    child_icons = static.File(icons)
    child_js = static.File(javascript)
    child_webform_css = webform.defaultCSS

    def render_allSlots(self, context, data):
        context.fillSlots('html_head',
            HTMLHeadSlot('pymon Management Interface'))
        context.fillSlots('page_header', PageHeaderSlot())
        context.fillSlots('nav_menu', NavMenuSlot())
        context.fillSlots('page_footer', PageFooterSlot())
        return context.tag


class Root(BasePage):
    """
    Root pymon page class.
    """
    docFactory = template('index.html')

    def child_combined(self, context):
        return StatesBasePage('combined')

    def child_local(self, context):
        return StatesBasePage('local')

    def child_json(self, context):
        return JSONPublisher()

    def data_getPeers(self, context, data):
        peers = []
        for peer in cfg.peers.url:
            peerData = {}
            schema, hostAndPort, path, d1, d2, d3 = urlparse.urlparse(peer)
            peerData['jsonURL'] = peer
            peerData['pymonHost'] = hostAndPort
            peerData['pymonURL'] = "%s://%s/local/states" % (schema,
                hostAndPort)
            peers.append(peerData)
        return peers


class StatesBasePage(BasePage):

    def __init__(self, pageType):
        self.pageType = pageType

    def child_states(self, context):
        return StatesPage()

    def child_statesdetail(self, context):
        return StatesDetailPage()


class StatesPage(BasePage):
    """
    Service states are listed in this page.
    """
    docFactory = template('states.html')

    def getStates(self):
        monitors = globalRegistry.factories
        idxs = sorted(monitors)
        return [ monitors[mon].state for mon in idxs ]

    def data_getStates(self, context, data):
        return self.getStates()


class StatesDetailPage(StatesPage):
    docFactory = template('statesdetail.html')


class JSONPublisher(StatesPage):
    docFactory = template('json.html')

    def __init__(self, data=None):
        self.data = data

    def child_localStates(self, context):
        data = [ mon.data for mon in self.getStates() ]
        return JSONPublisher(data)

    def child_combinedStates(self, context):
        # XXX 
        # for each peer and for the local host, get the JSON data and then
        # merge the data sets... gotta figure out how to determine "average"
        # service ups/downs...
        # for now, just return local data
        data = [ mon.data for mon in self.getStates() ]
        return JSONPublisher(data)

    def child_localConfig(self, context):
        pass

    def data_getJSONData(self, context, data):
        return simplejson.dumps(self.data)
