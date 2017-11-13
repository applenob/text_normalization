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
set_pkl_name = "../output/letter_set.pkl"
target_class = "LETTERS"


def extract():
    print('extracting start...')

    # Work with primary dataset
    s = time.time()
    file_name = "en_train.csv"
    print("extracting from file {} ...".format(file_name))
    train = open(os.path.join(INPUT_PATH, file_name), encoding='UTF8')
    train.readline()
    res = set()
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
        if class_ == target_class:
            entry_num += 1
            text = line[pos + 2:]
            if text[:3] == '","':
                continue
            text = text[1:-1]
            arr = text.split('","')
            res.add(arr[0])
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
            if class_ == target_class:
                entry_num += 1
                text = line[pos + 2:]
                if text[:3] == '","':
                    continue
                text = text[1:-1]
                arr = text.split('","')
                res.add(arr[0])
        train.close()
        print(file_name + ':\tTotal: {}, set entry num: {} '.
              format(total, entry_num))
        print("time costs: {}".format(time.time() - s1))
    print("total time costs: {}".format(time.time() - s))
    with open(set_pkl_name, "wb") as f:
        pkl.dump(res, f)
    print("set size: ", len(res))
    print("dict dumped!")


def double_check():
    with open(set_pkl_name, "rb") as f:
        letter_set = pkl.load(f)
    print("set size: ", len(letter_set))
    # Work with primary dataset
    s = time.time()
    file_name = "en_train.csv"
    print("extracting from file {} ...".format(file_name))
    train = open(os.path.join(INPUT_PATH, file_name), encoding='UTF8')
    train.readline()
    total = 0
    entry_num = 0
    while 1:
        line = train.readline().strip()
        if line == '':
            break
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
            if arr[0] in letter_set:
                letter_set.remove(arr[0])
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
            if class_ == "PLAIN":
                entry_num += 1
                text = line[pos + 2:]
                if text[:3] == '","':
                    continue
                text = text[1:-1]
                arr = text.split('","')
                if arr[0] in letter_set:
                    letter_set.remove(arr[0])
        train.close()
        print(file_name + ':\tTotal: {}, set entry num: {} '.
              format(total, entry_num))
        print("time costs: {}".format(time.time() - s1))
    print("total time costs: {}".format(time.time() - s))
    with open(set_pkl_name, "wb") as f:
        pkl.dump(letter_set, f)
    print("set size: ", len(letter_set))
    print("dict dumped!")

if __name__ == '__main__':
    # extract()
    double_check()