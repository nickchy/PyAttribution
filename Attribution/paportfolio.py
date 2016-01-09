#!/usr/bin/python
# -*- coding: utf-8 -*-

import pandas as pd

class portfolio:
    """
    basic class
    """
    pass

class paportfolio(portfolio):
    """
    Assume return numbers and weight numbers are in decimal (10% as 0.1)
    Portfolio Attribution portfolio includes:
    -- weights
    -- returns
    -- periods
    -- identity for stocks
    -- category(e.g. sector, quartile,...)
    """
    def __init__(self, weights, returns, category=None, period=None):
        """
        Each component is pandas Series with index as key
        """
        assert type(weights) is pd.Series, "weights type is not pandas.Series"
        assert type(returns) is pd.Series, "returns type is not pandas.Series"

        self.weights = weights
        self.returns = returns

        if category is None:
            self.category = pd.Series(self.weights.index)
            self.category_name = 'category'
        else:
            self.category = category
            if self.category.name is None:
                self.category_name = 'category'
            else:
                self.category_name = self.category.name
        self.unique_category = self.category.unique()
        self.period = period

    @property
    def data(self):
        """
        Merge multiple data series into one dataframe
        :return: DataFrame
        """
        dfdata = pd.concat([self.weights, self.returns, self.category], axis=1)
        dfdata.columns = ['weights', 'returns', self.category_name]
        if self.period is not None:
            dfdata['date'] = self.period
        return dfdata

    @property
    def total_weight(self):
        return self.weights.sum()

    @property
    def total_return(self):
        return (self.weights * self.returns).sum()

    @property
    def weights_by_category(self):
        """
        Calculate weight by category
        :return:
        """
        cate_weights = {}
        for cate in self.unique_category:
            cate_weights[cate] = self.weights[self.category == cate].sum()
        return pd.Series(cate_weights, index=self.unique_category)

    @property
    def returns_by_category(self):
        """
        Calculate category level returns and weights
        :return:
        """
        cate_weights = self.weights_by_category
        cate_returns = {}
        for cate in self.unique_category:
            if cate_weights[cate] == 0:
                cate_returns[cate] = 0
            else:
                cate_returns[cate] = (self.returns[self.category == cate] *
                                      self.weights[self.category == cate]).sum()/cate_weights[cate]
        return pd.Series(cate_returns, index=self.unique_category)

    def category_to_paportfolio(self):
        """
        Aggregate portfolio by category and construct a paportfolio object for it
        :return: paportfolio
        """
        data = pd.concat([self.weights_by_category, self.returns_by_category], axis=1)
        data = data.reset_index()
        data.columns = [self.category_name, 'weights', 'returns']
        return paportfolio(data['weights'], data['returns'], data[self.category_name])

