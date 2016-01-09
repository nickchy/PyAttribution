#!/usr/bin/python
# -*- coding: utf-8 -*-

from paportfolio import paportfolio
import pandas as pd

def brinson_topdown(portfolio, benchmark, category=None):
    """
    Single period BF(Brinson and Fachler) model with top-down approach.
    Only consider allocation and selection effect, the total effect is the sum of those two
    :param portfolio: paportfolio object
    :param benchmark: paportfolio object
    :param category: str
    :return:
    """
    assert type(portfolio) is paportfolio, "portfolio type is invalid"
    assert type(benchmark) is paportfolio, "benchmark type is invalid"

    if category is None:
        category = "category"

    # total benchmark return
    ret_bench_ttl = benchmark.total_return

    # effects by category
    alloc = (portfolio.weights - benchmark.weights) * (benchmark.returns - ret_bench_ttl)
    select_inter = portfolio.weights * (portfolio.returns - benchmark.returns)
    total = alloc + select_inter

    # total effects
    alloc_ttl = alloc.sum()
    select_inter_ttl = select_inter.sum()
    total_ttl = total.sum()

    result = pd.DataFrame({category: portfolio.category,
                           "allocation": alloc,
                           "selection_interaction": select_inter,
                           "total": total},
                          columns=[category, 'allocation', 'selection_interaction', 'total'])

    result_ttl = pd.DataFrame({category: ['Total'],
                               "allocation": [alloc_ttl],
                               "selection_interaction": [select_inter_ttl],
                               "total": [total_ttl]},
                              columns=[category, 'allocation', 'selection_interaction', 'total'])

    return (result, result_ttl)