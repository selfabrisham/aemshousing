"""
io.py

Input and Output functions.

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

################################################################################################################################
# Data Input Functions
################################################################################################################################
def clean_accounts(accounts):
    """
    Clean account data for any reason necessary. This is called at the end of `read_in_accounts()`. This is optional and will
    always need to be overriden by the user.
    """

    return accounts

def read_in_accounts(filepath=''):
    """
    Read in the data file containing monlhty account balances, credit card limits, and miscallaneous loan.
    This should be an simple excel with sheets for each section, or the function should overriden by the user.

    Example:
    ```
    accounts, limits, loan = read_in_accounts('/path/to/estate.xlsx')
    ```
    """

    # Read in account data as excel
    xlxs = {k: v.fillna(0.0) for k, v in pd.read_excel(
        filepath,
        sheetname=None,
        index_col=0,
        parse_dates=True,
        header=[0,1],
        date_parser=parse_month_year_end
    ).items()}

    # Separate out worksheet
    accounts = xlxs['accounts']
    limits = xlxs['limits']
    loan = xlxs['loan']

    # Set Index name for later
    accounts.index.name = 'Date'
    limits.index.name = 'Date'
    loan.index.name = 'Date'

    # Clean up account data by user
    accounts = clean_accounts(accounts)

    return (accounts, limits, loan)
