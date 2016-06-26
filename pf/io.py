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
from __future__ import division

import re
import os
import ast
import glob
import cStringIO
import numpy as np
import pandas as pd

from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage, PDFTextExtractionNotAllowed
from pdfminer.converter import TextConverter
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.layout import LAParams

from pf.constants import DATE_RE
from pf.util import read_date_csv_file, checksum

################################################################################################################################
# Account Functions
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
    accounts, limits, loan, taxes = read_in_accounts('/path/to/estate.xlsx')
    ```
    """

    # Read in account data as excel
    xlsx = pd.read_excel(
        filepath,
        sheetname=None,
        index_col=0,
        header=[0, 1]
    )

    # Separate out worksheet and fill NaNs
    accounts = xlsx['accounts'].fillna(0.0)
    limits = xlsx['limits'].fillna(0.0)
    loan = xlsx['loan'].fillna(0.0)
    incometaxes = xlsx['income taxes'].fillna(0.0)
    salestax = xlsx['sales tax'].fillna(0.0)

    # Set Index to DatetimeIndex
    accounts.index = pd.to_datetime(accounts.index, format='%m/%Y').to_period('M').to_timestamp('M')
    limits.index = pd.to_datetime(limits.index, format='%m/%Y').to_period('M').to_timestamp('M')
    loan.index = pd.to_datetime(loan.index, format='%m/%Y').to_period('M').to_timestamp('M')
    incometaxes.index = pd.to_datetime(incometaxes.index, format='%m/%Y').to_period('M').to_timestamp('M')
    salestax.index = pd.to_datetime(salestax.index, format='%m/%Y').to_period('M').to_timestamp('M')

    # Set Index name for later
    accounts.index.name = 'Date'
    limits.index.name = 'Date'
    loan.index.name = 'Date'
    incometaxes.index.name = 'Date'
    salestax.index.name = 'Date'

    # Clean up account data by user
    accounts = clean_accounts(accounts)

    return (accounts, limits, loan, incometaxes, salestax)

################################################################################################################################
# Transaction Functions
################################################################################################################################
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

def read_in_transactions(filepath='', cache=True):
    """
    Read in the data file containing all transaction details, this should be a json file from mint.com, or the function should
    overriden by the user.

    Example:
    ```
    transactions = read_in_transactions('/path/to/transactions.json')
    ```

    See readme for example of [mint](mint.com) json export

    """

    # Get filepaths
    transactions_cache_file = os.path.splitext(filepath)[0] + '.csv'
    cached = os.path.exists(transactions_cache_file)

    # Read in cached file if it exists
    if cache and cached:
        transactions = read_date_csv_file(transactions_cache_file)
        transactions['labels'] = transactions['labels'].map(lambda x: set(ast.literal_eval(x)))
        last_hash = transactions.ix[0, 'checksum']
        transactions = transactions.drop('checksum', 1)
    else:
        last_hash = ''
        transactions = None

    # Read Input Transaction info hash
    transaction_hash = checksum(filepath)

    # Read paycheck data if need be (not cached or update transactions)
    if not cache or not cached or transaction_hash != last_hash:

        # Read Transaction info
        transactions = pd.read_json(filepath, orient='records').set_index('date')
        # Correct Dates for index
        transactions.index = transactions.index.astype(str).to_datetime()

        # Process labels
        transactions['labels'] = [{label['name'] for label in transaction} for transaction in transactions['labels']]

        # Remove duplicate transactions
        transactions = transactions[np.invert(transactions.isDuplicate)]

        # Convert amount from dollar strings to floats
        transactions['amount'] = transactions['amount'].str.replace('$', '').str.replace(',', '').astype(float)

        # Set debit transactions as negative
        transactions.loc[transactions.isDebit, 'amount'] = -1.0 * transactions.loc[transactions.isDebit, 'amount']

        # Fill NaNs
        transactions = transactions.fillna(0.0)

        # Clean up transaction data by user
        transactions = clean_transactions(transactions)

        if cache:
            transactions.ix[0, 'checksum'] = transaction_hash
            transactions['labels'] = transactions['labels'].apply(list)
            transactions.to_csv(transactions_cache_file)
            transactions['labels'] = transactions['labels'].apply(set)
            transactions = transactions.drop('checksum', 1)

    return transactions

################################################################################################################################
# Paycheck Functions
################################################################################################################################
def paycheck_parser(paychecks_dict=None):
    """
    User defined function to convert dictonary of paycheck list of lists into a DataFrame. You could always replace of the whole
    function or you can use the default one as a starting point.  This fuction is called from within `read_in_paychecks()`.

    Necessary user defined parts are sectioned off with `#####`.

    """
    #pylint: disable=too-many-branches,too-many-statements,too-many-locals
    # User Defined Constants like precompiled regex
    ############################################################################################################################
    check_date_re = re.compile(r'.*Check Date: +(.*?) +.*')
    baserate_re = re.compile(r'(.*) Base Rate:')
    top_re = re.compile(r'Total Gross')
    earnings_re = re.compile(r'Earnings')
    end_re = re.compile(r'Total:')
    deductions_re = re.compile(r'Description')
    ############################################################################################################################

    # Loop thru dictionary (these lines are generic)
    paychecks = []
    for _, paycheck_text in paychecks_dict.items():

        # Parse data into dictionary of 'fields'
        df = {}

        # User Defined parsing 'flags' (usefull to have different parsing logic for different sections)
        # and internal or intermediate variables (usefull for saving data across rows without putting in final dictionary)
        ########################################################################################################################
        t = -1
        t0 = -1
        t1 = -1
        t2 = -1
        in_base = False
        in_top = False
        in_earnings = False
        in_deductions = False
        baserate = ''
        earnings_table = []
        taxes_table = []
        pre_table = []
        post_table = []
        other_table = []
        ########################################################################################################################

        lines = [line for line in paycheck_text.split('\n') if line.strip()]

        # Process each row of paycheck
        for line in lines:

            line = str(line)

            # User Defined Parser Logic, this will be totally dependent on the format of your paycheck pdf... good luck!
            ####################################################################################################################
            if in_base:
                number = float(line.strip().replace(',', ''))
                df['Base Rate'] = number * 80.0 if baserate == 'Hourly' else number
                in_base = False

            elif in_top:
                row = line.split()
                row = [row[0]] + [float(r.replace(',', '')) for r in row[1:]]
                try:
                    df['Total Gross'] = row[1]
                    df['Fed Taxable Gross'] = row[2]
                    df['OASDI Gross'] = row[3]
                    df['MEDI Gross'] = row[4]
                    df['Net Pay'] = row[5]
                except:
                    pass
                in_top = False

            elif in_earnings:
                end_earnings = end_re.search(line)
                # Parse tables
                earnings = line[:t]
                taxes = line[t:]
                row0 = [earnings[:e+1].split('  ')[-1].strip().replace(',', '') for e in earnings_table]
                row1 = [taxes[:e+1].split('  ')[-1].strip().replace(',', '') for e in taxes_table]
                key0 = earnings.split('  ')[0]
                key1 = taxes.split('  ')[0]

                if end_earnings:
                    in_earnings = False
                    key0 = key0.replace(':', '') + ' Pay'
                    key1 = key1.replace(':', '') + ' Tax'

                if key0:
                    df[key0] = float(row0[2]) if row0[2] else 0.0
                if key1:
                    df[key1] = float(row1[1]) if row1[1] else 0.0

            elif in_deductions:
                end_deductions = end_re.search(line)
                # Parse tables
                pre = line[:t1]
                post = line[t1:t2]
                other = line[t2:]
                row0 = [pre[:e+1].split('  ')[-1].strip().replace(',', '') for e in pre_table]
                row1 = [post[:e+1].split('  ')[-1].strip().replace(',', '') for e in post_table]
                row2 = [other[:e+1].split('  ')[-1].strip().replace(',', '') for e in other_table]
                key0 = pre.split('  ')[0]
                key1 = post.split('  ')[0]
                key2 = other.split('  ')[0]
                if end_deductions:
                    in_deductions = False
                    key0 = key0.replace(':', '') + ' Before Tax'
                    key1 = key1.replace(':', '') + ' After Tax'
                    key2 = key2.replace(':', '') + ' Other Tax'

                if key0:
                    df[key0] = float(row0[1]) if row0[1] else 0.0
                if key1:
                    df[key1] = float(row1[1]) if row1[1] else 0.0
                if key2:
                    df[key2] = float(row2[1]) if row2[1] else 0.0

            # Regular parsing
            else:

                # Search for Strings
                date_search = check_date_re.search(line)
                baserate_search = baserate_re.search(line)
                top_search = top_re.search(line)
                earnings_search = earnings_re.search(line)
                deductions_search = deductions_re.search(line)

                # Set flags and parse out table positions
                if date_search:
                    df['Date'] = pd.to_datetime(date_search.groups()[0])
                if baserate_search:
                    baserate = baserate_search.groups()[0]
                    in_base = True
                if top_search:
                    in_top = True
                if earnings_search:
                    t = line.find('Taxes')
                    earnings = line[:t]
                    taxes = line[t:]
                    earnigs_enum_zip = enumerate(zip(earnings[:-2], earnings[1:-1], earnings[2:]))
                    taxes_enum_zip = enumerate(zip(taxes[:-2], taxes[1:-1], taxes[2:]))
                    earnings_table = [i for i, (c0, c1, c2) in earnigs_enum_zip if c0 != ' ' and c1 + c2 == '  ']
                    taxes_table = [i for i, (c0, c1, c2) in taxes_enum_zip if c0 != ' ' and c1 + c2 == '  ']
                    in_earnings = True
                if deductions_search:
                    t0 = line.find('Description')
                    t1 = line.find('Description', t0 + 1)
                    t2 = line.find('Description', t1 + 1)
                    pre = line[:t1]
                    post = line[t1:t2]
                    other = line[t2:]
                    pre_enum_zip = enumerate(zip(pre[:-2], pre[1:-1], pre[2:]))
                    post_enum_zip = enumerate(zip(post[:-2], post[1:-1], post[2:]))
                    other_enum_zip = enumerate(zip(other[:-2], other[1:-1], other[2:]))
                    pre_table = [i for i, (c0, c1, c2) in pre_enum_zip if c0 != ' ' and c1 + c2 == '  ']
                    post_table = [i for i, (c0, c1, c2) in post_enum_zip if c0 != ' ' and c1 + c2 == '  ']
                    other_table = [i for i, (c0, c1, c2) in other_enum_zip if c0 != ' ' and c1 + c2 == '  ']

                    in_deductions = True

        # Store paycheck fields in list
        paychecks.append(df)

    # Convert list of paycheck field dictionary to DataFrame
    paycheck_df = pd.DataFrame(paychecks).set_index('Date')

    # Up until now paychecks are not necessarilly read or parsed in chronological order so sort chronologically
    paycheck_df = paycheck_df.sort_index()

    return paycheck_df

def read_in_paychecks(filepaths='', password='', parser=paycheck_parser, cache=True):
    """
    Read in all the paychecks from a directory full of PDFs and returns DataFrame. If a password is supplied encrypted PDFs CAN
    be read. PDFs are converted to text lines, which are assumed to be mostly tabular and converted to lists of lists using
    multiple spaces as elimiters. Since PDFs are unstructured the parsing function will almost definetly need to be overriden
    by the user.

    Note:
    Assumes PDF file names contain date.

    Example:
    ```
    paychecks = read_in_paychecks('/path/to/paycheck/directory/*.pdf', password='secret', parser=paycheck_parser)
    ```
    """

    # Get PDFs from directory and check for cached file
    paycheckfiles = glob.glob(filepaths)
    paycheck_cache_file = os.path.dirname(filepaths) + '.csv'
    cached = os.path.exists(paycheck_cache_file)

    # Read in cached file if it exists
    if cache and cached:
        paycheck_df = read_date_csv_file(paycheck_cache_file)

    # Read paycheck data if need be (not cached or new paycheck)
    if not cache or not cached or len(paycheckfiles) > len(paycheck_df):
        # Read in paycheck data to dictionary
        paycheck_dict = {}
        for paycheckfile in paycheckfiles:

            # Open a PDF file
            fp = open(paycheckfile, 'rb')
            # Get the date
            date = DATE_RE.findall(paycheckfile)[0]

            # Create string to put PDF
            output = cStringIO.StringIO()

            # Create a PDF parser object associated with the file object.
            pdfparser = PDFParser(fp)

            # Create a PDF document object that stores the document structure. Supply the password for initialization.
            document = PDFDocument(pdfparser, password)

            # Check if the document allows text extraction. If not, abort.
            if not document.is_extractable:
                raise PDFTextExtractionNotAllowed

            # Create a PDF resource manager object that stores shared resources.
            manager = PDFResourceManager()

            # Create a PDF converter object.
            converter = TextConverter(manager, output, laparams=LAParams())

            # Create a PDF interpreter object.
            interpreter = PDFPageInterpreter(manager, converter)

            # Process each page contained in the document.
            pages = list(PDFPage.create_pages(document))
            interpreter.process_page(pages[0])

            # Get text
            text = output.getvalue()

            # Close up file objects
            pdfparser.close()
            fp.close()
            converter.close()
            output.close()

            # Add to dictionary
            paycheck_dict[date] = text

        # Parse paycheck data with user defined function
        paycheck_df = parser(paycheck_dict)

        # Enforce pennies
        paycheck_df = paycheck_df.fillna(0.0).round(2)

        if cache:
            paycheck_df.to_csv(paycheck_cache_file)

    return paycheck_df
