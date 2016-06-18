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
import hashlib
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
from pf.util import read_date_csv_file

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
    xls = pd.read_excel(
        filepath,
        sheetname=None,
        index_col=0,
        header=[0, 1]
    )
    xlsx = {k: v.fillna(0.0) for k, v in xls.items()}

    # Separate out worksheet
    accounts = xlsx['accounts']
    limits = xlsx['limits']
    loan = xlsx['loan']
    incometaxes = xlsx['income taxes']
    salestax = xlsx['sales tax']

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
    transaction_hash = hashlib.md5(filepath).hexdigest()

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

        # Clean up transaction data by user
        transactions = clean_transactions(transactions)

        if cache:
            transactions.ix[0, 'checksum'] = transaction_hash
            transactions['labels'] = transactions['labels'].apply(lambda x: list(x))
            transactions.to_csv(transactions_cache_file)
            transactions['labels'] = transactions['labels'].apply(lambda x: set(x))
            transactions = transactions.drop('checksum', 1)

    return transactions

################################################################################################################################
# Paycheck Functions
################################################################################################################################
def text2listoflists(text=''):
    """
    Convert text to list of lists.
    May need to be overriden by user, but it is suggested the use this format and override `paycheck_parser()`.
    """

    # Splits text on lines and then splits line on multiple spaces, ignoring empty lines
    listoflists = [
        [cell.strip() for cell in line.split('  ') if cell.strip() != '']
        for line in text.split('\n')
    ]
    # Remove empty lists or 'cells'
    listoflists = [
        p for p in listoflists
        if p and p != ['']
    ]

    # Parse floats if 'cell' only contains number
    #pylint: disable=bare-except
    for rownum, row in enumerate(listoflists):
        for colnum, col in enumerate(row):
            try:
                listoflists[rownum][colnum] = float(col.replace(',', ''))
            except:
                pass

    return listoflists

