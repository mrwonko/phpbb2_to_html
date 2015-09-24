from __future__ import print_function

from . import extract, render

def convert( **db_options ):
    """ options are forwarded to _mysql.connect(); fill accordingly. """
    render.render( extract.extract( **db_options ) )
