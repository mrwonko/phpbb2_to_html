import jinja2
import os
import errno

from . import config

def _mkdir_p( path ):
    try:
        os.makedirs( path )
    except OSError as e:
        if e.errno == errno.EEXIST and os.path.isdir( path ):
            pass
        else:
            raise

env = jinja2.Environment(
    loader = jinja2.FileSystemLoader( "templates", encoding='utf-8' )
)
topic_template = env.get_template( "topic.html" )

def render( data ):
    # create directories
    if not config.DRY_RUN:
        for forum in data.forums.values():
            _mkdir_p( config.PATH_PREFIX + forum.path() )

    for topic in [ data.topics[301] ]: # data.topics.values():
        html = topic_template.render(
            topic = topic,
            posts = data.posts,
            topics = data.topics
            )
        if not config.DRY_RUN:
            with open( config.PATH_PREFIX + topic.path(), "wb" ) as f:
                f.write( html.encode( "utf-8" ) )
        if config.SINGLE_TOPIC:
            break
