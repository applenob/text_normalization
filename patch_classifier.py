# coding=utf-8
# @author: cer
# 有一些分类器分错的明显的错误，使用规则矫正。
# 这个脚本跟在分类器脚本后面跑。
from __future__ import print_function
import pandas as pd
import numpy as np

pred_file = "output/class_pred_16.csv"
test_file = "input/en_test.csv"
out_file = "output/class_pred_16_fixed.csv"
labels = ['PLAIN', 'PUNCT', 'DATE', 'LETTERS', 'CARDINAL', 'VERBATIM',
          'DECIMAL', 'MEASURE', 'MONEY', 'ORDINAL', 'TIME', 'ELECTRONIC',
          'DIGIT', 'FRACTION', 'TELEPHONE', 'ADDRESS']
label2index = dict(zip(labels, range(len(labels))))
index2label = dict([(v, k) for k, v in label2index.items()])

test_df = pd.read_csv(test_file)
pred_df = pd.read_csv(pred_file)
pred_df["before"] = test_df["before"]
print("start iterating...")
for i, row in pred_df.iterrows():
    # 1.被误认为是cardinal的实际上的date的年份
    if index2label[row["class_pred"]] == "CARDINAL":
        if row["before"].isdigit() and int(row["before"]) <= 3000 and int(row["before"]) >= 1000:
            # 不能直接修改row，因为row是副本
            pred_df.loc[i, "class_pred"] = label2index["DATE"]


pred_df.to_csv(out_file, index=False)
print("done!")
