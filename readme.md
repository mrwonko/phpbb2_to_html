# PHPBB2 to HTML

This is mostly a personal project; I have an old PHPBB2 forum whose contents I want to keep, but I don't want to keep a PHP/MySQL stack around just to be able to look at it.

To this end this project connects to a MySQL database and extracts the topics/posts, then writes out static HTML (styled with bootstrap) in a directory structure reflecting the various categories/subforums/topics. It does not care about rights and is only tested with one forum (for which it was written), so it may not work for all inputs.

Most configuration is defined in [a static config file](phpbb2_to_html/config.py); I probably wouldn't release this as a package like that, but it works for me, and this isn't really meant to be for anyone but me. (But if you find it useful, great!)

The bbcode parsing is partially derived from [Dan Watson's bbcode library](https://pypi.python.org/pypi/bbcode/1.0.19); to prevent any potential issues this is thus also licensed as BSD.

As far as I can tell the MySQL-python package is only available for Python 2, as such this probably does not work with Python 3.
