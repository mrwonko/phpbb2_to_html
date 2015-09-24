import os.path
import time

import bbcode #TODO: DELETEME
import re #TODO: DELETEME

from . import utils

DATE_FORMAT = u"{date.tm_year}-{date.tm_mon:0>2}-{date.tm_mday:0>2} {date.tm_hour:0>2}{sep}{date.tm_min:0>2}"
TOPIC_TYPE_NORMAL = 0
TOPIC_TYPE_STICKY = 1
TOPIC_TYPE_ANNOUNCEMENT = 2
TOPIC_PREFIX = {
    TOPIC_TYPE_STICKY: "_sticky ",
    TOPIC_TYPE_ANNOUNCEMENT: "_announcement "
    }

class Forum:
    def __init__( self, forum_id, cat_title, cat_order, forum_name, forum_order ):
        self.id = forum_id
        self.name = forum_name.decode("latin-1")
        self.order = forum_order
        self.cat_title = cat_title.decode("latin-1")
        self.cat_order = cat_order

    def url( self ):
        return "/".join( (
            utils.toFilename( u"{self.cat_order} - {self.cat_title}".format( self=self ) ),
            utils.toFilename( u"{self.order} - {self.name}".format( self=self ) )
            ) )

    def path( self ):
        return os.path.normpath( self.url() )

    def __repr__( self ):
        return self.path()

class Topic:
    def __init__( self, forums, id, title, timestamp, forum_id, poster, type ):
        self.id = id
        self.type = type
        self._title = title.decode("latin-1")
        self._time = time.gmtime( timestamp )
        self.forum = forums[ forum_id ]
        self.poster = poster.decode("latin-1") # username
        self.posts = []

    def time( self, hourSep = u":" ):
        return DATE_FORMAT.format( date = self._time, sep=hourSep )

    def url( self ):
        prefix = TOPIC_PREFIX.get( self.type, "" )
        return u"/".join( (
            self.forum.url(),
            utils.toFilename( u"{}{} {}.html".format( prefix, self.time( u"" ), self._title ) )
            ) )

    def path( self ):
        return os.path.normpath( self.url() )

    def __repr__( self ):
        return self.path()

    def title( self ):
        return self._title # already escaped

#TODO DELETEME
DOMAIN_RE = re.compile(r'(?im)(?:www\d{0,3}[.]|[a-z0-9.\-]+[.](?:com|net|org|edu|biz|gov|mil|info|io|name|me|tv|us|uk|mobi))')
INTERNAL_LINK_RE = re.compile(r'(?:.*/)?viewtopic\.php\?(?:.*&)?(?:p=(?P<post_id>[0-9]+)|t=(?P<topic_id>[0-9]+).*)')

def convertInternalLink( href, context ):
    match = INTERNAL_LINK_RE.match( href )
    if match:
        data = match.groupdict()
        try:
            topic = context[ "topics" ][ int( data[ "topic_id" ] ) ] if data[ "topic_id" ] else context[ "posts" ][ int( data[ "post_id" ] ) ].topic
            return u"../../{}".format( escapeHTML( topic.url() ) )
        except KeyError:
            # missing posts/topics
            return href
    return href

def linker( text, context ):
    href = text
    if u"://" not in href:
        href = u"http://{}".format( href )
    href = convertInternalLink( href, context )
    return u'<a href="{}">{}</a>'.format( href.replace(u'"', u'%22'), text )

def render_url( name, value, options, parent, context ):
    if options and 'url' in options:
        # Option values are not escaped for HTML output.
        href = escapeHTML( options['url'] )
    else:
        href = value
    # Completely ignore javascript: and data: "links".
    if re.sub(r'[^a-z0-9+]', '', href.lower().split(u':', 1)[0]) in (u'javascript', u'data', u'vbscript'):
        return ''
    # Only add the missing http:// if it looks like it starts with a domain name.
    if u'://' not in href and _domain_re.match(href):
        href = 'http://' + href
    # For local/
    if u'://' not in href or u'darth-arth.de' in href:
        href = convertInternalLink( href, context )
    return u'<a href="{}">{}</a>'.format( href.replace(u'"', u'%22'), value )

parser = bbcode.Parser(
    linker_takes_context = True,
    linker = linker
    )
class Post:
    def __init__( self, topic, id, username, timestamp, subject, text, enable_bbcode, enable_html, bbcode_uid ):
        self.id = id
        self.bbcode_uid = bbcode_uid
        self._username = username.decode("latin-1")
        self._time = time.gmtime( timestamp )
        self._subject = subject.decode("latin-1")
        self._text = text.decode("latin-1")
        self._enable_bbcode = bool( enable_bbcode )
        self._enable_html = bool( enable_html )
        self.topic = topic

    def subject( self ):
        return self._subject # already escaped

    def text( self, topics, posts ):
        # html whitelist is stored by phpbb, in my case it's: b,i,u,pre,object,embed
        # but I'm not going to be that selective.
        if self._enable_bbcode:
            #TODO
            parser.escape_html = False # fairly sure bbcode takes care of that
            return parser.format( self._text, topics = topics, posts = posts )
        else:
            return self._text
    
    def time( self, hourSep = u":" ):
        return DATE_FORMAT.format( date = self._time, sep=hourSep )
    
    def author( self ):
        return self._username # already escaped

class Data:
    def __init__( self, forums, topics, posts ):
        self.forums = forums
        self.topics = topics
        self.posts = posts
