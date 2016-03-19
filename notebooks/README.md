# Notebooks

This folder contains examples [jupyter](https://jupyter.org) notebooks for using `pccompute`.

### [Get average personal income and expense from FRED data](Get%20average%20personal%20income%20and%20expense%20from%20FRED%20data.ipynb)

Notebook for extracting personal income and expense data from the total [FRED data download](https://research.stlouisfed.org/fred2/downloaddata/).  The code first parses an index `.csv` to obtain file paths to the desired data and then loops thru the `data/` directory to read in each time series `.csv`.  The data is placed into nice pandas `DataFrame`s, missing data is interpolated and extrapolated.  The national aggregates for the personal finance categories are obtained and then divided by the national population to determine the average or per capita total for each personal finance category. Finally the data is plotted to quickly test the import. This notebook is placed here to explain how to recreate average/fake/example personal finance data from raw FRED data.

### [Generate Personal Finance Models from Average FRED data](Generate%20Personal%20Finance%20Models%20from%20Average%20FRED data.ipynb)

Notebook for creating statistical models for an average person's financial habits (income and expense) from FRED data.  The code  takes average (per capita) personal finance data, derived from FRED sources, pre packaged into pandas `DataFrame`s of monthly time series for each category and resamples the data to a daily time index.  The daily data is used to fit [ARIMA](https://en.wikipedia.org/wiki/Autoregressive_integrated_moving_average) model to each category.  From these models, general financial daily transactions can be generated.  Some heuristics are enforced on the daily models to better simulate reality (e.g. paycheck type income is often transacted every two weeks)
