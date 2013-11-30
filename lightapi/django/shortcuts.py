#encoding: utf-8

from datetime import datetime

def model_to_dict( model ):
    d = dict( model.__dict__ )
    d.pop( '_state' )
    for k, v in d.items( ):
        if type( v ) == datetime:
            d[k] = v.isoformat( )
    return d