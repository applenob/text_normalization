# coding=utf-8
# @author: cer
# this script must run with python3
from __future__ import print_function
from __future__ import absolute_import
from num2words import num2words
import os
import time
import pandas as pd
import numpy as np
import pickle as pkl
from replace_by_rule import *

INPUT_PATH = "input"
OUTPUT_PATH = "output"
# self_classes = ["PLAIN", "PUNCT"]
dict_pkl_name = "dict.pkl"
class_pred_name = "class_pred_16_fixed.csv"
out_file_name = "res_16_1.csv"
labels = ['PLAIN', 'PUNCT', 'DATE', 'LETTERS', 'CARDINAL', 'VERBATIM',
          'DECIMAL', 'MEASURE', 'MONEY', 'ORDINAL', 'TIME', 'ELECTRONIC',
          'DIGIT', 'FRACTION', 'TELEPHONE', 'ADDRESS']


def replace():
    out_name = os.path.join(OUTPUT_PATH, out_file_name)
    class_pred_df = pd.read_csv(os.path.join(OUTPUT_PATH, class_pred_name))
    result = class_pred_df[["id"]]

    after_s = []
    s = time.time()
    for i, row in class_pred_df.iterrows():
        token = str(row["before"])
        # this token is 'PLAIN'
        if labels[int(row["class_pred"])] == 'PLAIN':
            token = replace_plain(token)
            after_s.append(token)
        # this token is 'PUNCT'
        elif labels[int(row["class_pred"])] == 'PUNCT':
            token = replace_puct(token)
            after_s.append(token)
        # this token belongs to other classes
        elif labels[int(row["class_pred"])] == 'DATE':
            token = replace_date(token)
            after_s.append(token)
        elif labels[int(row["class_pred"])] == 'LETTERS':
            token = replace_letters(token)
            after_s.append(token)
        elif labels[int(row["class_pred"])] == 'CARDINAL':
            token = replace_cardinal(token)
            after_s.append(token)
        elif labels[int(row["class_pred"])] == 'VERBATIM':
            token = replace_verbatim(token)
            after_s.append(token)
        elif labels[int(row["class_pred"])] == 'DECIMAL':
            token = replace_decimal(token)
            after_s.append(token)
        elif labels[int(row["class_pred"])] == 'MEASURE':
            token = replace_measure(token)
            after_s.append(token)
        elif labels[int(row["class_pred"])] == 'MONEY':
            token = replace_money(token)
            after_s.append(token)
        elif labels[int(row["class_pred"])] == 'ORDINAL':
            token = replace_ordinal(token)
            after_s.append(token)
        elif labels[int(row["class_pred"])] == 'TIME':
            token = replace_time(token)
            after_s.append(token)
        elif labels[int(row["class_pred"])] == 'ELECTRONIC':
            token = replace_electronic(token)
            after_s.append(token)
        elif labels[int(row["class_pred"])] == 'DIGIT':
            token = replace_digit(token)
            after_s.append(token)
        elif labels[int(row["class_pred"])] == 'FRACTION':
            token = replace_fraction(token)
            after_s.append(token)
        elif labels[int(row["class_pred"])] == 'TELEPHONE':
            token = replace_telephone(token)
            after_s.append(token)
        elif labels[int(row["class_pred"])] == 'ADDRESS':
            token = replace_address(token)
            after_s.append(token)

    print("replacing done!")
    print("time cost: {}".format(time.time() - s))
    print("after:", len(after_s))
    print("test file size: {}".format(result.shape[0]))
    result["after"] = after_s
    result.to_csv(out_name, index=False)


if __name__ == '__main__':
    # print("loading big dict...")
    # with open(os.path.join(OUTPUT_PATH, dict_pkl_name), "rb") as f:
    #     big_dict = pkl.load(f)
    print("start replacing...")
    replace()
