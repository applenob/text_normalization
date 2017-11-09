# coding=utf-8
# @author: cer
# this script must run with python3
from __future__ import print_function

import operator
from num2words import num2words
import os
import time
import pandas as pd
import numpy as np
import pickle as pkl

INPUT_PATH = "input"
OUTPUT_PATH = "output"
self_classes = ["PLAIN", "PUNCT"]
dict_pkl_name = "dict.pkl"
plain_dict_name = "plain_dict.pkl"
class_pred_name = "class_pred_3.csv"


def replace(big_dict, plain_dict):
    sdict = {}
    sdict['km2'] = 'square kilometers'
    sdict['km'] = 'kilometers'
    sdict['kg'] = 'kilograms'
    sdict['lb'] = 'pounds'
    sdict['dr'] = 'doctor'
    sdict['m²'] = 'square meters'
    SUB = str.maketrans("₀₁₂₃₄₅₆₇₈₉", "0123456789")
    SUP = str.maketrans("⁰¹²³⁴⁵⁶⁷⁸⁹", "0123456789")
    OTH = str.maketrans("፬", "4")

    out_name = os.path.join(OUTPUT_PATH, 'baseline3_en.csv')
    class_pred_df = pd.read_csv(os.path.join(OUTPUT_PATH, class_pred_name))
    result = class_pred_df[["id"]]

    after_s = []
    s = time.time()
    for i, row in class_pred_df.iterrows():
        token = str(row["before"])
        # this token is 'PLAIN'
        if row["class_pred"] == 0:
            if token not in plain_dict:
                after_s.append(token)
            else:
                srtd = sorted(plain_dict[token].items(), key=operator.itemgetter(1), reverse=True)
                after_s.append(srtd[0][0])
        # this token is 'PUNCT'
        elif row["class_pred"] == 1:
            after_s.append(token)
        # this token belongs to other classes
        else:
            # lookup the dict
            if row["before"] in big_dict:
                srtd = sorted(big_dict[token].items(), key=operator.itemgetter(1), reverse=True)
                after_s.append(srtd[0][0])
            else:
                # check if the token is a num like "123,456"
                if len(token) > 1:
                    val = token.split(',')
                    if len(val) == 2 and val[0].isdigit and val[1].isdigit:
                        token = ''.join(val)
                if token.isdigit():
                    srtd = token.translate(SUB)
                    srtd = srtd.translate(SUP)
                    srtd = srtd.translate(OTH)
                    after_s.append(num2words(float(srtd)))
                # check if the token is a num like "123 456"
                elif len(token.split(' ')) > 1:
                    val = token.split(' ')
                    for i, v in enumerate(val):
                        if v.isdigit():
                            srtd = v.translate(SUB)
                            srtd = srtd.translate(SUP)
                            srtd = srtd.translate(OTH)
                            val[i] = num2words(float(srtd))
                        elif v in sdict:
                            val[i] = sdict[v]
                    after_s.append(' '.join(val))
                else:
                    after_s.append(' '.join(token))
            # after_s.append("")

    print("replacing done!")
    print("time cost: {}".format(time.time() - s))
    print("after:", len(after_s))
    print("test file size: {}".format(result.shape[0]))
    result["after"] = after_s
    result.to_csv(out_name, index=False)


if __name__ == '__main__':
    print("loading big dict...")
    with open(os.path.join(OUTPUT_PATH, dict_pkl_name), "rb") as f:
        big_dict = pkl.load(f)
    with open(os.path.join(OUTPUT_PATH, plain_dict_name), "rb") as f:
        plain_dict = pkl.load(f)
    print("start replacing...")
    replace(big_dict, plain_dict)
