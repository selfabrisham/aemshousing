# Notebooks

This folder contains examples jupyter notebooks for using `pccompute`.

- [Get personal income and expense data from FRED data](Get%20personal%20income%20and%20expense%20data%20from%20FRED%20data.ipynb)
    Notebook from extracting personal income and expense data from the total [FRED data download](https://research.stlouisfed.org/fred2/downloaddata/).  The code first parses an index `.csv` to obtain file paths to the desired data, loops thru the `data/` directory to read in each time series `.csv`.  The data is placed into nice pandas `DataFrame`s and finally plotted to quickly test the import.
