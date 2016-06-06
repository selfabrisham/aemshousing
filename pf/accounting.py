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
import datetime
import numpy as np
import pandas as pd

from pf.constants import DAYS_IN_YEAR
from pf.util import get_age

################################################################################################################################
# Financial Statements
################################################################################################################################
def calc_balance(accounts=None, category_dict=None):
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
        (k0, k1, k2): accounts[v2].sum(axis=1) if v2 else pd.Series(0, index=accounts.index)
        for k0, v0 in category_dict.iteritems()
        for k1, v1 in v0.iteritems()
        for k2, v2 in v1.iteritems()
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
    net = balance[['$']].sum(level=[0, 1]).sum(level=1)
    net.index = pd.MultiIndex.from_tuples([('Net', x0, 'Total') for x0 in net.index])
    net.index.names = ['Category', 'Type', 'Item']

    # Add Net
    balance_df = pd.concat([balance, net])

    # Calculate percentages of level 0
    balance_df['%'] = 100.0 * balance_df.div(balance_df.sum(level=0), level=0)

    # Calculate heirarchical totals
    l1_totals = balance_df.sum(level=[0, 1])
    l1_totals.index = pd.MultiIndex.from_tuples([(x0, x1, 'Total') for x0, x1 in l1_totals.index])
    l1_totals.index.names = ['Category', 'Type', 'Item']

    l0_totals = balance_df.sum(level=[0])
    l0_totals.index = pd.MultiIndex.from_tuples([(x0, 'Total', ' ') for x0 in l0_totals.index])
    l0_totals.index.names = ['Category', 'Type', 'Item']

    # Add totals to dataframe
    balance_df = balance_df.combine_first(l1_totals)
    balance_df = balance_df.combine_first(l0_totals)

    return balance_df

def calc_income(paychecks=None, transactions=None, category_dict=None):
    """
    Calculate daily income of grouped revenue/expenses/taxes based on `category_dict`s from `paychecks` and `transactions`,
     returns a DataFrame.

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

                if v2['source'] == 'transactions':
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
    income = pd.DataFrame(
        data=[],
        columns=pd.MultiIndex.from_tuples(cats),
        index=pd.date_range(transactions.index[-1], transactions.index[0])
    )
    for cat in income_dict:
        cat_df = pd.DataFrame(income_dict[cat].values, index=income_dict[cat].index, columns=pd.MultiIndex.from_tuples([cat]))
        income[cat] = cat_df.groupby(lambda x: x.date()).sum()

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
    l1_totals = income.sum(level=[0, 1])
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
    after = [(x, 'Total', ' ') for x in set(income.index.levels[0])]

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
    income_df = pd.concat([income, net])

    return income_df

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
    #pylint: disable=cell-var-from-loop
    cashflow_dict = {
        (k0, k1, k2): transactions[
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
    cashflow = pd.DataFrame(
        data=[],
        columns=pd.MultiIndex.from_tuples(cols),
        index=pd.date_range(transactions.index[-1], transactions.index[0])
    )
    for cat in cashflow_dict:
        c = pd.DataFrame(cashflow_dict[cat].values, index=cashflow_dict[cat].index, columns=pd.MultiIndex.from_tuples([cat]))
        cashflow[cat] = c.groupby(lambda x: x.date()).sum()

    return cashflow.fillna(0.0)

def cashflow_statement(cashflow=None, period=datetime.datetime.now().year):
    """
    Return a Cashflow Statement for a period from cashflow DataFrame.
    Cashflow will be based on the last entry of account data (e.g. December 31st) for the given `period` time period, which
     defaults to the current year.  A Net section is automagically calculated.

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
    net = cashflow[['$']].sum(level=[0, 1]).sum(level=1)
    net.index = pd.MultiIndex.from_tuples([('Net', x0, 'Total') for x0 in net.index])
    net.index.names = ['Category', 'Type', 'Item']

    # Add Net
    cashflow_df = pd.concat([cashflow, net])

    # Calculate percentages of level 0
    cashflow_df['%'] = 100.0 * cashflow_df.div(cashflow_df.sum(level=0), level=0)

    # Calculate heirarchical totals
    l1_totals = cashflow_df.sum(level=[0, 1])
    l1_totals.index = pd.MultiIndex.from_tuples([(x0, x1, 'Total') for x0, x1 in l1_totals.index])
    l1_totals.index.names = ['Category', 'Type', 'Item']

    l0_totals = cashflow_df.sum(level=[0])
    l0_totals.index = pd.MultiIndex.from_tuples([(x0, 'Total', ' ') for x0 in l0_totals.index])
    l0_totals.index.names = ['Category', 'Type', 'Item']

    # Add totals to dataframe
    cashflow_df = cashflow_df.combine_first(l1_totals)
    cashflow_df = cashflow_df.combine_first(l0_totals)

    return cashflow_df

