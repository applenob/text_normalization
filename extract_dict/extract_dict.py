# coding=utf-8
# @author: cer
# this script must run with python3
from __future__ import print_function
import pickle as pkl

# -*- coding: utf-8 -*-

import operator
from num2words import num2words
import os
import time

INPUT_PATH = "../input"
self_classes = ["PLAIN", "PUNCT"]
dict_pkl_name = "../output/dict.pkl"


def extract():
    print('extracting start...')

    # Work with primary dataset
    s = time.time()
    file = "en_train.csv"
    print("extracting from file {} ...".format(file))
    train = open(os.path.join(INPUT_PATH, file), encoding='UTF8')
    line = train.readline()
    res = dict()
    total = 0
    not_same = 0
    entry_num = 0
    while 1:
        line = train.readline().strip()
        if line == '':
            break
        total += 1
        pos0 = line.find('"')
        pos = line.find('","')
        class_ = line[pos0+1: pos]
        if class_ not in self_classes:
            entry_num += 1
            text = line[pos + 2:]
            if text[:3] == '","':
                continue
            text = text[1:-1]
            arr = text.split('","')
            if arr[0] != arr[1]:
                not_same += 1
            if arr[0] not in res:
                res[arr[0]] = dict()
                res[arr[0]][arr[1]] = 1
            else:
                if arr[1] in res[arr[0]]:
                    res[arr[0]][arr[1]] += 1
                else:
                    res[arr[0]][arr[1]] = 1
    train.close()
    print(file + ':\tTotal: {}, Have diff value: {}, dict entry num: {} '.
          format(total, not_same, entry_num))
    print("time costs: {}".format(time.time() - s))

    # Work with additional dataset from https://www.kaggle.com/google-nlu/text-normalization
    files = ['output_1.csv', 'output_6.csv', 'output_11.csv', 'output_16.csv',
             'output_21.csv', 'output_91.csv', 'output_96.csv']

    for file in files:
        print("extracting from file {} ...".format(file))
        s1 = time.time()
        train = open(os.path.join(INPUT_PATH, 'tn', file), encoding='UTF8')
        line = train.readline()
        while 1:
            line = train.readline().strip()
            if line == '':
                break
            line = line.replace(',NA,', ',"NA",')
            total += 1
            pos0 = line.find('"')
            pos = line.find('","')
            class_ = line[pos0 + 1: pos]
            if class_ not in self_classes:
                entry_num += 1
                text = line[pos + 2:]
                if text[:3] == '","':
                    continue
                text = text[1:-1]
                arr = text.split('","')
                if arr[0] == '<eos>':
                    continue
                if arr[1] != '<self>':
                    not_same += 1

                if arr[1] == '<self>' or arr[1] == 'sil':
                    arr[1] = arr[0]

                if arr[0] not in res:
                    res[arr[0]] = dict()
                    res[arr[0]][arr[1]] = 1
                else:
                    if arr[1] in res[arr[0]]:
                        res[arr[0]][arr[1]] += 1
                    else:
                        res[arr[0]][arr[1]] = 1
        train.close()
        print(file + ':\tTotal: {}, Have diff value: {}, dict entry num: {} '.
              format(total, not_same, entry_num))
        print("time costs: {}".format(time.time() - s1))
    print("total time costs: {}".format(time.time() - s))
    return res

if __name__ == '__main__':
    big_dict = extract()
    with open(dict_pkl_name, "wb") as f:
        pkl.dump(big_dict, f)
