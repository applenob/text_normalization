# coding=utf-8
# @author: cer
# 有一些分类器分错的明显的错误，使用规则矫正。
# 这个脚本跟在分类器脚本后面跑。
from __future__ import print_function
import pandas as pd
import numpy as np
import re
import pickle as pkl

pred_file = "output/class_pred_16.v2.csv"
all_pred_file_name = "output/train_pred.v2.csv"
all_output_file_name = "output/train_pred.v2.fixed.2.csv"
train_file = "input/en_train.csv"
test_file = "input/en_test_2.csv"
out_file = "output/class_pred_16_fixed.v2.csv"
labels = ['PLAIN', 'PUNCT', 'DATE', 'LETTERS', 'CARDINAL', 'VERBATIM',
          'DECIMAL', 'MEASURE', 'MONEY', 'ORDINAL', 'TIME', 'ELECTRONIC',
          'DIGIT', 'FRACTION', 'TELEPHONE', 'ADDRESS']
label2index = dict(zip(labels, range(len(labels))))
index2label = dict([(v, k) for k, v in label2index.items()])
with open("output/letter_set.pkl", "rb") as f:
    letter_set = pkl.load(f)


def is_com(token):
    token = str(token)
    pt = re.compile(r"\.[a-zA-Z]{2,}")
    return True if pt.search(token) else False


def is_year(token):
    token = str(token)
    return token.isdigit() and len(token) == 4 and 1000 <= int(token) <= 3000


def patch():
    test_df = pd.read_csv(test_file)
    pred_df = pd.read_csv(pred_file)
    pred_df["before"] = test_df["before"]
    print("start iterating...")
    data_num = pred_df.shape[0]
    count = 0
    for i, row in pred_df.iterrows():
        # 1.被误认为是cardinal的实际上的date的年份
        if index2label[row["class_pred"]] == "CARDINAL":
            if is_year(row["before"]) and i + 1 < data_num \
                    and pred_df.loc[i + 1, "before"] not in ["-", "/", ":", "\""]:
                # 不能直接修改row，因为row是副本
                pred_df.loc[i, "class_pred"] = label2index["DATE"]
                count += 1
        elif index2label[row["class_pred"]] == "PLAIN":
            # 2.被误认为是plain的实际上的electronic的网站
            if is_com(row["before"]):
                pred_df.loc[i, "class_pred"] = label2index["ELECTRONIC"]
                count += 1
            # 3.被误认为是plain的实际上是letters
            elif row["before"] in letter_set:
                pred_df.loc[i, "class_pred"] = label2index["LETTERS"]
                count += 1
        elif index2label[row["class_pred"]] == "LETTERS":
            if row["before"] not in letter_set:
                pred_df.loc[i, "class_pred"] = label2index["PLAIN"]
                count += 1
    print("changed row num: ", count)
    pred_df.to_csv(out_file, index=False)
    print("save fixed prediction to file: ", out_file)
    print("done!")


def patch_train_file():
    pred_df = pd.read_csv(all_pred_file_name)
    print("start iterating...")
    data_num = pred_df.shape[0]
    count = 0
    for i, row in pred_df.iterrows():
        # 1.被误认为是cardinal的实际上的date的年份
        if row["class_pred"] == "CARDINAL":
            if is_year(row["before"]):
            # if is_year(row["before"]) and i + 1 < data_num and pred_df.loc[i + 1, "before"] not in ["-", "/"]:
                # 不能直接修改row，因为row是副本
                pred_df.loc[i, "class_pred"] = "DATE"
                count += 1
        elif row["class_pred"] == "PLAIN":
            # 2.被误认为是plain的实际上的electronic的网站
            if is_com(row["before"]):
                pred_df.loc[i, "class_pred"] = "ELECTRONIC"
                count += 1
            # 3.被误认为是plain的实际上是letters
            elif row["before"] in letter_set:
                pred_df.loc[i, "class_pred"] = "LETTERS"
                count += 1
        elif row["class_pred"] == "LETTERS":
            if row["before"] not in letter_set:
                pred_df.loc[i, "class_pred"] = "PLAIN"
                count += 1
    print("changed row num: ", count)
    pred_df.to_csv(all_output_file_name, index=False)
    print("save fixed prediction to file: ", all_output_file_name)
    print("done!")


if __name__ == '__main__':
    patch()
    # patch_train_file()