################################################################################################################################
# Net Worth Calculations
################################################################################################################################
def calculate_net_worth(accounts=None):
    """Calculate Net Worth (Assets - Debts) based on `accounts` DataFrame"""

    # Aggregate accounts by assets and debts
    net_worth = pd.DataFrame({
        'Assets': accounts[accounts > 0.0].fillna(0.0).sum(1),
        'Debts': accounts[accounts < 0.0].fillna(0.0).sum(1),
    })

    # Calculate Net Worth
    net_worth['Net'] = net_worth['Assets'] + net_worth['Debts']

    # Calculate Debt Ratio
    net_worth['Debt Ratio'] = 100.0 * (net_worth['Debts'].abs() / net_worth['Assets'])

    # Calculate Dollar and Percent Change
    for x in ['Assets', 'Debts', 'Net']:
        net_worth['{} Change ($)'.format(x)] = net_worth[x].diff(1).fillna(0.0)
        net_worth['{} Change (%)'.format(x)] = 100.0 * net_worth[x].pct_change().fillna(0.0)

    return net_worth

def calculate_stats(net_worth=None):
    """Calculate the statistics (Current, Max, Min, Mean, Median, Std. Dev.) of a `net_worth` DataFrame"""

    # Remove Infs and NaNs
    net_worth = net_worth.replace([-np.Inf, np.Inf, np.nan], 0.0)

    # Calculate Statistics
    stats = pd.DataFrame({'Current': net_worth.iloc[-1]})
    stats['Max'] = net_worth.max(skipna=True)
    stats['Min'] = net_worth.min(skipna=True)
    stats['Mean'] = net_worth.mean(skipna=True)
    stats['Median'] = net_worth.median(skipna=True)
    stats['Std Dev'] = net_worth.std(skipna=True)

    return stats

