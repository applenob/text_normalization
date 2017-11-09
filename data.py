# coding=utf-8
# @author: cer

import random
import numpy as np
import os


seperate = "\t\t"
same_classes = ['PLAIN', 'PUNCT']
flatten = lambda l: [item for sublist in l for item in sublist]  # 二维展成一维
index_seq2slot = lambda s, index2slot: [index2slot[i] for i in s]
index_seq2word = lambda s, index2word: [index2word[i] for i in s]


def data_pipeline(data, length=30):

    seq_in, seq_out, intent = list(zip(*data))
    sin = []
    sout = []
    # padding，原始序列和标注序列结尾+<EOS>+n×<PAD>
    for i in range(len(seq_in)):
        temp = seq_in[i]
        if len(temp) < length:
            temp.append('<EOS>')
            while len(temp) < length:
                temp.append('<PAD>')
        else:
            temp = temp[:length]
            temp[-1] = '<EOS>'
        sin.append(temp)

        temp = seq_out[i]
        if len(temp) < length:
            while len(temp) < length:
                temp.append('<PAD>')
        else:
            temp = temp[:length]
            temp[-1] = '<EOS>'
        sout.append(temp)
        data = list(zip(sin, sout, intent))
    return data


def get_info_from_training_data(my_train_dir, is_filter=False):
    char2index = {'<PAD>': 0, '<UNK>': 1, '<EOS>': 2}
    word2index = {'<PAD>': 0, '<UNK>': 1, '<EOS>': 2}
    for f_name in os.listdir(my_train_dir):
        if f_name.endswith(".txt"):
            with open(os.path.join(my_train_dir, f_name)) as f:
                for line in f:
                    before, class_, after = line.strip().split(seperate)
                    for c in before + after:
                        if c not in char2index:
                            char2index[c] = len(char2index)
                    if is_filter and class_ in same_classes:
                        continue
                    for w in (before + " " + after).split():
                        if w not in word2index:
                            word2index[w] = len(word2index)

    index2word = {v: k for k, v in word2index.items()}
    index2char = {v: k for k, v in char2index.items()}
    return char2index, index2char, word2index, index2word


def getBatch(batch_size, train_data):
    random.shuffle(train_data)
    sindex = 0
    eindex = batch_size
    while eindex < len(train_data):
        batch = train_data[sindex:eindex]
        temp = eindex
        eindex = eindex + batch_size
        sindex = temp
        yield batch


def to_index(train, char2index, class2index):
    new_train = []
    for before, class_, after in train:
        before_ix = list(map(lambda i: char2index[i] if i in char2index else char2index["<UNK>"],
                             before))
        before_true_length = before.index("<EOS>")
        class_ix = class2index[class_]
        after_ix = list(map(lambda i: char2index[i] if i in char2index else char2index["<UNK>"],
                            after))
        after_true_length = after.index("<EOS>")
        new_train.append([before_ix, before_true_length, class_ix, after_ix, after_true_length])
    return new_train

if __name__ == '__main__':
    get_info_from_training_data("input/my", is_filter=True)
