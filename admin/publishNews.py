#!/usr/bin/env python2.4
import re
from datetime import datetime
from optparse import OptionParser

from adytum.util.text import formatRFC822LongField
from adytum.util.sourceforge.news import getNewsURL
from adytum.util.sourceforge.news import postNews as postSFNews
from adytum.util.launchpad.news import postNews as postLPNews

from sourceforge_website import pageparts

usage = '''%prog [options]
'''

optp = OptionParser(usage=usage)
optp.set_defaults(isDryRun=False)
optp.add_option('-d', '--dry-run', dest='isDryRun', action='store_true')
optp.add_option('-f', '--filename', dest='filename')
(opts, args) = optp.parse_args()
if not opts.filename:
    optp.error('It is required that you pass a filename.')

def readSourceFile(filename):
    """
    The source file is a simple text file with the first line being the
    headline, and the rest of the file being the body of the story.
    """
    fh = open(filename)
    lines = fh.readlines()
    fh.close()
    headline = lines[0].strip()
    story = ' '.join(lines[1:])
    return (headline, story)

def convertLinks(story, dest='site'):
    links = re.findall('\[(http.+?) (.+?[^\[]+?)\]', story)
    for link in links:
        oldLink = r'[%s %s]' % link
        if dest == 'sf.net':
            newLink = r'%s (%s)' % (link[1], link[0])
        else:
            newLink = r'<a href="%s">%s</a>' % link
        story = re.sub(re.escape(oldLink), newLink, story)
    return story

def convertBreaks(story, dest='site'):
    if dest == 'site':
        story = story.replace(' \n', '\n')
        story = story.replace('\n\n', '<br/><br/>')
    return story

def convertTags(story, dest='site'):
    for tagname in ['ul']:
        for tag in ['<%s>' % tagname, '</%s>' % tagname]:
            if dest == 'sf.net':
                story = re.sub(re.escape(tag), '', story)
    return story

def convertBullets(story, dest='site'):
    if dest == 'site':
        bullets = re.findall('(^\s+\*)(.+$)', story, re.MULTILINE)
        for star, text in bullets:
            oldBullet = re.compile('^'+re.escape(star + text), re.MULTILINE)
            newBullet = '<li>%s</li>' % text
            story = re.sub(oldBullet, newBullet, story)
    return story

def doConversions(story, dest='site'):
    story = convertTags(story, dest)
    story = convertBullets(story, dest)
    story = convertLinks(story, dest)
    story = convertBreaks(story, dest)
    return story

headline, story = readSourceFile(opts.filename)
htmlNews = formatRFC822LongField(doConversions(story, dest='site'))
sfNews = doConversions(story, dest='sf.net')
if opts.isDryRun:
    print "\npymon.net news item:\n"
    print ''.join(pageparts.assembleNewsItem(headline, htmlNews))
    print "SF.net news item:\n"
    print sfNews
else:
    dest = 'sourceforge_website/data/content/news.front'
    pageparts.updateNews(dest, headline, htmlNews)
    b = postSFNews('pymon', 'sourceforge_creds', headline, sfNews)
    url = getNewsURL(b)
    date = datetime.now().strftime('%Y-%m-%d %H:%M')
    postLPNews('pymon', 'launchpad_creds', headline, lpNews, url, date)