def calculate_growth(net_worth=None, offsets=None):
    """
    Calculates the growth of cetain time periods from a net_worth DataFrame.
    The default time periods (1Mo, 3Mo, 6Mo, YTD, 1Yr, 3Yr, 5Yr, Life) may be overriden by providing a list of nested tuples
     containing (string label, (pandas `DataTimeOffset` objects)).  Multiple `DataTimeOffset` will be added together.

    The default is
    ```
    [
        ('1 Mo', (pd.tseries.offsets.MonthEnd(-1),)),
        ('3 Mo', (pd.tseries.offsets.MonthEnd(-3),)),
        ('6 Mo', (pd.tseries.offsets.MonthEnd(-6),)),
        ('YTD', (-pd.tseries.offsets.YearBegin(), pd.tseries.offsets.MonthEnd())),
        ('1 Yr', (pd.tseries.offsets.MonthEnd(-1 * 12),)),
        ('2 Yr', (pd.tseries.offsets.MonthEnd(-2 * 12),)),
        ('3 Yr', (pd.tseries.offsets.MonthEnd(-3 * 12),)),
        ('5 Yr', (pd.tseries.offsets.MonthEnd(-5 * 12),)),
        ('Life', (pd.DateOffset(days=-(net_worth.index[-1] - net_worth.index[0]).days),))
    ]
    ```
    """

    # Set up
    columns = ['Assets', 'Debts', 'Net']
    current_index = net_worth.index[-1]

    # Calculate Grow over time periods (1mo, 3mo, 6mo, ytd, 1yr, 3yr,, 5yr, 10yr, life)
    offsets = offsets if offsets else [
        ('1 Mo', (pd.tseries.offsets.MonthEnd(-1),)),
        ('3 Mo', (pd.tseries.offsets.MonthEnd(-3),)),
        ('6 Mo', (pd.tseries.offsets.MonthEnd(-6),)),
        ('YTD', (-pd.tseries.offsets.YearBegin(), pd.tseries.offsets.MonthEnd())),
        ('1 Yr', (pd.tseries.offsets.MonthEnd(-1 * 12),)),
        ('2 Yr', (pd.tseries.offsets.MonthEnd(-2 * 12),)),
        ('3 Yr', (pd.tseries.offsets.MonthEnd(-3 * 12),)),
        ('5 Yr', (pd.tseries.offsets.MonthEnd(-5 * 12),)),
        ('Life', (pd.DateOffset(days=-(net_worth.index[-1] - net_worth.index[0]).days),))
    ]

    growth = []
    for offstr, offset in offsets:
        # Compute offset date
        final = current_index
        initial = current_index
        for t in offset:
            initial = initial + t

        # If inside data
        if initial >= net_worth.index[0]:
            # Set time indexes
            initial_date = initial.date().strftime('%b %Y')
            final_date = final.date().strftime('%b %Y')
            number_of_days = (final - initial).days
            number_of_years = number_of_days / DAYS_IN_YEAR
            # Calculate growth
            delta = net_worth.loc[final][columns] - net_worth.loc[initial][columns]
            gains = 100.0 * delta / net_worth.loc[initial][columns]
            annualized_gains = gains / number_of_years
            try:
                cagr = 100.0 * (
                    (net_worth.loc[final][columns] / net_worth.loc[initial][columns]).pow(1.0 / number_of_years) - 1.0
                )
            except ZeroDivisionError:
                cagr = pd.Series(np.zeros(gains.shape))
            # Store Info in Dictionary
            #pylint: disable=maybe-no-member
            growth.extend([
                [offstr, final_date] + net_worth.loc[final][columns].round(2).values.tolist(),
                [offstr, initial_date] + net_worth.loc[initial][columns].round(2).values.tolist(),
                [offstr, 'Delta'] + delta.round(2).values.tolist(),
                [offstr, 'Gain'] + gains.round(2).values.tolist(),
                [offstr, 'Ann Gain'] + annualized_gains.round(2).values.tolist(),
                [offstr, 'CAGR'] + cagr.round(2).values.tolist()
            ])

    # Convert to DataFrame
    growth_df = pd.DataFrame(growth, columns=['Period', 'Growth', 'Assets', 'Debts', 'Net']).set_index(['Period', 'Growth'])

    return growth_df

def summarize_accounts(accounts=None):
    """Summarize current accounts"""

    # Get current accounts
    account_summary = accounts.iloc[[-1]].T
    account_summary.columns = ['Balance']
    account_summary.index.names = ['Type', 'Account']

    # Calculate percentages of type and total
    percent_of_type = 100.0 * account_summary.div(account_summary.sum(level=0), level=0)
    percent_of_total = 100.0 * account_summary.div(account_summary.sum(), level=0)
    account_summary['% of Type'] = percent_of_type
    account_summary['% of Total'] = percent_of_total

    # Calculate heirarchical totals
    l0_totals = account_summary.sum(level=[0])
    l0_totals.index = pd.MultiIndex.from_tuples([(x0, 'Total') for x0 in l0_totals.index])
    l0_totals.index.names = ['Type', 'Account']

    # Add totals to DataFrame
    account_summary = account_summary.combine_first(l0_totals)

    return account_summary

