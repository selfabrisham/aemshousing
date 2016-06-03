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

import sys
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
    year = 0
    try:
        year = pd.to_datetime(month_day)
    except (pd.tslib.OutOfBoundsDatetime, ValueError):
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

class ProgressBar(object):
    """implements a comand-line progress bar"""

    def __init__(self, iterations):
        """create a progress bar"""
        self.iterations = iterations
        self.prog_bar = '[]'
        self.fill_char = '*'
        self.width = 40
        self.__update_amount(0)

    def animate(self, iterate):
        """animate progress"""
        print '\r', self,
        sys.stdout.flush()
        self.update_iteration(iterate + 1)
        return self

    def update_iteration(self, elapsed_iter):
        """increment progress"""
        self.__update_amount((elapsed_iter / float(self.iterations)) * 100.0)
        self.prog_bar = '%s  %s of %s complete' % (self.prog_bar, elapsed_iter, self.iterations)
        return self

    def __update_amount(self, new_amount):
        """update amout of progress"""
        percent_done = int(round((new_amount / 100.0) * 100.0))
        all_full = self.width - 2
        num_hashes = int(round((percent_done / 100.0) * all_full))
        self.prog_bar = '[%s%s]' % ((self.fill_char * num_hashes), ' ' * (all_full - num_hashes))
        pct_place = (len(self.prog_bar) // 2) - len(str(percent_done))
        pct_string = '%s%%' % (percent_done)
        self.prog_bar = '%s%s%s' % (self.prog_bar[0:pct_place], pct_string, self.prog_bar[pct_place + len(pct_string):])
        return self

    def __str__(self):
        """string representation"""
        return str(self.prog_bar)

def make_pdf(dist, params, size=10000):
    """Generate distributions's Propbability Distribution Function """

    # Separate parts of parameters
    arg = params[:-2]
    loc = params[-2]
    scale = params[-1]

    # Get sane start and end points of distribution
    start = dist.ppf(0.01, *arg, loc=loc, scale=scale) if arg else dist.ppf(0.01, loc=loc, scale=scale)
    end = dist.ppf(0.99, *arg, loc=loc, scale=scale) if arg else dist.ppf(0.99, loc=loc, scale=scale)

    # Build PDF and turn into pandas Series
    x = np.linspace(start, end, size)
    y = dist.pdf(x, loc=loc, scale=scale, *arg)
    pdf = pd.Series(y, x)

    return pdf
