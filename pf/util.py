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

from pf.constants import DAYS_IN_YEAR

################################################################################################################################
# Helper Functions
################################################################################################################################
def parse_month_year_end(month_year=''):
    """Parse month/year to pandas datetimeindex at month's end"""
    month, year = [int(x) for x in month_year.split('/')]
    month0 = (month + 1) if month < 12 else 1
    year0 = (year + 1) if month > 11 else year
    return pd.to_datetime(datetime.date(year0, month0, 1) - datetime.timedelta(days=1))

def parse_month_day_dates(month_day=''):
    """Parse dates that only contain month/day for dates in current year"""
    try:
        year = pd.to_datetime(month_day)
    except pd.tslib.OutOfBoundsDatetime:
        year = pd.to_datetime('{} {}'.format(month_day, datetime.datetime.now().year))
    return year

def get_age(date=datetime.datetime.now(), bday=datetime.datetime(1989, 3, 27)):
    """Calculate personal age given birthday"""
    return np.round((date - bday).days / DAYS_IN_YEAR, 2)

def f2as(x=0.0):
    """Format number to accounting string"""
    if np.isnan(x):
        return ' '
    else:
        return '{:0,.2f}'.format(x) if x >= 0 else '({:0,.2f})'.format(np.abs(x))