def get_milestones(networth=None, milestones=None):
    """Search networth for milestones"""
    milestones = milestones if milestones else np.array([
        1e4, 2.5e4, 5e4, 7.5e4, 1e5, 1.5e5, 2e5, 2.5e5, 5e5, 7.5e5, 1e6, 1.5e6, 2e6
    ])
    milestone_data = []
    for milestone in milestones:
        gt_milestone = networth['Net'] >= milestone
        milestone_date = gt_milestone[gt_milestone].index[0] if gt_milestone.any() else gt_milestone.index[-1]
        milestone_age = get_age(milestone_date)
        milestone_years = (milestone_date - datetime.datetime.today()).days / DAYS_IN_YEAR
        milestone_actual = networth['Net'].loc[milestone_date]
        milestone_data.append((milestone_date, milestone, milestone_actual, milestone_age, milestone_years))

    return pd.DataFrame(milestone_data, columns=['Date', 'Milestone', 'Actual', 'Age', 'Years'])

def summary_statement(networth=None, income=None, cashflow=None, limits=None):
    """
    Combine accounts, expenses, income, debt, etc. into one high level DataFrame
    """
    summary = pd.concat([
        networth[['Assets', 'Debts', 'Net']],
        12.0 * pd.DataFrame(income.Revenue.resample('M', how='sum').sum(axis=1), columns=['Total Income']),
        12.0 * pd.DataFrame(cashflow.Inflow.resample('M', how='sum').sum(axis=1), columns=['Realized Income']),
        12.0 * pd.DataFrame(cashflow.Outflow.resample('M', how='sum').sum(axis=1), columns=['Expense']),
        12.0 * pd.DataFrame(income.Taxes.resample('M', how='sum').sum(axis=1), columns=['Taxes']),
        pd.DataFrame(limits.sum(axis=1), columns=['Credit Line']),
    ], axis=1).dropna()

    return summary

def calc_metrics(summary=None, swr=0.04):
    """
    Calculate various metrics for personal finance (profit margin (SR), debt ratio, debt to income, time to FI).
    """
    # Create mean from month to month yearly estimates
    summary[['Total Income', 'Realized Income', 'Expense', 'Taxes']] = pd.expanding_mean(
        summary[['Total Income', 'Realized Income', 'Expense', 'Taxes']]
    )
    # Calculate metrics
    metrics = pd.DataFrame({
        'Debt Ratio [%]' : 100.0 * -summary['Debts'] / summary['Assets'],
        'Debt to Income [%]' : 100.0 * -summary['Debts'] / summary['Realized Income'],
        'Debt Utilization [%]' : 100.0 * -summary['Debts'] / summary['Credit Line'],
        'Profit Margin [%]' : 100.0 * (summary['Realized Income'] + summary['Expense']) / summary['Realized Income'],
        'Income Multiple [Yr]' : summary['Net'] / summary['Realized Income'],
        'Expense Multiple [Yr]' :  summary['Net'] / -summary['Expense'],
        'Safe Withdrawl Expense [%]' : 100.0 * (swr * summary['Net']) / -summary['Expense'],
        'Safe Withdrawl Income [%]' : 100.0 * (swr * summary['Net']) / summary['Realized Income'],
        'Realized Income to Net [%]' : 100.0 * summary['Realized Income'] / summary['Net'],
        'Total Tax Rate [%]' : 100.0 * summary['Taxes'] / summary['Total Income'],
        'Realized Income Tax Rate [%]' : 100.0 * summary['Taxes'] / summary['Realized Income'],
        'Tax to Net [%]' : 100.0 * summary['Taxes'] / summary['Net'],
    })

    return metrics
