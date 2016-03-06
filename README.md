# pfcompute
Personal Finance library for the Computationally Curious.

## Description
`pfcompute` is a python library for computationally exploring personal finance.  The library provides a computing environment with data structures, common equations/algorithms and convenience functions to calculate, analyze and visualize existing personal finance data. It is *not* meant to be a full service financial app or replace any software used to manage personal finances.  It does *not* collect data. However, once data is provided, it allows a much larger degree of freedom in processing and analyzing financial data than typical personal finance apps supply.

### Interactive Computing
While this library may be used internally to other software, it was intended to be used in a interactive computing fashion with software such as [jupyter](https://jupyter.org).  This type of environment, along with the library, provides a quick and easy way to explore complex data, relations and algorithms.

### Data Sources
Since `pfcompute` does not aggregate or collect it's own data, it requires data to be provided by some other means (e.g. [mint](https://mint.com), [personalcapital](https://personalcapital.com), [ynab](https://youneedabudget.com), [yodlee](https://yodlee.com), a bank, etc.).  It is left up to the user to obtain this data however they wish.  Below are some data collection [suggestions](#data-suggestions).

There are three main data sources assumed to exist by the library: Accounts, Transactions, and Paychecks.  They can really
be in any format (`csv`, `json`, `pdf`) as long as the user writes some method to interpret the data.  It eventually needs to arrive to the library as [pandas](http://pandas.pydata.org) with the following format:

1. Accounts

    DataFrame of account balances with Date index and (Category, Account Name) multi-columns:

    ```
    |        | Cash                         | Investment               | Credit   | Loan      |
    | Date   | Ally Checking | Ally Savings | LendingClub | Betterment | BofA     | Student   |
    | Oct 15 |       1000.00 |  5000.00     |    10000.00 |  30000.00  | -1000.00 | -10000.00 |
    ```

    *Date could be any period... however, currently assumes month end and one row per date.*

2. Transactions

    DataFrame of transaction details with Date index and Field name columns:

    ```
    | Date       |  Amount  | Account       | Category | Label |
    | 2015-10-15 |  2000.00 | Ally Checking | Paycheck |    {} |
    | 2015-10-15 | -1000.00 | Ally Checking | Rent     |    {} |
    ```

    *Can have multiple transactions per date*

3. Paychecks

    DataFrame of paycheck details with Date index and Field name columns:

    ```
    | Date       |  Total Gross | Tax    | Pre Tax Deductions | Post Tax Deductions | Net Pay |
    | 2015-10-15 |  2000.00     | 500.00 |             500.00 |                 0.0 | 1000.00 |
    ```

    *Can have multiple paychecks per date*

Optional data sources include: Credit Limits and Miscellaneous.  These can be useful to keep track of but may require
additional effort to record.

4. Credit Limits
    DataFrame of account limits with Date index and (Category, Account Name) multi-columns, similar to Account data.

5. Miscellaneous
    DataFrame of whatever Miscellaneous data is applicable with Date index and Field/Account columns, similar to Account data

<a name="data-suggestions"></a>
### Data Collections Ideas

#### Account Balances
A Google Sheets of month end account values.

#### Transactions
[Mint](https://mint.com) transaction can be "downloaded" using the following code in the developer console of a typical authenticated browser session (only tested on [Chrome](https://www.google.com/chrome/browser/desktop/)):

```javascript
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

This `javascript` object will need to be copied into a text file and saved (eg. `transaction.json`).
You can copy a console variable with the following code, then paste (cmd+v or ctrl+v) into a text editor:

```
// Send to clipboard (only tested in Chrome)
copy(transactions)
```

#### Paychecks
This is the most difficult one... You will have to get dirty and roll your own custom implementation. Assuming you get a `pdf` paycheck, you must create a  `pdf` parser.  The library has an example of this and provide a framework to make is easier.

## Features

## Examples

```
import pfcompute as pf


```

## License
[MIT](https://github.com/tmthydvnprt/pfcompute/blob/master/LICENSE)
