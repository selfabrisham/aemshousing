"""
accounting.py

Accounting and Financial functions.

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

import pandas as import pd

################################################################################################################################
# Financial Statements
################################################################################################################################
def balance_sheet(accounts=None, category_dict=None):
    """
    Calculate daily balances of grouped assets/liabilities based on `category_dict`s from `accounts`, returns a DataFrame.

    Balance sheet is split into these sections:
    Assets
        Current
            Cash
            ...
        Long Term
            Investments
            Property
            ...
    Liabilities
        Current
            Credit Card
            ...
        Long Term
            Loans
            ...

    categories = {
        'Assets' : {
            'Current': {
                # User category keys and account DataFrame columns list for values
                'Cash & Cash Equivalents': [
                    ('Cash', 'BofA Checking'),
                    ('Cash', 'BofA Savings'),
                    ...
                ],
                'User Category': [...]
                ...
            },
            'Long Term': {...}
        },
        'Liabilities' : {
            'Current': {...},
            'Long Term': {...}
        }
    }
    """

    # Aggregate accounts based on category definition, via 3 level dictionary comprehension
    balance_dict = {
        (k0, k1, k2): accounts[v2].sum(axis=1)
            for k0, v0 in category_dict.iteritems()
                for k1, v1 in v0.iteritems()
                    for k2, v2 in v1.iteritems()
                        if v2
    }

    # Convert to DataFrame
    balance = pd.DataFrame(balance_dict)

    return balance.fillna(0.0)

def balance_sheet(balance=None, period=datetime.datetime.now().year):
    """
    Calculate and return a balance sheet.
    Balance will be based on the last entry of account data (e.g. December 31st) for the given `period` time period,
    which defaults to the current year.

    All levels may be user defined by the category dictonary. The value of the last level must contain valid pandas DataFrame
    column selectors, e.g. `Account Type` for single index column / level 0 access or `('Cash', 'Account Name')` for
    multilevel indexing.

    Example:
    ```
    balance = calc_balance(accounts, category_dict=categories)
    balancesheet = balance_sheet(balance, period=2015)
    ```
    """

    # Force period to string
    period = str(period)

    # Sum over Period and convert to Statement DataFrame
    balance = pd.DataFrame(balance[period].iloc[-1])
    balance.columns = ['$']
    balance.index.names = ['Category', 'Type', 'Item']

    # Calculate Net
    net = balance[['$']].sum(level=[0,1]).sum(level=1)
    net.index = pd.MultiIndex.from_tuples([('Net', x0, 'Total') for x0 in net.index])
    net.index.names = ['Category', 'Type', 'Item']

    # Add Net
    balance = pd.concat([balance, net])

    # Calculate percentages of level 0
    balance['%'] = 100.0 * balance.div(balance.sum(level=0), level=0)

    # Calculate heirarchical totals
    l1_totals = balance.sum(level=[0,1])
    l1_totals.index = pd.MultiIndex.from_tuples([(x0, x1, 'Total') for x0, x1 in l1_totals.index])
    l1_totals.index.names = ['Category', 'Type', 'Item']

    l0_totals = balance.sum(level=[0])
    l0_totals.index = pd.MultiIndex.from_tuples([(x0, 'Total', ' ') for x0 in l0_totals.index])
    l0_totals.index.names = ['Category', 'Type', 'Item']

    # Add totals to dataframe
    balance = balance.combine_first(l1_totals)
    balance = balance.combine_first(l0_totals)

    return balance

def calc_income(paychecks=None, transactions=None, category_dict=None):
    """
    Calculate daily income of grouped revenue/expenses/taxes based on `category_dict`s from `paychecks` and `transactions`, returns a DataFrame.

    Income Statement is split into these sections:
    Revenue
        Operating
            Technical Services
            ...
        Non-Operating
            Interest Income
            Dividend & Capital Gains
            ...
    Expenses
        Operating
            Medical
            ...
        Non-Operating
            ...
    Taxes
        Operating
            Federal
            State
            ...

    All levels may be user defined by the category dictonary. However the last level must contain a dictionary
    with at least a `category` key and set of categories for the value along with optional parameters.

    ```
    'Revenue': {
        'Operating': {
            # Paychecks
            'Technical Services': {
                'source': 'paycheck',            # Optional string to select data source,  defaults to 'transactions'
                'categories': {'Paycheck', ...}, # Required set of categories
                'labels': set(),                 # Optional set of labels, defaults to set() if not passed in
                'logic': ''                      # Optional 'not' string to set inverse of 'labels', defaults to ''
            },
            'User Category': {...}
        },
        'Non-Operating': {
            'User Category': {
                'categories': {...}
            }
        }
    },
    'Expenses': {
        'Operating': {...},
        'Non-Operating': {..}
    },
    'Taxes': {
        'Operating': {...},
        'Non-Operating': {..}
    }
    ```
    """

    # Clean category
    for k0, v0 in category_dict.iteritems():
        for k1, v1 in v0.iteritems():
            for k2, v2 in v1.iteritems():
                if not v2.has_key('source'):
                    category_dict[k0][k1][k2]['source'] = 'transactions'
                if not v2.has_key('labels'):
                    category_dict[k0][k1][k2]['labels'] = set()
                if not v2.has_key('logic'):
                    category_dict[k0][k1][k2]['logic'] = ''

    # Aggregate accounts based on category definition, via 3 level dictionary comprehension
    income_dict = {}
    for k0, v0 in category_dict.iteritems():
        for k1, v1 in v0.iteritems():
            for k2, v2 in v1.iteritems():

                if v2['source'] =='transactions':
                    income_dict[(k0, k1, k2)] = transactions[
                        # If it is in the category
                        (transactions['category'].isin(v2['categories'])) &
                        (
                            # And if is has the correct label
                            (transactions['labels'].apply(
                                    lambda x: x.isdisjoint(v2['labels']) if v2['logic'] else not x.isdisjoint(v2['labels'])
                            )) |
                            # Or it does not have any labels
                            (transactions['labels'].apply(lambda x: v2['labels'] == set()))
                        )
                    ]['amount']
                else:
                    income_dict[(k0, k1, k2)] = paychecks[list(v2['categories'])].sum(axis=1)

    # Convert to DataFrame
    cats = income_dict.keys()
    cats.sort()
    income = pd.DataFrame([], columns=pd.MultiIndex.from_tuples(cats), index=pd.date_range(transactions.index[-1], transactions.index[0]))
    for cat in income_dict:
        d = pd.DataFrame(income_dict[cat].values, index=income_dict[cat].index, columns=pd.MultiIndex.from_tuples([cat]))
        income[cat] = d.groupby(lambda x: x.date()).sum()

    return income.fillna(0.0)

def income_statement(income=None, period=datetime.datetime.now().year, nettax=None):
    """
    Calculate and return an Income Statement.
    Income will be based on the last entry of account data (e.g. December 31st) for the given `period` time period,
    which defaults to the current year.

    Example:
    ```
    income = calc_income(paychecks=paychecks, transactions=transactions, category_dict=categories)
    incomestatement = income_statement(income, period=2016)
    ```
    """

    # Force period to string and set default nettax
    period = str(period)
    nettax = nettax if nettax else {'Taxes'}

    # Convert to DataFrame
    income = pd.DataFrame(income[period].sum(), columns=['$'])
    income.index.names = ['Category', 'Type', 'Item']

    # Calculate percentages of level 0
    income['%'] = 100.0 * income.div(income.sum(level=0), level=0)

    # Calculate heirarchical totals
    l1_totals = income.sum(level=[0,1])
    l1_totals.index = pd.MultiIndex.from_tuples([(x0, x1, 'Total') for x0, x1 in l1_totals.index])
    l1_totals.index.names = ['Category', 'Type', 'Item']

    l0_totals = income.sum(level=[0])
    l0_totals.index = pd.MultiIndex.from_tuples([(x0, 'Total', ' ') for x0 in l0_totals.index])
    l0_totals.index.names = ['Category', 'Type', 'Item']

    # Add totals to dataframe
    income = income.combine_first(l1_totals)
    income = income.combine_first(l0_totals)

    # Calculate Net
    before = [(x, 'Total', ' ') for x in set(income.index.levels[0]).difference(nettax)]
    after =  [(x, 'Total', ' ') for x in set(income.index.levels[0])]

    net = pd.DataFrame({
        '$': [
            income.loc[before]['$'].sum(),
            income.loc[after]['$'].sum(),
            income.loc[after]['$'].sum()
        ]
    }, index=pd.MultiIndex.from_tuples([
        ('Net', 'Net Income', 'Before Taxes'),
        ('Net', 'Net Income', 'After Taxes'),
        ('Net', 'Total', ' ')
    ]))

    # Add Net
    income = pd.concat([income, net])

    return income

def calc_cashflow(transactions=None, category_dict=None):
    """
    Calculate daily cashflow of grouped inflow/outflow based on `category_dict`s from `transactions`, returns a DataFrame.

    Cashflow is split into these sections:
    Inflow
        Operating
            Technical Services
            ...
        Non-Operating
            Interest Income
            Dividend & Capital Gains
            ...
    Outflow
        Operating
            Rent
            Food
            ...
        Non-Operating
            Interest Payments
            ...

    All of the first 3 levels may be user defined by the category dictonary. However the last level must contain a dictionary
    with at least a `category` key and set of categories for the value along with optional parameters.

    ```
    categories = {
        'Inflow': {
            'Operating': {
                # Paychecks
                'Technical Services': {
                    'categories': {'Paycheck', ...}, # required set of categories
                    'labels': set(),                 # optional set of labels, defaults to set() if not passed in
                    'logic': ''                      # optional 'not' string to set inverse of 'labels', defaults to ''
                },
                'User Category': {...}
            },
            'Non-Operating': {
                'User Category': {
                    'categories': {...}
                }
            }
        },
        'Outflow': {
            'Operating': {...},
            'Non-Operating': {..}
        }
    }
    ```
    """

    # Add empty 'labels' key to dictionary if they do not have the item
    # Add default 'logic' if it does not exist
    for k0, v0 in category_dict.iteritems():
        for k1, v1 in v0.iteritems():
            for k2, v2 in v1.iteritems():
                if not v2.has_key('labels'):
                    category_dict[k0][k1][k2]['labels'] = set()
                if not v2.has_key('logic'):
                    category_dict[k0][k1][k2]['logic'] = ''

    # Aggregate transactions based on category definition, via 3 level dictionary comprehension
    cashflow_dict = {
        (k0, k1, k2):
            transactions[
                # If it is in the category
                (transactions['category'].isin(v2['categories'])) &
                (
                    # And if is has the correct label
                    (transactions['labels'].apply(
                            lambda x: x.isdisjoint(v2['labels']) if v2['logic'] else not x.isdisjoint(v2['labels'])
                    )) |
                    # Or it does not have any labels
                    (transactions['labels'].apply(lambda x: v2['labels'] == set()))
                )
            ]['amount']

            for k0, v0 in category_dict.iteritems()
                for k1, v1 in v0.iteritems()
                    for k2, v2 in v1.iteritems()
    }

    # Convert to DataFrame
    cols = cashflow_dict.keys()
    cols.sort()
    cashflow = pd.DataFrame([], columns=pd.MultiIndex.from_tuples(cols), index=pd.date_range(transactions.index[-1], transactions.index[0]))
    for cat in cashflow_dict:
        c = pd.DataFrame(cashflow_dict[cat].values, index=cashflow_dict[cat].index, columns=pd.MultiIndex.from_tuples([cat]))
        cashflow[cat] = c.groupby(lambda x: x.date()).sum()

    return cashflow.fillna(0.0)

def cashflow_statement(cashflow=None, period=datetime.datetime.now().year):
    """
    Return a Cashflow Statement for a period from cashflow DataFrame.
    Cashflow will be based on the last entry of account data (e.g. December 31st) for the given `period` time period, which defaults to the current year.  A Net section is automagically calculated.

    Example:
    ```
    cashflow = calc_cashflow(transactions, category_dict=categories)
    cashflowstatement = cashflow_statement(cashflow, period=2015)
    ```
    """

    # Force period to string
    period = str(period)

    # Sum over Period and convert to Statement DataFrame

    cashflow = pd.DataFrame(cashflow[period].sum(), columns=['$'])
    cashflow.index.names = ['Category', 'Type', 'Item']

    # Calculate Net
    net = cashflow[['$']].sum(level=[0,1]).sum(level=1)
    net.index = pd.MultiIndex.from_tuples([('Net', x0, 'Total') for x0 in net.index])
    net.index.names = ['Category', 'Type', 'Item']

    # Add Net
    cashflow = pd.concat([cashflow, net])

    # Calculate percentages of level 0
    cashflow['%'] = 100.0 * cashflow.div(cashflow.sum(level=0), level=0)

    # Calculate heirarchical totals
    l1_totals = cashflow.sum(level=[0,1])
    l1_totals.index = pd.MultiIndex.from_tuples([(x0, x1, 'Total') for x0, x1 in l1_totals.index])
    l1_totals.index.names = ['Category', 'Type', 'Item']

    l0_totals = cashflow.sum(level=[0])
    l0_totals.index = pd.MultiIndex.from_tuples([(x0, 'Total', ' ') for x0 in l0_totals.index])
    l0_totals.index.names = ['Category', 'Type', 'Item']

    # Add totals to dataframe
    cashflow = cashflow.combine_first(l1_totals)
    cashflow = cashflow.combine_first(l0_totals)

    return cashflow
