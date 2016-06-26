"""
constants.py

Constants used across code.

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

import re

################################################################################################################################
# Constant Definitions
################################################################################################################################
# General Constants
DAYS_IN_YEAR = 365.24
DATE_RE = re.compile(r'\d{4}-\d{2}-\d{2}')

# Regex Constants


# Forcasting Constants
ARIMA_ORDERS = [(3, 2, 1), (2, 2, 1), (2, 1, 1), (1, 1, 1), (1, 1, 0), (1, 0, 0)]
