from __future__ import print_function

from . import extract, render

def convert( **db_options ):
    render.render( extract.extract( **db_options ) )
