import os.path
import time

from . import utils, bbcode

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

class Post:
    def __init__( self, topic, id, username, timestamp, subject, text, enable_bbcode, enable_html, bbcode_uid ):
        self.id = id
        self._bbcode_uid = bbcode_uid
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
            return bbcode.convert( self._text, self._bbcode_uid, topics = topics, posts = posts )
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
