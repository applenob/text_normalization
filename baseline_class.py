# coding=utf-8
# @author: cer
# use python3
from __future__ import print_function
import os
import operator
from num2words import num2words  # 这个包不支持中文
import gc
import pandas as pd
import numpy as np
import time
import pickle as pkl

train_file_name = "input/en_train.csv"
test_file = 'input/en_test_2.csv'
baseline_file = 'output/baseline_class.csv'
pkl_name = "output/class_dict.pkl"
train_df = pd.read_csv(train_file_name)
test_df = pd.read_csv(test_file)


def train():
    print('Train start...')
    if os.path.exists(pkl_name):
        with open(pkl_name, "rb") as f:
            res = pkl.load(f)
    else:
        # Work with primary dataset
        train_file = open(train_file_name, encoding='UTF8')
        train_file.readline()
        res = dict()
        total = 0
        not_same = 0
        while 1:
            line = train_file.readline().strip()
            if line == '':
                break
            total += 1
            pos = line.find('","')
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
        train_file.close()
        print(train_file_name + ':\tTotal: {} Have diff value: {}'.format(total, not_same))

        # Work with additional dataset from https://www.kaggle.com/google-nlu/text-normalization
        files = ['output_1.csv', 'output_6.csv', 'output_11.csv', 'output_16.csv', \
                 'output_21.csv', 'output_91.csv', 'output_96.csv']

        for add_file_name in files:
            train_file = open(os.path.join("input", 'tn', add_file_name), encoding='UTF8')
            train_file.readline()
            while 1:
                line = train_file.readline().strip()
                if line == '':
                    break
                line = line.replace(',NA,', ',"NA",')
                total += 1
                pos = line.find('","')
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
            train_file.close()
            print(add_file_name + ':\tTotal: {} Have diff value: {}'.format(total, not_same))

    return res


def solve(res):
    sdict = {}
    sdict['km2'] = 'square kilometers'
    sdict['km'] = 'kilometers'
    sdict['kg'] = 'kilograms'
    sdict['lb'] = 'pounds'
    sdict['dr'] = 'doctor'
    sdict['m²'] = 'square meters'

    total = 0
    changes = 0
    out = open(baseline_file, "w", encoding='UTF8')
    out.write('"id","after"\n')
    test = open(test_file, encoding='UTF8')
    test.readline().strip()
    while 1:
        line = test.readline().strip()
        if line == '':
            break

        pos = line.find(',')
        i1 = line[:pos]
        line = line[pos + 1:]

        pos = line.find(',')
        i2 = line[:pos]
        line = line[pos + 1:]

        line = line[1:-1]
        out.write('"' + i1 + '_' + i2 + '",')
        if line in res:
            srtd = sorted(res[line].items(), key=operator.itemgetter(1), reverse=True)
            out.write('"' + srtd[0][0] + '"')
            changes += 1
        else:
            # line.split(' ')
            if len(line) > 1:
                val = line.split(',')
                if len(val) == 2 and val[0].isdigit and val[1].isdigit:
                    line = ''.join(val)

            if line.isdigit():
                srtd = line.translate(SUB)
                srtd = srtd.translate(SUP)
                srtd = srtd.translate(OTH)
                out.write('"' + num2words(float(srtd)) + '"')
                changes += 1
            elif len(line.split(' ')) > 1:
                val = line.split(' ')
                for i, v in enumerate(val):
                    if v.isdigit():
                        srtd = v.translate(SUB)
                        srtd = srtd.translate(SUP)
                        srtd = srtd.translate(OTH)
                        val[i] = num2words(float(srtd))
                    elif v in sdict:
                        val[i] = sdict[v]

                out.write('"' + ' '.join(val) + '"')
                changes += 1
            else:
                out.write('"' + line + '"')

        out.write('\n')
        total += 1

    print('Total: {} Changed: {}'.format(total, changes))
    test.close()
    out.close()

if __name__ == '__main__':
    res = train()
    solve(res)
