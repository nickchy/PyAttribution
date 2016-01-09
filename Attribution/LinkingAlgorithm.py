#!/usr/bin/python
# -*- coding: utf-8 -*-

import numpy as np

def modified_frongello(rsingle, ls_portret, ls_benchret, portret, benchret, ls_radj):
    """
    Modified Frongello Method. Calculate adjusted attribute at Period T
    Assume periods are t1, t2, ..., T-1, T
    Return numbers are in decimal (10% as 0.1)
    :param rsingle: Original single period attribute at period T
    :param portrt: a list of portfolio returns from t1 to T-1
    :param benchrt: a list of benchmark returns from t1 to T-1
    :param portrt_T: portfolio return at period T
    :param benchrt_T: benchmark return at period T
    :param radj: a list of adjusted attribute from t1 to T-1
    :return: float
    """
    # print(ls_portret)
    # result = rsingle * 0.5 * (np.prod(1 + np.nan_to_num(ls_portret)) + np.prod(1 + np.nan_to_num(ls_benchret))) \
    #          + 0.5 * (portret + benchret) * np.sum(np.nan_to_num(ls_radj))
    result = rsingle * 0.5 * (np.prod(1 + np.array(ls_portret)) + np.prod(1 + np.array(ls_benchret))) \
             + 0.5 * (portret + benchret) * np.sum(np.array(ls_radj))
    return result