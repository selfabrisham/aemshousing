"""
forecasting.py

Assumption and Data Driven based forecasting calculation.  Assumption based forecasting is useful for quickly playing with or understanding a concept; it can be used to evaluate various strategies without historical or real data.  Data driven forecasting is useful for forecasting an actual financial situation based on historical data, either personal or economic.  The Data driven approach generates statistical models from real data and forecasts with random samples from the models.

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
# Assumption Based Forecasting
################################################################################################################################

def assumption_financial_independance_forecast(
        income=50000.00,
        initial_balance=0.0,
        income_increase=0.03,
        savings_rate=0.50,
        withdrawal_rate=0.04,
        return_rate=0.05,
        age=23,
        life_expectancy=90,
        start=None,
        expense_increase=True
    ):
    """
    Financial Independance (Investment withdrawal > Living expenses) forecasting based purely on assumptions not real data.
    """

    # Calculate years to simulate
    years = life_expectancy - age

    # Empty DataFrame to store results
    columns = ['balance', 'income', 'savings', 'expenses', 'withdrawal', 'age', 'fi']
    cashflow_table = pd.DataFrame(
        data=np.zeros((years, len(columns))),
        index=range(years),
        columns=columns
    )
    cashflow_table.index.name = 'year'

    # Store initial balance
    cashflow_table.iloc[0]['balance'] = initial_balance

    # Generate Cashflow table
    fi = False
    for i in cashflow_table.index:

        # Calculate savings and expenses
        yearly_savings = savings_rate * income
        if i == 0 or expense_increase:
            yearly_expenses = (1 - savings_rate) * income if not fi else cashflow_table.loc[i-1]['withdrawal']

        # store data
        cashflow_table.loc[i]['age'] = age + i
        cashflow_table.loc[i]['income'] = income
        cashflow_table.loc[i]['savings'] = yearly_savings
        cashflow_table.loc[i]['expenses'] = yearly_expenses

        # If not the first year
        if i >= 1:
            # Growth balance
            cashflow_table.loc[i]['balance'] = (1 + return_rate) * cashflow_table.loc[i-1]['balance']
            # Calculate potential withdrawal
            cashflow_table.loc[i]['withdrawal'] = withdrawal_rate * cashflow_table.loc[i-1]['balance']

            # Once withdrawal is greater than expenses, retire
            if cashflow_table.loc[i]['withdrawal'] >= cashflow_table.loc[i-1]['expenses']:
                fi = True
                # Remove withdrawal from blance for expenses
                cashflow_table.loc[i]['balance'] -= cashflow_table.loc[i]['withdrawal']

        if fi:
            # stop income
            income = 0
        elif i > 0:
            # Add yearly savings
            cashflow_table.loc[i]['balance'] += yearly_savings

            # increase income a little for next year
            income = (1 + income_increase) * income

        # Store boolean
        cashflow_table.loc[i]['fi'] = fi

    # Turn Index into date if data available
    if start:
        cashflow_table['Date'] = pd.date_range(start=start, periods=len(cashflow_table.index), freq='A')
        cashflow_table = cashflow_table.reset_index().set_index('Date')

    return cashflow_table

################################################################################################################################
# Modeled Forecasting
################################################################################################################################
