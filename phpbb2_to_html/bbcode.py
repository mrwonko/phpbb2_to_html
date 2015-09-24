import re

from . import utils, config

_INTERNAL_POST_LINK_RE = re.compile( r'./viewtopic\.php\?(?:.*&)?p=([0-9]+)' )
_INTERNAL_TOPIC_LINK_RE = re.compile( r'/viewtopic\.php\?(?:.*&)?t=([0-9]+)' )

# can't precompile due to uid
_REPLACEMENTS = [
    ( r'\[code:1:{uid}\](.*?)\[/code:1:{uid}\]', r'<pre>\1</pre>', re.I | re.S ),
    ( r'\[code:{uid}\]', r'<pre>', re.I ),
    ( r'\[/code:{uid}\]', r'</pre>', re.I ),
    ( r'\[color=(\#[0-9a-f]{{6}}|[a-z]+):{uid}\]', r'<span style="color: \1">', re.I ),
    ( r'\[/color:{uid}\]', r'</span>', re.I ),
    ( r'\[size=([12]?[0-9]):{uid}\]', r'<span style="font-size: \1px">', re.I ),
    ( r'\[/size:{uid}\]', r'</span>', re.I ),
    ( r'\[b:{uid}\]', r'<strong>', re.I ),
    ( r'\[/b:{uid}\]', r'</strong>', re.I ),
    ( r'\[u:{uid}\]', r'<u>', re.I ),
    ( r'\[/u:{uid}\]', r'</u>', re.I ),
    ( r'\[i:{uid}\]', r'<em>', re.I ),
    ( r'\[/i:{uid}\]', r'</em>', re.I ),
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
    
    # quote attribution goes to the bottom in Bootstrap, so we need the author's name at the closing tag. Since quotes can be nested we need a stack.
    quote_stack = []
    def quote( match ):
        captures = match.groupdict()
        if captures[ "start" ]:
            quote_stack.append( captures[ 'author' ] )
            return u'<blockquote>'
        else:
            author = quote_stack.pop()
            if author:
                return u'<footer>{}</footer></blockquote>'.format( author )
            else:
                return u'</blockquote>'
    
    # to properly close list tags we need to keep track of our position in the list.
    list_first_stack = []
    def list_end( close_tag ):
        if not list_first_stack.pop():
            return u'</li>{}'.format( close_tag )
        else:
            return close_tag
    def list( match ):
        captures = match.groupdict()
        if captures[ "olist_start" ]:
            list_first_stack.append( True )
            return u'<ol type="{}">'.format( captures["type"] )
        elif captures[ "olist_end" ]:
            return list_end( '</ol>' )
        elif captures[ "ulist_start" ]:
            list_first_stack.append( True )
            return u'<ul>'
        elif captures[ "ulist_end" ]:
            return list_end( '</ul>' )
        elif captures[ "list_item" ]:
            if not list_first_stack[-1]:
                return u'</li><li>'
            else:
                list_first_stack[-1] = False
                return u'<li>'
        else:
            assert( False )
    
    # link handling
    
    def convertInternalLink( href ):
        topic = None
        match = _INTERNAL_POST_LINK_RE.search( href )
        if match:
            topic = context[ "topics" ].get( int( match.group( 1 ) ), None )
        else:
            match = _INTERNAL_TOPIC_LINK_RE.search( href )
            if match:
                post = context[ "posts" ].get( int( match.group( 1 ) ), None )
                if post:
                    topic = post.topic
        if topic:
            return u"../../{}".format( utils.escapeHTML( topic.url() ) )
        else:
            return href
    
    def url( prefix, href, text ):
        if "://" not in href:
            href = "http://{}".format( href )
        if config.isInternalLink( href ):
            href = convertInternalLink( href )
        return u'{}<a href="{}">{}</a>'.format( prefix, href, text )
    
    # handle all kinds of links at once, to prevent injections using nested urls
    def url_or_img( match ):
        captures = match.groupdict()
        if captures["img"]:
            return u'<img src="{}"/>'.format( captures["src"] )
        elif captures["url"]:
            href = captures["href_and_text"]
            return url( u"", href, href )
        elif captures["url_text"]:
            return url( u"", captures["href"], captures["text"] )
        elif captures["url_auto"]:
            href = captures["auto_href"]
            return url( captures["prefix"], href, href )
        else:
            assert( False )
    
    # replacements depending on context or have state
    replacements = _REPLACEMENTS + [
        ( '|'.join( [
            r'(?P<start>\[quote:{uid}(?:="(?P<author>.*?)")?\])',
            r'(?P<end>\[/quote:{uid}\])',
            ] ), quote, re.I ),
        
        ( '|'.join( [
            r'(?P<ulist_start>\[list:{uid}\])',
            r'(?P<ulist_end>\[/list:u:{uid}\])',
            r'(?P<olist_start>\[list=(?P<type>[a1]):{uid}\])',
            r'(?P<olist_end>\[/list:o:{uid}\])',
            r'(?P<list_item>\[\*:{uid}\])',
            ] ), list, re.I ),
        
        ( '|'.join( [
            #[img]src[/img]
            r'(?P<img>\[img:{uid}\](?P<src>.*?)\[/img:{uid}\])',
            #[url]href[/img]
            r'(?P<url>\[url\](?P<href_and_text>.*?)\[/url\])',
            #[url=href]text[/url]
            r'(?P<url_text>\[url=(?P<href>.*?)\](?P<text>.*?)\[/url\])',
            # http://url or www.url or ftp.url
            r'(?P<url_auto>(?P<prefix>(?:^|[ \n]))(?P<auto_href>(?:\w+://|(?:www|ftp)\.)[^\s,"\'<>]+))'
            ] ), url_or_img, re.I ),
        ]
    
    for pattern, repl, flags in replacements:
        text = re.sub( pattern.format( uid = bbcode_uid ), repl, text, flags = flags )
    return _convertNewlines( text )
