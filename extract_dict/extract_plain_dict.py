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
dict_pkl_name = "../output/plain_dict.pkl"


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
        if class_ == "PLAIN":
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
            if class_ == "PLAIN":
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
    with open(dict_pkl_name, "wb") as f:
        pkl.dump(res, f)
    print("dict dumped!")


def double_check():
    print("loading first dict ...")
    with open(dict_pkl_name, "rb") as f:
        res = pkl.load(f)

    print('double check start...')
    # Work with primary dataset
    s = time.time()
    file = "en_train.csv"
    print("extracting from file {} ...".format(file))
    train = open(os.path.join(INPUT_PATH, file), encoding='UTF8')
    line = train.readline()
    entry_num = 0
    while 1:
        line = train.readline().strip()
        if line == '':
            break
        pos0 = line.find('"')
        pos = line.find('","')
        class_ = line[pos0 + 1: pos]
        if class_ == "PLAIN":
            text = line[pos + 2:]
            if text[:3] == '","':
                continue
            text = text[1:-1]
            arr = text.split('","')
            if arr[0] in res and arr[0] == arr[1]:
                entry_num += 1
                if arr[0] in res[arr[0]]:
                    res[arr[0]][arr[0]] += 1
                else:
                    res[arr[0]][arr[0]] = 1
    train.close()
    print("double check add {} entries".format(entry_num))
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
            pos0 = line.find('"')
            pos = line.find('","')
            class_ = line[pos0 + 1: pos]
            if class_ == "PLAIN":
                text = line[pos + 2:]
                if text[:3] == '","':
                    continue
                text = text[1:-1]
                arr = text.split('","')
                if arr[0] == '<eos>':
                    continue
                if arr[0] in res and arr[1] == '<self>':
                    entry_num += 1
                    if arr[0] in res[arr[0]]:
                        res[arr[0]][arr[0]] += 1
                    else:
                        res[arr[0]][arr[0]] = 1
        train.close()

        print("time costs: {}".format(time.time() - s1))
    print("double check add {} entries".format(entry_num))
    print("total time costs: {}".format(time.time() - s))
    with open(dict_pkl_name, "wb") as f:
        pkl.dump(res, f)
    print("dict dumped!")


if __name__ == '__main__':
    extract()
    double_check()
