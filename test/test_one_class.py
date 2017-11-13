# coding=utf-8
# @author: cer
from __future__ import print_function
import pandas as pd
import numpy as np
import sys
sys.path.append("..")
from replace_by_rule import *


param_dict = {'PLAIN': {"func": replace_plain},
              'PUNCT': {"func": replace_puct},
              'DATE': {"func": replace_date},
              'LETTERS': {"func": replace_letters},
              'CARDINAL': {"func": replace_cardinal},
              'VERBATIM': {"func": replace_verbatim},
              'DECIMAL': {"func": replace_decimal},
              'MEASURE': {"func": replace_measure},
              'MONEY': {"func": replace_money},
              'ORDINAL': {"func": replace_ordinal},
              'TIME': {"func": replace_time},
              'ELECTRONIC': {"func": replace_electronic},
              'DIGIT': {"func": replace_digit},
              'FRACTION': {"func": replace_fraction},
              'TELEPHONE': {"func": replace_telephone},
              'ADDRESS': {"func": replace_address}}


def replace_one_class(target_class):
    train_df = pd.read_csv('../input/en_train.csv')
    labels = train_df["class"].unique()
    # print("labels: ", labels)
    date_df = train_df.loc[train_df["class"] == target_class]
    print("start replacing {} !".format(target_class))
    my_replaces = []
    for one in date_df["before"].values:
        res = param_dict[target_class]["func"](one)
        my_replaces.append(res)
    date_df["my_replaces"] = my_replaces
    print("all entry num: ", date_df.shape[0])
    diff_df = date_df[date_df["after"] != date_df["my_replaces"]]
    print("diff entry num: ", diff_df.shape[0])
    print("error rate: ", float(diff_df.shape[0]) / date_df.shape[0])
    diff_df.to_csv("{}.csv".format(target_class), index=False)


def replace_all_class():
    replace_one_class("PLAIN")
    replace_one_class("PUNCT")
    replace_one_class("DATE")
    replace_one_class("VERBATIM")
    replace_one_class("CARDINAL")
    replace_one_class("LETTERS")
    replace_one_class("DECIMAL")
    replace_one_class("MEASURE")
    replace_one_class("MONEY")
    replace_one_class("ORDINAL")
    replace_one_class("TIME")
    replace_one_class("ELECTRONIC")
    replace_one_class("DIGIT")
    replace_one_class("FRACTION")
    replace_one_class("TELEPHONE")
    replace_one_class("ADDRESS")


if __name__ == '__main__':
    # replace_one_class("PLAIN")
    # replace_one_class("PUNCT")
    replace_one_class("DATE")
    # replace_one_class("VERBATIM")
    # replace_one_class("CARDINAL")
    # replace_one_class("LETTERS")
    # replace_one_class("DECIMAL")
    # replace_one_class("MEASURE")
    # replace_one_class("MONEY")
    # replace_one_class("ORDINAL")
    # replace_one_class("TIME")
    # replace_one_class("ELECTRONIC")
    # replace_one_class("DIGIT")
    # replace_one_class("FRACTION")
    # replace_one_class("TELEPHONE")
    # replace_one_class("ADDRESS")

    # replace_all_class()