import os.path

# Don't write any files, just create and discard content?
DRY_RUN = False
# Just get one?
SINGLE_TOPIC = False
# output directory
PATH_PREFIX = "output" + os.path.sep
# MySQL table prefix
TABLE_PREFIX = "forumgr_"
# how to determine internal links
def isInternalLink( url ):
    return u"darth-arth.de" in url
