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

max_num_features = 10
pad_size = 1
boundary_letter = -1
space_letter = 0
# max_data_size = 320000
param = {'objective': 'multi:softmax',
             'eta': '0.3',
             'max_depth': 10,
             'silent': 1,
             'nthread': -1,
             # 'num_class':num_class,
             'num_class': 3,
             'eval_metric': 'merror'}


def context_window_transform(data, pad_size):
    """每个词加上前面一个和后面一个词，中间用-1隔开"""
    pre = np.zeros(max_num_features)
    pre = [pre for x in np.arange(pad_size)]
    data = pre + data + pre
    neo_data = []
    for i in np.arange(len(data) - pad_size * 2):
        row = []
        for x in data[i: i + pad_size * 2 + 1]:
            row += [boundary_letter]
            row += x.tolist()
        row += [boundary_letter]
        neo_data.append(row)
    return neo_data


def train(with_valid=True):
    print("open data files ...")
    train_df = pd.read_csv('input/en_train.csv')

    print("data processing...")
    x_data = []
    # 将类别数字化
    # y_data = pd.factorize(train_df['class'])
    # labels = y_data[1]
    # y_data = y_data[0]
    labels = train_df["class"].unique()
    class2index = dict(zip(labels, range(len(labels))))
    for k in class2index:
        if k == "PLAIN":
            class2index[k] = 0
        elif k == "PUNCT":
            class2index[k] = 1
        else:
            class2index[k] = 2

    y_data = map(lambda c: class2index[c], train_df['class'].values)
    gc.collect()
    # 每个目标词用组成这个词的所有字符的ascii码表示，并padding
    for x in train_df['before'].values:
        x_row = np.ones(max_num_features, dtype=int) * space_letter
        for xi, i in zip(list(str(x)), np.arange(max_num_features)):
            x_row[i] = ord(xi)
        x_data.append(x_row)
    del train_df
    gc.collect()

    x_data_context = np.array(context_window_transform(x_data, pad_size))
    del x_data
    gc.collect()
    x_data_context_a = np.array(x_data_context)
    y_data_a = np.array(y_data)

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
        x_train, x_valid, y_train, y_valid= train_test_split(x_data_context_a, y_data_a,
                                                              test_size=0.1, random_state=2017)
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
        model = xgb.train(param, dtrain, 70, watchlist, early_stopping_rounds=20,
                          verbose_eval=10)
    else:
        dtrain = xgb.DMatrix(x_data_context_a, label=y_data_a)
        del x_data_context_a
        del y_data_a
        gc.collect()
        model = xgb.train(param, dtrain, 70, early_stopping_rounds=20,
                          verbose_eval=10)
    model.save_model('model_vars/train3.model')
    model.dump_model('model_vars/dump.train3.txt')


def test(model_file='model_vars/train3.model'):
    test_df = pd.read_csv('input/en_test.csv')
    # 每个目标词用组成这个词的所有字符的ascii码表示，并padding
    x_data = []
    for x in test_df['before'].values:
        x_row = np.ones(max_num_features, dtype=int) * space_letter
        for xi, i in zip(list(str(x)), np.arange(max_num_features)):
            x_row[i] = ord(xi)
        x_data.append(x_row)

    x_data_context = np.array(context_window_transform(x_data, pad_size))
    x_data_context_a = np.array(x_data_context)
    dtest = xgb.DMatrix(x_data_context_a)

    bst = xgb.Booster(param)  # init model
    bst.load_model(model_file)
    ypred = bst.predict(dtest)
    print("ypred:", type(ypred), np.shape(ypred))
    print(test_df.shape)
    # test_df["id"] = test_df[["sentence_id", "token_id"]].apply(lambda row: axis=1)
    print(test_df["sentence_id"].values.shape, test_df["sentence_id"].values.dtype)
    ids_a = np.array(map(lambda tup: str(tup[0]) + "_" + str(tup[1]),
                         zip(test_df["sentence_id"].values,
                             test_df["token_id"].values)))
    print("ids_a: ", ids_a.shape)
    test_df["id"] = ids_a
    # test_df.drop(["sentence_id", "token_id"])
    class_df = test_df[["id", "before"]]
    class_df["class_pred"] = ypred
    # class_df = class_df[["id", "before", "class_pred"]]
    class_df.to_csv("output/class_pred_3.csv", index=False)


if __name__ == '__main__':
    train(with_valid=False)
    # test()
