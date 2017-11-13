# coding=utf-8
# @author: cer
from __future__ import print_function
import pandas as pd
import numpy as np
import os
import pickle
import gc
import xgboost as xgb
import re
from sklearn.model_selection import train_test_split
from sklearn.utils import class_weight

max_num_features = 10
pad_size = 1
boundary_letter = -1
space_letter = 0
round_num = 150
train_file_name = "input/en_train.csv"
test_file_name = "input/en_test.csv"
model_file_name = "model_vars/train16.v2.model"
model_dump_name = "model_vars/dump.train16.v2.txt"
class_pred_file_name = "output/class_pred_16.v2.csv"
valid_compare_file_name = "output/valid_compare_16.v2.csv"

# max_data_size = 320000
param = {'objective': 'multi:softmax',
         'eta': '0.2',
         'max_depth': 11,
         'silent': 1,
         'nthread': -1,
         'num_class': 16,
         'eval_metric': 'merror'}
labels = ['PLAIN', 'PUNCT', 'DATE', 'LETTERS', 'CARDINAL', 'VERBATIM',
          'DECIMAL', 'MEASURE', 'MONEY', 'ORDINAL', 'TIME', 'ELECTRONIC',
          'DIGIT', 'FRACTION', 'TELEPHONE', 'ADDRESS']
weight_dict = {'PLAIN': 0.01,
               'PUNCT': 1,
               'DATE': 1,
               'LETTERS': 1,
               'CARDINAL': 1,
               'VERBATIM': 1,
               'DECIMAL': 1,
               'MEASURE': 1,
               'MONEY': 1,
               'ORDINAL': 1,
               'TIME': 1,
               'ELECTRONIC': 1,
               'DIGIT': 1,
               'FRACTION': 1,
               'TELEPHONE': 1,
               'ADDRESS': 1}


def context_window_transform(data, pad_size):
    """每个词加上前面一个和后面一个词，中间用-1隔开"""
    pre = np.zeros(max_num_features)
    pre = [pre for x in np.arange(pad_size)]
    data = pre + data + pre
    neo_data = []
    for i in np.arange(len(data) - pad_size * 2):
        row = []
        for x in data[i : i + pad_size * 2 + 1]:
            row += [boundary_letter]
            row += x.tolist()
        row += [boundary_letter]
        neo_data.append(row)
    return neo_data


def get_feas(data_df):
    # 特征工程
    feas = []
    # 1.token的长度
    fea_len = data_df["before"].apply(lambda token: len(str(token))).values
    feas.append(fea_len)
    # 2.是否是每句话的第一个token
    fea_start = data_df["token_id"].apply(lambda token_id: 1 if int(token_id) == 0 else 0)
    feas.append(fea_start)
    fea_x = np.transpose(np.vstack(feas))
    return fea_x


def train(with_valid=True, save=True):
    print("open data files ...")
    train_df = pd.read_csv(train_file_name)

    print("data processing...")
    x_data = []
    # 将类别数字化
    # labels = train_df["class"].unique()
    class2index = dict(zip(labels, range(len(labels))))
    y_data = map(lambda c: class2index[c], train_df['class'].values)
    gc.collect()
    # 每个目标词用组成这个词的所有字符的ascii码表示，并padding
    for x in train_df['before'].values:
        x_row = np.ones(max_num_features, dtype=int) * space_letter
        for xi, i in zip(list(str(x)), np.arange(max_num_features)):
            x_row[i] = ord(xi)
        x_data.append(x_row)

    fea_x = get_feas(train_df)

    del train_df
    gc.collect()

    x_data_context = np.array(context_window_transform(x_data, pad_size))
    del x_data
    gc.collect()
    # x_data_context_a = np.array(x_data_context)
    x_data_context_a = np.hstack([x_data_context, fea_x])
    y_data_a = np.array(y_data)

    # 计算每个类别的权重
    print(np.unique(y_data_a))
    index_weight_dict = dict([(class2index[k], v)for k, v in weight_dict.items()])
    class_weights = class_weight.compute_class_weight("balanced", np.arange(16), y_data_a)
    weights = np.array(map(lambda y: class_weights[y], y_data_a))
    # print("weights: ", weights[:100])
    print('Total number of samples:', len(x_data_context))

    print('x_data sample:')
    print(x_data_context[0])
    print('y_data sample:')
    print(y_data[0])
    print('labels:')
    print(labels)

    del x_data_context
    del y_data
    gc.collect()

    if with_valid:
        x_train, x_valid, y_train, y_valid = train_test_split(x_data_context_a, y_data_a,
                                                              test_size=0.01, random_state=2017)
        del x_data_context_a
        del y_data_a
        gc.collect()

        print("forming dmatrix...")
        dtrain = xgb.DMatrix(x_train, label=y_train)
        dvalid = xgb.DMatrix(x_valid, label=y_valid)
        watchlist = [(dvalid, 'valid'), (dtrain, 'train')]

        del x_train
        del y_train
        gc.collect()

        print("training start...")
        print("params: ", param)
        model = xgb.train(param, dtrain, round_num, watchlist, early_stopping_rounds=20,
                          verbose_eval=10)
    else:
        dtrain = xgb.DMatrix(x_data_context_a, label=y_data_a)
        watchlist = [(dtrain, 'train')]
        del x_data_context_a
        del y_data_a
        gc.collect()
        model = xgb.train(param, dtrain, round_num, watchlist, early_stopping_rounds=20,
                          verbose_eval=10)
    if save:
        model.save_model(model_file_name)
        model.dump_model(model_dump_name)


