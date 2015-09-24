import _mysql
from MySQLdb.constants import FIELD_TYPE

from . import config, types

_TOPIC_STATUS_UNLOCKED = 0
_TOPIC_STATUS_LOCKED = 1
_TOPIC_STATUS_MOVED = 2

_SELECT_FORUMS = """
    SELECT forum_id, cat_title, cat_order, forum_name, forum_order
    FROM {prefix}forums
    NATURAL JOIN {prefix}categories
    """.format( prefix = config.TABLE_PREFIX )


# forum_id 0 is for global stickies, which are not supported.
_SELECT_TOPICS = """
    SELECT topic_id, topic_title, topic_time, forum_id, username, topic_type
    FROM {prefix}topics AS topics
    JOIN {prefix}users AS users ON topics.topic_poster = users.user_id
    WHERE EXISTS (
        SELECT *
        FROM forumgr_forums AS forums
        WHERE forums.forum_id = topics.forum_id
        )
        AND
        topic_status != {MOVED}
        AND
        forum_id != 0
    """.format( MOVED = _TOPIC_STATUS_MOVED, prefix = config.TABLE_PREFIX )


_SELECT_POSTS = """
    SELECT posts.post_id, username, post_time, post_subject, post_text, enable_bbcode, enable_html, bbcode_uid
    FROM {prefix}posts AS posts
    JOIN {prefix}posts_text AS texts ON posts.post_id = texts.post_id
    JOIN {prefix}users AS users ON posts.poster_id = users.user_id
    WHERE posts.topic_id = {{topic_id}}
    ORDER BY post_time ASC
    """.format( prefix = config.TABLE_PREFIX )

def extract( **options ):
    db = _mysql.connect(
        conv = {
            # see https://dev.mysql.com/doc/refman/5.5/en/c-api-data-structures.html
            # integer
            FIELD_TYPE.LONG : int,
            # smallint
            FIELD_TYPE.SHORT : int,
            # mediumint
            FIELD_TYPE.INT24 : int,
            # tinyint (not exclusively used for bools)
            FIELD_TYPE.TINY : int,
            },
        **options
        )
    
    db.query( _SELECT_FORUMS )
    # store_result to fetch all, such that num_rows() works; use_result() for lazy fetching
    result = db.store_result()
    forums = {}
    for row in result.fetch_row( result.num_rows() ):
        forum = types.Forum( *row )
        forums[ forum.id ] = forum

    
    db.query( _SELECT_TOPICS ) # there is one orphan topic in my data, but it has no posts
    result = db.store_result()
    topics = {}
    for row in result.fetch_row( result.num_rows() ):
        topic = types.Topic( forums, *row )
        topics[ topic.id ] = topic
        if config.SINGLE_TOPIC:
            break

    
    posts = {}
    for topic in topics.values():
        db.query( _SELECT_POSTS.format( topic_id = topic.id ) )
        result = db.store_result()
        for row in result.fetch_row( result.num_rows() ):
            post = types.Post( topic, *row )
            posts[ post.id ] = post
            topic.posts.append( post )
    
    return types.Data( forums, topics, posts )
