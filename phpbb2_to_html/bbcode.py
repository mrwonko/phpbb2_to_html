import re

from . import utils, config

_INTERNAL_POST_LINK_RE = re.compile( r'(?:^|/)viewtopic\.php\?(?:.*&)?p=([0-9]+)' )
_INTERNAL_TOPIC_LINK_RE = re.compile( r'(?:^|/)viewtopic\.php\?(?:.*&)?t=([0-9]+)' )

# can't precompile due to uid
_REPLACEMENTS = [
    ( r'\[code:1:{uid}\](.*?)\[/code:1:{uid}\]', '<pre>\\1</pre>', re.I | re.S ),
    ( r'\[code:{uid}\]', u'<pre>', re.I ),
    ( r'\[/code:{uid}\]', u'</pre>', re.I ),
    ]

_NEWLINE_OR_PRE_RE = re.compile( r'\n|<pre>' )

def _convertNewlines( text ):
    """
    Converts newlines to <br/>, but only outside <pre> tags
    
    Only finds exact "<pre>" matches, but we only generate those.
    """
    result = []
    while True:
        match = _NEWLINE_OR_PRE_RE.search( text )
        if not match:
            result.append( text )
            return "".join( result )
        if match.group() == '\n':
            result.append( text[:match.start()] )
            result.append( "<br/>\n" )
            text = text[match.end():]
        else: # <pre>
            end = text.find( "</pre>", match.end() )
            result.append( text[:end] )
            text = text[end:]

def convert( text, bbcode_uid, **context ):
    def convertInternalLink( href, context ):
        topic = None
        match = _INTERNAL_POST_LINK_RE.match( href )
        if match:
            topic = context[ "topics" ].get( int( match.groups( 1 ) ), None )
        else:
            match = _INTERNAL_TOPIC_LINK_RE.match( href )
            if match:
                post = context[ "posts" ].get( int( match.groups( 1 ) ), None )
                if post:
                    topic = post.topic
        if topic:
            return u"../../{}".format( utils.escapeHTML( topic.url() ) )
        else:
            return href
    
    # replacements depending on context
    replacements = _REPLACEMENTS + [
        ]
    
    for pattern, repl, flags in replacements:
        text = re.sub( pattern.format( uid = bbcode_uid ), repl, text, flags = flags )
    return _convertNewlines( text )