def test():
    test_df = pd.read_csv(test_file_name)
    # 每个目标词用组成这个词的所有字符的ascii码表示，并padding
    print("loading test data ...")
    x_data = []
    for x in test_df['before'].values:
        x_row = np.ones(max_num_features, dtype=int) * space_letter
        for xi, i in zip(list(str(x)), np.arange(max_num_features)):
            x_row[i] = ord(xi)
        x_data.append(x_row)

    fea_x = get_feas(test_df)
    x_data_context = np.array(context_window_transform(x_data, pad_size))
    # x_data_context_a = np.array(x_data_context)
    x_data_context_a = np.hstack([x_data_context, fea_x])
    dtest = xgb.DMatrix(x_data_context_a)
    print("loading model ...")
    bst = xgb.Booster(param)  # init model
    bst.load_model(model_file_name)
    print("start predicting ...")
    ypred = bst.predict(dtest)
    print("ypred:", type(ypred), np.shape(ypred))
    print(test_df.shape)
    print(test_df["sentence_id"].values.shape, test_df["sentence_id"].values.dtype)
    ids_a = np.array(map(lambda tup: str(tup[0]) + "_" + str(tup[1]),
                         zip(test_df["sentence_id"].values,
                             test_df["token_id"].values)))
    print("ids_a: ", ids_a.shape)
    test_df["id"] = ids_a
    class_df = test_df[["id", "before"]]
    class_df["class_pred"] = ypred
    class_df.to_csv(class_pred_file_name, index=False)


def compare_valid_data_pred():
    print("open data files ...")
    train_df = pd.read_csv(train_file_name)

    print("data processing...")
    x_data = []

    class2index = dict(zip(labels, range(len(labels))))
    index2class = dict(zip(range(len(labels)), labels))
    y_data = map(lambda c: class2index[c], train_df['class'].values)
    gc.collect()
    # 每个目标词用组成这个词的所有字符的ascii码表示，并padding
    before = train_df["before"].values
    for x in before:
        x_row = np.ones(max_num_features, dtype=int) * space_letter
        for xi, i in zip(list(str(x)), np.arange(max_num_features)):
            x_row[i] = ord(xi)
        x_data.append(x_row)

    fea_x = get_feas(train_df)

    del train_df
    gc.collect()

    x_data_context = np.array(context_window_transform(x_data, pad_size))
    del x_data
    gc.collect()
    # x_data_context_a = np.array(x_data_context)
    x_data_context_a = np.hstack([x_data_context, fea_x])
    y_data_a = np.array(y_data)
    del x_data_context
    del y_data
    gc.collect()

    x_train, x_valid, y_train, y_valid, before_train, before_valid = train_test_split(x_data_context_a, y_data_a, before,
                                                          test_size=0.05, random_state=2017)
    del x_data_context_a
    del y_data_a
    del x_train
    del y_train
    del before_train
    gc.collect()

    print("forming dmatrix...")
    dvalid = xgb.DMatrix(x_valid, label=y_valid)
    print("loading model ...")
    bst = xgb.Booster(param)  # init model
    bst.load_model(model_file_name)
    print("start predicting ...")
    ypred = bst.predict(dvalid)
    print("ypred:", type(ypred), np.shape(ypred))
    valid_df = pd.DataFrame({"before": before_valid})
    valid_df["true"] = list(map(lambda y: index2class[y], y_valid))
    valid_df["class_pred"] = list(map(lambda y: index2class[y], ypred))
    diff_df = valid_df.loc[valid_df["true"] != valid_df["class_pred"]]
    diff_df.to_csv(valid_compare_file_name, index=False)


if __name__ == '__main__':
    train()
    # train(with_valid=False)
    # test()
    # compare_valid_data_pred()