def paycheck_parser(paychecks_dict=None):
    """
    User defined function to convert dictonary of paycheck list of lists into a DataFrame. You could always replace of the whole
    function or you can use the default one as a starting point.  This fuction is called from within `read_in_paychecks()`.

    Necessary user defined parts are sectioned off with `#####`.

    """
    #pylint: disable=too-many-branches,too-many-statements
    # User Defined Constants like precompiled regex
    ############################################################################################################################
    baserate_re = re.compile(r'(.*) Base Rate:')
    ############################################################################################################################

    # Loop thru dictionary (these lines are generic)
    paychecks = []
    for _, paycheck_lists in paychecks_dict.items():

        # Parse data into dictionary of 'fields'
        paycheck_fields = {}

        # User Defined parsing 'flags' (usefull to have different parsing logic for different sections)
        # and internal or intermediate variables (usefull for saving data across rows without putting in final dictionary)
        ########################################################################################################################
        in_earnings = False
        in_deductions = False
        baserate = ''
        ########################################################################################################################

        # Process each row of paycheck
        for row in paycheck_lists:

            # User Defined Parser Logic, this will be totally dependent on the format of your paycheck pdf... good luck!
            ####################################################################################################################
            # If inside earnings and tax tables
            if in_earnings:
                # Find string cells, these represent the field keys (names), the floats represent the field values
                stringindex = np.array([i for i, cell in enumerate(row) if isinstance(cell, str)])

                if len(row) > 1 and row[0] == 'Total:':
                    if len(stringindex) == 2:
                        stringdiff = stringindex[1] - stringindex[0]
                        if stringdiff == 4:
                            paycheck_fields[row[stringindex[0]].replace(':', '') + ' Earnings'] = row[2]
                            paycheck_fields[row[stringindex[1]].replace(':', '') + ' Tax'] = -row[stringindex[1] + 1]
                        if stringdiff == 3:
                            paycheck_fields[row[stringindex[0]].replace(':', '') + ' Earnings'] = row[1]
                            paycheck_fields[row[stringindex[1]].replace(':', '') + ' Tax'] = -row[stringindex[1] + 1]

                    # If total row appears, exit earnings and tax table
                    in_earnings = False
                else:
                    # If there are two columns, get the data
                    if len(stringindex) == 2:
                        stringdiff = stringindex[1] - stringindex[0]
                        if stringdiff == 4:
                            paycheck_fields[row[0]] = row[2]
                            paycheck_fields[row[4]] = -row[5]
                        elif stringdiff == 3:
                            paycheck_fields[row[0]] = row[1]
                            paycheck_fields[row[3]] = -row[4]
                        elif stringdiff == 2:
                            paycheck_fields[row[2]] = -row[3]
                    # If single column get tax
                    else:
                        paycheck_fields[row[0]] = -row[1]

            # If inside deduction tables
            elif in_deductions:
                # Find string cells
                stringindex = np.array([i for i, cell in enumerate(row) if isinstance(cell, str)])
                # If there are two columns, get the data
                if len(stringindex) == 3:
                    stringdiff1 = stringindex[1] - stringindex[0]
                    stringdiff2 = stringindex[2] - stringindex[1]
                    if row[0] == 'Total:':
                        if stringdiff1 > 2:
                            paycheck_fields['Total Before Tax'] = -row[stringindex[0] + 1]
                        if stringdiff2 > 2:
                            paycheck_fields['Total After Tax'] = -row[stringindex[1] + 1]
                        if (len(row) - stringindex[2]) > 2:
                            paycheck_fields['Total Other Tax'] = -row[stringindex[2] + 1]
                        # If total row appears, exit earnings and tax table
                        in_deductions = False
                    else:
                        if stringdiff1 > 2:
                            paycheck_fields[row[stringindex[0]]] = -row[stringindex[0] + 1]
                        if stringdiff2 > 2:
                            paycheck_fields[row[stringindex[1]]] = -row[stringindex[1] + 1]
                        if (len(row) - stringindex[2]) > 2:
                            paycheck_fields[row[stringindex[2]]] = -row[stringindex[2] + 1]

                elif len(stringindex) == 2:
                    stringdiff = stringindex[1] - stringindex[0]
                    if stringdiff == 3:
                        paycheck_fields[row[0]] = -row[1]
                        if len(row) == 5:
                            paycheck_fields[row[3]] = -row[4]
                    elif stringdiff == 2:
                        paycheck_fields[row[2]] = -row[3]
                # If single column get current (3 cells)
                else:
                    paycheck_fields[row[0]] = -row[1]

            # Regular parsing
            else:
                baserate_search = baserate_re.search(str(row[0]))
                # Read Base Rate
                if baserate_search:
                    baserate = baserate_search.groups()[0]
                elif len(row) > 0 and isinstance(row[0], float):
                    paycheck_fields['Base Rate'] = row[0] * 80.0 if baserate == 'Hourly' else row[0]
                # Read Check Date
                elif len(row) > 1 and row[1] == 'Check Date:':
                    paycheck_fields['Date'] = pd.to_datetime(row[2])
                # Read Tax Categories
                elif len(row) > 4 and row[0] == 'Current':
                    paycheck_fields['Total Gross'] = row[1]
                    paycheck_fields['Fed Taxable Gross'] = row[2]
                    paycheck_fields['OASDI Gross'] = row[3]
                    paycheck_fields['MEDI Gross'] = row[4]
                    paycheck_fields['Net Pay'] = row[5]
                # Enter Earnings and Tax Tables
                elif len(row) > 0 and row[0] == 'Earnings':
                    in_earnings = True
                # Enter Earnings and Tax Tables
                elif len(row) > 0 and row[0] == 'Description':
                    in_deductions = True
            ####################################################################################################################

        # Store paycheck fields in list
        paychecks.append(paycheck_fields)

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

            # Convert to list of lists
            paycheck_lists = text2listoflists(text)

            # Add to dictionary
            paycheck_dict[date] = paycheck_lists

        # Parse paycheck data with user defined function
        paycheck_df = parser(paycheck_dict)

        # Enforce penny
        paycheck_df = paycheck_df.round(2)

        if cache:
            paycheck_df.to_csv(paycheck_cache_file)

    return paycheck_df
