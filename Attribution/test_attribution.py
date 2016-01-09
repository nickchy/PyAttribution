#!/usr/bin/python
# -*- coding: utf-8 -*-

from PortfolioAttribution import Attribution
import pandas as pd

# initiate Attribution
attr = Attribution()

# ------ test single period ------
rawf1 = ".\\test_data\\test_single.csv"
rawdata1 = pd.read_csv(rawf1)

# input raw data to Attribution class
# each parameter is indicating the column name of corresponding property
attr.input(rawdata1, category='sector', port_returns="port_rt", port_weights="port_wt",
           bench_returns='bench_rt', bench_weights='bench_wt')
result1 = attr.run()
print(result1['summary']) # output is a dict, for single period, it only contains one element 'summary' to storage the result


# ------ test multi-period ------
rawf2 = ".\\test_data\\test_multi.csv"
rawdata2 = pd.read_csv(rawf2)

# input raw data to Attribution class
# each parameter is indicating the column name of corresponding property
attr.input(rawdata2, category='sector', port_returns="port_rt", port_weights="port_wt",
           bench_returns='bench_rt', bench_weights='bench_wt')
result2 = attr.run()
print(result2['summary'])   # for multi-period, use date as key to access the result of each period
