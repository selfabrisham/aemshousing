#!/usr/bin/bash

# remove trailing whitespace
find . -name '*.py' | xargs sed -i '' -e's/[ ^I]*$//'

# lint project
echo '' > linting_report.txt
echo 'pf Linting Report' >> linting_report.txt
echo `date "+%Y-%m-%d %H:%M:%S %z"` >> linting_report.txt
echo '=========================================' >> linting_report.txt
echo '' >> linting_report.txt
pylint pf >> linting_report.txt

echo 'project linted'
