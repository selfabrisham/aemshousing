"""
calculator.py

General functions that would be in a finacial calculator.
"""

import numpy as np

# Typical Financial Calculator Functions
# ------------------------------------------------------------------------------------------------------------------------------
def future_value(present_value=100.0, rate=0.07, num_period=1.0, frequency=1.0):
    """
    Calculate the future value of present_value present value after compounding for num_period periods at rate every frequency.
    """
    return present_value * np.power(1.0 + rate / frequency, num_period * frequency)

def present_value(future_value=100.0, rate=0.07, num_period=1.0, frequency=1.0):
    """
    Calculate the present value of future_value future value before compounding for num_period periods at rate every frequency.
    """
    return future_value / np.power(1.0 + rate / frequency, num_period * frequency)

def payment(rate=0.07, num_periods=72.0, present_value=0.0):
    """
    Calculate the payment for a loan payment based on constant period payments and interest rate.
    """
    return present_value * (rate * (1.0 + rate) ** num_periods) / ( (1.0 + rate) ** num_periods - 1.0)

def interest_payment(rate=0.07, period=1.0, num_periods=72.0, present_value=0.0):
    """
    Calculate the amount of interest for a loan payment based on constant period payments and interest rate.
    """
    pmt = payment(rate, num_periods, present_value)
    ppmt = principal_payment(rate, period, num_periods, present_value)
    return pmt - ppmt

def principal_payment(rate=0.07, period=1.0, num_periods=72.0, present_value=0.0):
    """
    Calculate the amount of principal for a loan payment based on constant period payments and interest rate.
    """
    pmt = payment(rate, num_periods, present_value)
    return (pmt - rate * present_value) * np.power(rate + 1.0, (period - 1.0))

def principal_remaining(rate=0.07, period=1.0, num_periods=72.0, present_value=0.0):
    """
    Calculate the amount of principal remaining for a loan based on constant period payments and interest rate.
    """
    pmt = payment(rate, num_periods, present_value)
    return (pmt + np.power(1.0 + rate, period) * (rate * present_value - pmt)) / rate

def loan_balance(rate=0.07, period=1.0, num_periods=72.0, present_value=0.0):
    """
    Alias for principal_remaining.
    """
    return principal_remaining(rate=rate, period=period, num_periods=num_periods, present_value=present_value)

def rate(future_value=100.0, present_value=90.0, num_period=1.0, frequency=1.0):
    """
    Calculate the rate needed to compound a present_value present value into a future_value future value compounding over num_period periods every frequency
    frequency.
    """
    return frequency * np.power(future_value / present_value, 1.0 / (num_period * frequency)) - 1.0

def periods(future_value=0.0, present_value=0.0, rate=0.0, frequency=0.0):
    """
    Calculate the period needed to compound a present_value present value into a future_value future value compounding at rate every frequency.
    """
    return np.log(future_value / present_value) / (frequency * np.log(1.0 + rate / frequency))

def effective_return(rate=0.07, frequency=2.0):
    """
    Calculate the annual rate needed to equal an rate at frequency.
    """
    return np.power(1.0 + (rate / frequency), frequency) - 1.0

def annual_return(rate=0.07, frequency=1.0):
    """
    Calculate annual return from semiannual return.
    """
    return np.power(1.0 + rate, frequency) - 1.0

def inflation_adjusted(rate=0.07, i=0.03):
    """
    Calculate inflation adjusted returns.
    """
    return (1.0 + rate) / (1.0 + i) - 1.0

def gain(xi=100.0, xf=110.0):
    """
    Calculate gain from intial to final value.
    """
    return (xf - xi) / xi

def amortization(p=1000.0, rate=0.05, num_period=10.0, frequency=1.0):
    """
    Calculate periodic payments needed to pay off p principle at rate over num_period periods every frequency.
    """
    return p * (rate / frequency) / (1.0 - np.power(1.0 + rate / frequency, -frequency*num_period))

def cagr(xi=100.0, xf=110.0, num_period=1.0):
    """
    Calculate compund annual growth rate.
    """
    return np.power(xf / xi, 1.0 / num_period) - 1.0

def length_of_payment(b=1000.0, p=100.0, apr=0.18):
    """
    Calculate the length of payments of b balance with p payment at apr APR.
    """
    i = apr / 30.0
    return (-1.0 / 30.0) * np.log(1.0 + (b / p)*(1.0 - np.power(1.0 + i, 30.0))) / np.log(1.0 + i)

def annuity(p=100.0, rate=0.07, num_period=10.0, frequency=1.0):
    """
    Calculate future value based on periodic p investment payment at rate over num_period periods every frequency - check this
    formula.
    """
    return p * ((np.power(1.0 + rate / frequency, num_period * frequency) - 1.0) / rate / frequency)
