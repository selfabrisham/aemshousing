# pfcompute
Personal Finance library for the Computationally Curious.

## Description
`pfcompute` is a python library for computationally exploring personal finance.  The library provides a computing environment with data structures, common equations/algorithms and convenience functions to calculate, analyze and visualize existing personal finance data. It is *not* meant to be a full service financial app or replace any software used to manage personal finances.  It does *not* collect data. However, once data is provided, it allows a much larger degree of freedom in processing and analyzing financial data than typical personal finance apps supply.

### Interactive Computing
While this library may be used internally to other software, it was intended to be used in a interactive computing fashion with software such as [jupyter](https://jupyter.org).  This type of environment, along with the library, provides a quick and easy way to explore complex data, relations and algorithms.

### Data Sources
Since `pfcompute` does not aggregate or collect it's own data, it requires data to be provided by some other means (e.g. [mint](https://mint.com), [personalcapital](https://personalcapital.com), [ynab](https://youneedabudget.com), [yodlee](https://yodlee.com), a bank, etc.).  It is left up to the user to obtain this data however they wish.  There are three main data sources assumed to exist by the library:

1. Accounts
2. Transactions
3. Paychecks

They can really be in any format (`xls(x)`, `csv`, `json`, `pdf`) as long as the user writes some method to interpret the data.  The data [format](#data-format) and some collection [ideas](#data-ideas) are described below.

## Features
The following checklist describes the current (`[x]`) and future (`[ ]`) capabilities of `pfcompute`:

- [x] Data input
    - [x] Import convenience functions
    - [x] Overridable data cleaning functions
    - [x] Generic paycheck import from folder of `pdf`s (user must write internal parser)
    - [x] User defines account & transaction categories
- [x] Generate financial statements
    - [x] Balance sheet
    - [x] Income statement
    - [x] Cashflow statement
    - [x] Account Summary
- [x] Net worth analysis
    - [x] Net worth calculator
    - [x] Growth calculator & analyzer
    - [x] Milestone status
- [ ] Account Forecasting
    - [x] :pencil: Autoregressive Integrated Moving Average (ARIMA) modeling
    - [x] :pencil: Autoregressive Integrated Moving Average (ARIMA) forecasting
    - [x] :pencil: Maximum Likelihood Estimator (MLE) distribution modeling
    - [x] :pencil: Monte Carlo forecasting
- [x] Assumption Based Forecasting
    - [x] Assumption (savings rate, expense, growth) modeler
- [ ] Investing Forecasting
    - [ ] Index (e.g. [Vanguard](https://investor.vanguard.com/home/)) based asset data
    - [ ] Asset allocation correlation
    - [ ] Asset allocation modeling
    - [ ] Monte Carlo Asset forecasting
- [ ] Visualization
    - [x] Time series plotting
    - [x] Probability Distribution Function (PDF) plotting
- [ ] Report Generation

## Examples

```py
import pfcompute as pf


```

<a name="data-format"></a>
## Data Format
The format needed by `pfcompute` for each set of data is [pandas](http://pandas.pydata.org) `DataFrame`s with the following format:

1. Accounts

    DataFrame of account balances with Date index and (Category, Account Name) multi-columns:

    ```csv
    |        | Cash                         | Investment               | Credit   | Loan      |
    | Date   | Ally Checking | Ally Savings | LendingClub | Betterment | BofA     | Student   |
    | Oct 15 |       1000.00 |  5000.00     |    10000.00 |  30000.00  | -1000.00 | -10000.00 |
    ```

    *Date could be any period... however, currently assumes month end and one row per date.*

2. Transactions

    DataFrame of transaction details with Date index and Field name columns:

    ```csv
    | Date       |  Amount  | Account       | Category | Label |
    | 2015-10-15 |  2000.00 | Ally Checking | Paycheck |    {} |
    | 2015-10-15 | -1000.00 | Ally Checking | Rent     |    {} |
    ```

    *Can have multiple transactions per date*

3. Paychecks

    DataFrame of paycheck details with Date index and Field name columns:

    ```csv
    | Date       |  Total Gross | Tax    | Pre Tax Deductions | Post Tax Deductions | Net Pay |
    | 2015-10-15 |  2000.00     | 500.00 |             500.00 |                 0.0 | 1000.00 |
    ```

    *Can have multiple paychecks per date*

Optional data sets include: Credit Limits and Miscellaneous.  These can be useful to keep track of but may require
additional effort to record.

4. Credit Limits
    DataFrame of account limits with Date index and (Category, Account Name) multi-columns, similar to Account data.

5. Miscellaneous
    DataFrame of whatever Miscellaneous data is applicable with Date index and Field/Account columns, similar to Account data

<a name="data-ideas"></a>
### Data Collections Ideas

#### Account Balances
A Google Sheets of month end account values.

#### Transactions
[Mint](https://mint.com) transaction can be "downloaded" using the following code in the developer console of a typical authenticated browser session (only tested on [Chrome](https://www.google.com/chrome/browser/desktop/)):

```js
// Constants
L = 100;
transactions = [];
offset = 0;
url = 'https://wwws.mint.com/app/getJsonData.xevent?accountId=0&offset={}&task=transactions,txnfilters&rnd=###';

// Download each page of transactions from Mint.com
function getNextData() {
    console.log('offset: ' + offset);
    jQuery.getJSON(url.replace('{}', offset),function( rsp ) {
        data = rsp['set'][0]['data'];
        transactions.push.apply(transactions, data);
        L = data.length;
        offset = offset + 100;
        if (L == 100) {
            getNextData();
        }
    });
}
getNextData();
```

This `javascript` object will need to be copied into a text file and saved (e.g. `transaction.json`).
You can copy a console variable with the following code, then paste (`cmd+v` || `ctrl+v`) into a text editor:

```js
// Send to clipboard
copy(transactions)
```

#### Paychecks
This is the most difficult one... You will have to get dirty and roll your own custom implementation. Assuming you get a `pdf` paycheck, you must create a  `pdf` parser.  The library has an example of this and provides a framework to make is easier.
Good Luck :)

## License
[MIT](https://github.com/tmthydvnprt/pfcompute/blob/master/LICENSE)
