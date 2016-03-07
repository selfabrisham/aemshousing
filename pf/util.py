"""
util.py

Common functions used across code.

project    : pf
version    : 0.0.0
status     : development
modifydate :
createdate :
website    : https://github.com/tmthydvnprt/pf
author     : tmthydvnprt
email      : tim@tmthydvnprt.com
maintainer : tmthydvnprt
license    : MIT
copyright  : Copyright 2016, tmthydvnprt
credits    :

"""

import datetime
import numpy as np
import pandas as pd

################################################################################################################################
# Helper Functions
################################################################################################################################
def parse_month_year_end(my):
    """Parse month/year to pandas datetimeindex at month's end"""
    m, y = [int(x) for x in my.split('/')]
    m1 = (m + 1) if m < 12 else 1
    y1 = (y + 1) if m > 11 else y
    return pd.to_datetime(datetime.date(y1, m1, 1) - datetime.timedelta(days=1))

def parse_month_day_dates(x=''):
    """Parse dates that only contain month/day for dates in current year"""
    try:
        y = pd.to_datetime(x)
    except pd.tslib.OutOfBoundsDatetime:
        y = pd.to_datetime('{} {}'.format(x, datetime.datetime.now().year))
    return y

def get_age(d, bday=datetime.datetime(1989, 3, 27)):
    """Calculate personal age given birthday"""
    return np.round((d - bday).days / DAYS_IN_YEAR, 2)

def f2as(x=0.0):
    """Format number to accounting string"""
    if np.isnan(x):
        return ' '
    else:
        return '{:0,.2f}'.format(x) if x >= 0 else '({:0,.2f})'.format(np.abs(x))
