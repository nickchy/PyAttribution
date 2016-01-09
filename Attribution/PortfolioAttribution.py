#!/usr/bin/python
# -*- coding: utf-8 -*-

from paportfolio import paportfolio
import SinglePeriodMethod as sm
import LinkingAlgorithm as la
import pandas as pd
import numpy as np

class Attribution:
    """
    Portfolio attribution analysis is to decompose a portfolio performance into several attributions in order to explain
    the impact of various portfolio management decisions.

    The allocation effect is the difference weights of categories you put in your portfolio and your benchmark.
    The higher the value is, the wiser your allocation decision is.
    The selection effect is the difference returns of categories you get from your portfolio and your benchmark.
    The reason that causes the difference is the different securities you choose for your portfolio from your
    benchmark. The higher the value is, the wiser your selection decision is.
    The interaction effect is the residual effect besides allocation and selection. Sometimes it is considered
    with selection effect together.
    """
    def __init__(self, single_period='brinson_topdown', linking_algorithm='modified_frongello'):
        self.single = single_period
        self.linking = linking_algorithm

        # storage data
        self.multi = False
        self.outdata = {}
        self.periods = []
        self.category_name = None
        # security-level portfolio holder
        self.portfolio_sec = {}
        self.benchmark_sec = {}
        # category-level portfolio holder
        self.portfolio_cate = {}
        self.benchmark_cate = {}

    def _reset(self):
        """
        reset storage data
        """
        self.multi = False
        self.outdata = {}
        self.periods = []
        self.category_name = None
        # security-level portfolio holder
        self.portfolio_sec = {}
        self.benchmark_sec = {}
        # category-level portfolio holder
        self.portfolio_cate = {}
        self.benchmark_cate = {}

    def input(self, dfdata, category="category", port_returns="returns", port_weights="portfolio",
              bench_returns="returns", bench_weights="benchmark", period='date'):
        """
        Input one dataframe object with portfolio and benchmark data merged together
        For a single dataframe input, assume weight columns are different for portfolio and benchmark.
        If return columns are same, use weights to differentiate between portfolio returns and benchmark returns.
        :param dfdata: dataframe
        """
        assert type(dfdata) is pd.DataFrame, "dfdata type is invalid"

        self._reset()

        self.category_name = category
        if period in dfdata.columns:
            self.periods = dfdata[period].unique()
        if len(self.periods) > 1:
            self.multi = True
            for dt in self.periods:
                tmp = dfdata[dfdata[period] == dt]
                df_category = tmp[category]
                port_wt = tmp[port_weights]
                bench_wt = tmp[bench_weights]
                port_rt = tmp[port_returns].copy()
                bench_rt = tmp[bench_returns].copy()
                port_rt[port_wt == 0] = 0
                bench_rt[bench_wt == 0] = 0
                self.portfolio_sec[dt] = paportfolio(port_wt, port_rt, df_category, period=dt)
                self.benchmark_sec[dt] = paportfolio(bench_wt, bench_rt, df_category, period=dt)
        else:
            df_category = dfdata[category]
            port_wt = dfdata[port_weights]
            bench_wt = dfdata[bench_weights]
            port_rt = dfdata[port_returns].copy()
            bench_rt = dfdata[bench_returns].copy()
            port_rt[port_wt == 0] = 0
            bench_rt[bench_wt == 0] = 0
            self.portfolio_sec = paportfolio(port_wt, port_rt, df_category)
            self.benchmark_sec = paportfolio(bench_wt, bench_rt, df_category)

    def input_raw(self, portfolio, benchmark, key="index", category="category",
                  port_returns="returns", port_weights="weights",
              bench_returns="returns", bench_weights="weights", period='date'):
        """
        Input two dataframe obejcct with portfolio and benchmark as separate object
        :param portfolio: dataframe
        :param benchmark: dataframe
        :param key: merge key, default as index
        """
        pass

    def input_aggregated(self, dfdata, category="category", port_returns="port_returns", port_weights="port_weights",
              bench_returns="bench_returns", bench_weights="bench_weights", period='date'):
        """
        Input aggregated dataframe object
        :param dfdata: dataframe
        """
        pass

    def run(self):
        # aggregate security level to category level
        if self.multi:
            # check if it is already category level
            all_category = self.portfolio_sec[list(self.portfolio_sec.keys())[0]].category
            unique_category = self.portfolio_sec[list(self.portfolio_sec.keys())[0]].unique_category.tolist()
            if len(all_category) == len(set(all_category)):
                self.portfolio_cate = self.portfolio_sec
                self.benchmark_cate = self.benchmark_sec
            else:
                for dt in self.periods:
                    self.portfolio_cate[dt] = self.portfolio_sec[dt].category_to_paportfolio()
                    self.benchmark_cate[dt] = self.benchmark_sec[dt].category_to_paportfolio()
        else:
            # check if it is already category level
            all_category = self.portfolio_sec.category.tolist()
            unique_category = self.portfolio_sec.unique_category.tolist()
            if len(all_category) == len(set(all_category)):
                self.portfolio_cate = self.portfolio_sec
                self.benchmark_cate = self.benchmark_sec
            else:
                self.portfolio_cate = self.portfolio_sec.category_to_paportfolio()
                self.benchmark_cate = self.benchmark_sec.category_to_paportfolio()
        # apply method
        if self.single is 'brinson_topdown' and self.linking is 'modified_frongello':
            self._calculate_brinson_topdown_modified_frongello(unique_category)
        return self.outdata

    def _calculate_brinson_topdown_modified_frongello(self, category=None):
        """
        Assume category are same and unique for both portfolio and benchmark, and consistent through the periods
        :param category: a list contains all category components
        """
        if self.multi:
            # storage for different effects
            # for total effect of each period
            ls_alloc = [0.0]
            ls_select_inter = [0.0]
            ls_total = [0.0]
            # for category-level effect of each period
            dict_alloc = {}
            dict_select_inter = {}
            dict_total = {}
            for cate in category:
                dict_alloc[cate] = [0.0]
                dict_select_inter[cate] = [0.0]
                dict_total[cate] = [0.0]
            # for portfolio and benchmark returns of each period
            ls_portret = [0.0]
            ls_benchret = [0.0]
            for dt in sorted(self.periods):
                # calc single period atrribute at period dt
                single_pa = sm.brinson_topdown(self.portfolio_cate[dt], self.benchmark_cate[dt], self.category_name)
                single_cate = single_pa[0]
                single_ttl = single_pa[1]
                self.outdata[dt] = single_pa[0].append(single_pa[1], ignore_index=True)
                # calc portfolio and benchmark return at period dt
                portret = self.portfolio_cate[dt].total_return
                benchret = self.benchmark_cate[dt].total_return
                # link up
                # total level
                ls_alloc.append(la.modified_frongello(float(single_ttl['allocation']), ls_portret, ls_benchret,
                                                      portret, benchret, ls_alloc))
                ls_select_inter.append(la.modified_frongello(float(single_ttl['selection_interaction']), ls_portret, ls_benchret,
                                                             portret, benchret, ls_select_inter))
                ls_total.append(la.modified_frongello(float(single_ttl['total']), ls_portret, ls_benchret,
                                                      portret, benchret, ls_total))
                # category level
                for cate in category:
                    dict_alloc[cate].append(la.modified_frongello(float(single_cate.loc[single_cate[self.category_name]
                                                                                        == cate, 'allocation']),
                                                                  ls_portret, ls_benchret, portret, benchret,
                                                                  dict_alloc[cate]))
                    dict_select_inter[cate].append(la.modified_frongello(float(single_cate.loc[single_cate[self.category_name]
                                                                                        == cate, 'selection_interaction']),
                                                                  ls_portret, ls_benchret, portret, benchret,
                                                                  dict_select_inter[cate]))
                    dict_total[cate].append(la.modified_frongello(float(single_cate.loc[single_cate[self.category_name]
                                                                                        == cate, 'total']),
                                                                  ls_portret, ls_benchret, portret, benchret,
                                                                  dict_total[cate]))
                # add current return to portfolio return list
                ls_portret.append(portret)
                ls_benchret.append(benchret)

                print('%s is done.' % (str(dt)))

            # sum up by category
            cate_alloc = pd.DataFrame.from_dict(dict_alloc, orient='index').sum(axis=1)
            cate_select_inter = pd.DataFrame.from_dict(dict_select_inter, orient='index').sum(axis=1)
            cate_total = pd.DataFrame.from_dict(dict_total, orient='index').sum(axis=1)
            result = pd.concat([cate_alloc, cate_select_inter, cate_total], axis=1)
            result = result.reindex(category).reset_index()
            result.columns = [self.category_name, 'allocation', 'selection_interaction', 'total']
            # sum up by total
            # result_ttl = pd.DataFrame({self.category_name: "Total",
            #                            "allocation": [np.sum(np.nan_to_num(ls_alloc))],
            #                            "selection_interaction": [np.sum(np.nan_to_num(ls_select_inter))],
            #                            "total": [np.sum(np.nan_to_num(ls_total))]},
            #                           columns=[self.category_name, 'allocation', 'selection_interaction', 'total'])
            result_ttl = pd.DataFrame({self.category_name: "Total",
                                       "allocation": [np.sum(np.array(ls_alloc))],
                                       "selection_interaction": [np.sum(np.array(ls_select_inter))],
                                       "total": [np.sum(np.array(ls_total))]},
                                      columns=[self.category_name, 'allocation', 'selection_interaction', 'total'])
            self.outdata['summary'] = result.append(result_ttl, ignore_index=True)
            # self.outdata = (result, result_ttl)
        else:
            result = sm.brinson_topdown(self.portfolio_cate, self.benchmark_cate, self.category_name)
            self.outdata['summary'] = result[0].append(result[1], ignore_index=True)