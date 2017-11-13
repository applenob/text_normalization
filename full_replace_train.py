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
class_pred_name = "en_train.csv"
out_file_name = "res_16_train.csv"
labels = ['PLAIN', 'PUNCT', 'DATE', 'LETTERS', 'CARDINAL', 'VERBATIM',
          'DECIMAL', 'MEASURE', 'MONEY', 'ORDINAL', 'TIME', 'ELECTRONIC',
          'DIGIT', 'FRACTION', 'TELEPHONE', 'ADDRESS']


def replace_train():
    out_name = os.path.join(OUTPUT_PATH, out_file_name)
    class_pred_df = pd.read_csv(os.path.join(INPUT_PATH, class_pred_name))
    result = class_pred_df[["before", "after"]]

    after_s = []
    s = time.time()
    for i, row in class_pred_df.iterrows():
        token = str(row["before"])
        # this token is 'PLAIN'
        if row["class"] == 'PLAIN':
            token = replace_plain(token)
            after_s.append(token)
        # this token is 'PUNCT'
        elif row["class"] == 'PUNCT':
            token = replace_puct(token)
            after_s.append(token)
        # this token belongs to other classes
        elif row["class"] == 'DATE':
            token = replace_date(token)
            after_s.append(token)
        elif row["class"] == 'LETTERS':
            token = replace_letters(token)
            after_s.append(token)
        elif row["class"] == 'CARDINAL':
            token = replace_cardinal(token)
            after_s.append(token)
        elif row["class"] == 'VERBATIM':
            token = replace_verbatim(token)
            after_s.append(token)
        elif row["class"] == 'DECIMAL':
            token = replace_decimal(token)
            after_s.append(token)
        elif row["class"] == 'MEASURE':
            token = replace_measure(token)
            after_s.append(token)
        elif row["class"] == 'MONEY':
            token = replace_money(token)
            after_s.append(token)
        elif row["class"] == 'ORDINAL':
            token = replace_ordinal(token)
            after_s.append(token)
        elif row["class"] == 'TIME':
            token = replace_time(token)
            after_s.append(token)
        elif row["class"] == 'ELECTRONIC':
            token = replace_electronic(token)
            after_s.append(token)
        elif row["class"] == 'DIGIT':
            token = replace_digit(token)
            after_s.append(token)
        elif row["class"] == 'FRACTION':
            token = replace_fraction(token)
            after_s.append(token)
        elif row["class"] == 'TELEPHONE':
            token = replace_telephone(token)
            after_s.append(token)
        elif row["class"] == 'ADDRESS':
            token = replace_address(token)
            after_s.append(token)

    print("replacing done!")
    print("time cost: {}".format(time.time() - s))
    print("after:", len(after_s))
    print("test file size: {}".format(result.shape[0]))
    result["pred"] = after_s
    result.to_csv(out_name, index=False)
    correct_num = np.sum(result["pred"] == result["after"])
    print("training file correct rate: {} / {} = {}".format(correct_num, result.shape[0],
                                                            correct_num / result.shape[0]))

if __name__ == '__main__':
    print("start replacing training files...")
    replace_train()
