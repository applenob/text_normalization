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
dict_pkl_name = "../output/year_dict_big.pkl"


# def is_year(token):
#     return token.isdigit() and len(token) == 4 and 1000 <= int(token) <= 3000

def is_year(token):
    return token.isdigit() and 2 <= len(token) <= 4 and int(token) <= 3000


def extract():
    print('extracting start...')

    # Work with primary dataset
    s = time.time()
    file_name = "en_train.csv"
    print("extracting from file {} ...".format(file_name))
    train = open(os.path.join(INPUT_PATH, file_name), encoding='UTF8')
    train.readline()
    res = {}
    total = 0
    entry_num = 0
    while 1:
        line = train.readline().strip()
        if line == '':
            break
        total += 1
        pos0 = line.find('"')
        pos = line.find('","')
        class_ = line[pos0+1: pos]
        text = line[pos + 2:]
        if text[:3] == '","':
            continue
        text = text[1:-1]
        arr = text.split('","')
        if is_year(arr[0]):
            entry_num += 1
            if arr[0] not in res:
                res[arr[0]] = {}
            if class_ not in res[arr[0]]:
                res[arr[0]][class_] = 1
            else:
                res[arr[0]][class_] += 1

    train.close()
    print(file_name + ':\tTotal: {}, set entry num: {} '.
          format(total, entry_num))
    print("time costs: {}".format(time.time() - s))

    # Work with additional dataset from https://www.kaggle.com/google-nlu/text-normalization
    files = ['output_1.csv', 'output_6.csv', 'output_11.csv', 'output_16.csv',
             'output_21.csv', 'output_91.csv', 'output_96.csv']

    for file_name in files:
        print("extracting from file {} ...".format(file_name))
        s1 = time.time()
        train = open(os.path.join(INPUT_PATH, 'tn', file_name), encoding='UTF8')
        train.readline()
        while 1:
            line = train.readline().strip()
            if line == '':
                break
            line = line.replace(',NA,', ',"NA",')
            total += 1
            pos0 = line.find('"')
            pos = line.find('","')
            class_ = line[pos0 + 1: pos]
            text = line[pos + 2:]
            if text[:3] == '","':
                continue
            text = text[1:-1]
            arr = text.split('","')
            if is_year(arr[0]):
                entry_num += 1
                if arr[0] not in res:
                    res[arr[0]] = {}
                if class_ not in res[arr[0]]:
                    res[arr[0]][class_] = 1
                else:
                    res[arr[0]][class_] += 1
        train.close()
        print(file_name + ':\tTotal: {}, set entry num: {} '.
              format(total, entry_num))
        print("time costs: {}".format(time.time() - s1))
    print("total time costs: {}".format(time.time() - s))
    with open(dict_pkl_name, "wb") as f:
        pkl.dump(res, f)
    print("set size: ", len(res))
    print("dict dumped!")


if __name__ == '__main__':
    extract()

