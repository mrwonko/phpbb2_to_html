
_HTML_ESCAPE = (
    ('&', '&amp;'),
    ('<', '&lt;'),
    ('>', '&gt;'),
    ('"', '&quot;'),
    ("'", '&#39;'),
)

_PATH_ESCAPE = {
    '"': "'",
    '<': '{',
    '>': '}',
    ':': ' -',
    '/': '-',
    '\\': '-',
    '|': '-',
    '?': '',
    '*': '_'
    }

def replace( s, d ):
    for illegal, substitution in d:
        s = s.replace( illegal, substitution )
    return s

def toFilename( s ):
    return replace( s, _PATH_ESCAPE.items() )

def escapeHTML( s ):
    # order matters; & must be replaced first
    return replace( s, _HTML_ESCAPE )
