# coding=utf-8
# @author: cer
from __future__ import print_function
import pandas as pd
import numpy as np
import sys
sys.path.append("..")

pred_file = "../output/class_pred_16.v2.csv"
test_file = "../input/en_test_2.csv"
baseline_file = "../output/baseline.csv"
res_file = "../output/res_16.v2.csv"
out_file = "compare.csv"
labels = ['PLAIN', 'PUNCT', 'DATE', 'LETTERS', 'CARDINAL', 'VERBATIM',
          'DECIMAL', 'MEASURE', 'MONEY', 'ORDINAL', 'TIME', 'ELECTRONIC',
          'DIGIT', 'FRACTION', 'TELEPHONE', 'ADDRESS']

test_df = pd.read_csv(test_file)
baseline_df = pd.read_csv(baseline_file)
res_df = pd.read_csv(res_file)
pred_df = pd.read_csv(pred_file)
class_pred = list(map(lambda pre: labels[int(pre)], pred_df["class_pred"].values))
test_df["id"] = baseline_df["id"]
compare_df = pd.merge(test_df, baseline_df, on=["id"])
compare_df = pd.merge(compare_df, res_df, on=["id"])
compare_df["class_pred"] = class_pred
diff_df = compare_df[compare_df["after_x"] != compare_df["after_y"]]
diff_df = diff_df[["id", "class_pred", "before", "after_x", "after_y"]]

print("all test entry num: ", res_df.shape[0])
print("diff entry num: ", diff_df.shape[0])

diff_df.to_csv(out_file, index=False)
print("compare file: ", out_file)
