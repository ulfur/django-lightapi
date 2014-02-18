#encoding: utf-8

import re, ast, dateutil
from datetime import date, datetime
import dateutil.parser

def parse_value( value ):
    if isinstance(value, str) or isinstance(value,unicode):
        value = str_value( value )
    elif isinstance( value, date ) and not isinstance( value, datetime ):
        value = datetime.combine( value, datetime.min.time() )
    elif isinstance( value, dict ):
        for k, v in value.items( ):
            value[k] = parse_value( v )
    elif isinstance( value, list ) or isinstance( value, tuple ):
        nl = []
        for v in value:
            nl.append( parse_value(v) )
        value = nl
    return value
    
reg_listtuple = '^[\(|\[].+[\)|\]]$'
reg_intfloat = '^\d{1,}(\.\d{1,}){0,1}$'
reg_datetime = '^\d{4}-\d{2}-\d{2}(T\d{2}:\d{2}:\d{2}\.\d{1,6}){0,1}$'

def str_value( value ):
    if re.match( reg_listtuple, value ):
        try:
            value = ast.literal_eval( value )
            return parse_value( value )
        except:
            pass
    elif re.match( reg_intfloat, value ):
        try:
            return ast.literal_eval( value )
        except:
            pass
    elif re.match( reg_datetime, value ):
        try:
            d = dateutil.parser.parse( value )
            if isinstance( d, date ) and not isinstance( d, datetime ):
                d = datetime.combine( d, datetime.min.time() )
            return d
        except:
            pass
    return value