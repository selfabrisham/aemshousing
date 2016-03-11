# Notebooks

This folder contains examples jupyter notebooks for using `pccompute`.

### [Get average personal income and expense from FRED data](Get%20average%20personal%20income%20and%20expense%20from%20FRED%20data.ipynb)

Notebook from extracting personal income and expense data from the total [FRED data download](https://research.stlouisfed.org/fred2/downloaddata/).  The code first parses an index `.csv` to obtain file paths to the desired data and then loops thru the `data/` directory to read in each time series `.csv`.  The data is placed into nice pandas `DataFrame`s, missing data is interpolated and finally plotted to quickly test the import.
