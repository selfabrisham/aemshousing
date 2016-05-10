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
def clean_accounts(accounts=None):
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
    taxes = xlxs['taxes']

    # Set Index name for later
    accounts.index.name = 'Date'
    limits.index.name = 'Date'
    loan.index.name = 'Date'
    taxes.index.name = 'Date'

    # Clean up account data by user
    accounts = clean_accounts(accounts)

    return (accounts, limits, loan, taxes)

def clean_transactions(transactions=None):
    """
    Cleans transaction data at the end of `read_in_transactions()`, this will always need to be overriden by the user.
    """

    # Group Investments transactions together for simplicity
    # transactions.loc[transactions['account'] == 'Motif Individual', 'merchant'] = 'Motif Individual'

    # Remove Pending and Schedualed transactions
    # drop = (
    #     (transactions['account'] == 'Student Loan 1') | (transactions['account'] == 'Student Loan 2')
    # ) & (transactions['omerchant'] != 'Payment')
    # transactions = transactions[~drop]

    # Rename Category
    # transactions.loc[transactions['category'] == 'Transfer for Cash Spending', 'category'] = u'Cash Spending'

    return transactions

def read_in_transactions(filepath=''):
    """
    Read in the data file containing all transaction details, this should be a json file from mint.com, or the function should
    overriden by the user.

    Example:
    ```
    transactions = read_in_transactions('/path/to/transactions.json')
    ```

    See readme for example of [mint](mint.com) json export

    """

    # Read Transaction info
    transactions = pd.read_json(filepath, orient='records').set_index('date')
    # Correct Dates for index
    transactions.index = pd.DatetimeIndex([parse_month_day_dates(d) for d in transactions.index], name='Date')

    # Process labels
    transactions['labels'] = [{label['name'] for label in transaction} for transaction in transactions['labels']]

    # Remove duplicate transactions
    transactions = transactions[np.invert(transactions.isDuplicate)]

    # Convert amount from dollar strings to floats
    transactions['amount'] = transactions['amount'].str.replace('$', '').str.replace(',', '').astype(float)

    # Set debit transactions as negative
    transactions.loc[transactions.isDebit, 'amount'] = -1.0 * transactions.loc[transactions.isDebit, 'amount']

    # Clean up transaction data by user
    transactions = clean_transactions(transactions)

    return transactions
