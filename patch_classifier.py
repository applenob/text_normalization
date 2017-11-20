# coding=utf-8
# @author: cer
# 有一些分类器分错的明显的错误，使用规则矫正。
# 这个脚本跟在分类器脚本后面跑。
from __future__ import print_function
import pandas as pd
import numpy as np
import re
import pickle as pkl
import time

pred_file = "output/class_pred_16.v2.5.csv"
out_file = "output/class_pred_16_fixed.v2.5.csv"
all_pred_file_name = "output/train_pred.v2.5.csv"
all_output_file_name = "output/train_pred.v2.5.fixed.2.csv"
change_file = "output/patch_change.csv"
train_file = "input/en_train.csv"
test_file = "input/en_test_2.csv"
labels = ['PLAIN', 'PUNCT', 'DATE', 'LETTERS', 'CARDINAL', 'VERBATIM',
          'DECIMAL', 'MEASURE', 'MONEY', 'ORDINAL', 'TIME', 'ELECTRONIC',
          'DIGIT', 'FRACTION', 'TELEPHONE', 'ADDRESS']
label2index = dict(zip(labels, range(len(labels))))
index2label = dict([(v, k) for k, v in label2index.items()])
# with open("output/letter_set.pkl", "rb") as f:
#     letter_set = pkl.load(f)
letters_name = "output/letter_dict.pkl"
with open(letters_name, "rb") as f:
    letter_dict = pkl.load(f)
# chem_dict = {"CO₂": "carbon di oxide",
#              "ZnI₂": "zinc iodide",
#              "NH₄": "ammonium",
#              "SiO₂": "silicon di oxide",
#              "CaCO₃": "calcium carbonate",
#              "CaCO3": "calcium carbonate",
#              "H₂O": "water",
#              "TiO2": "rutile"}
chem_dict = {"CO₂": "CO₂",
             "ZnI₂": "ZnI₂",
             "NH₄": "NH₄",
             "SiO₂": "SiO₂",
             "OH)₂": "OH)₂",
             "CaCO₃": "CaCO₃",
             "CaCO3": "CaCO3",
             "H₂O": "H₂O",
             "NH₃": "NH₃",
             "C₂₅H₂₁": "C₂₅H₂₁",
             "XeF₂": "XeF₂",
             "N₅O": "N₅O",
             "CH₃": "CH₃",
             "PI₃": "PI₃",
             "Cu₃O₇": "Cu₃O₇",
             "CH₂": "CH₂",
             "Zn(OH)₂": "Zn(OH)₂",
             "NH₂": "NH₂",
             "MnS₂": "MnS₂",
             "C₆H₂": "C₆H₂",
             "C₁₉H₁₆": "C₁₉H₁₆",
             "AlCl₃": "AlCl₃",
             "SO₂": "SO₂",
             "CCl₄": "CCl₄",
             "C₁₀H₆": "C₁₀H₆",
             "Ca₃(AsO₄)₂": "Ca₃(AsO₄)₂",
             "BaTiO3": "BaTiO3",
             "F₁F₂": "F₁F₂",
             "C₃H": "C₃H",
             "SiO4": "SiO4",
             "CO)₃": "CO)₃",
             "O₂N)₃": "O₂N)₃",
             "SiO₅": "SiO₅",
             "Ca5(PO4)3": "Ca5(PO4)3",
             "Na(SO4)2": "Na(SO4)2",
             "Mg₃B₇": "Mg₃B₇",
             "O₁₃Cl": "O₁₃Cl",
             "Li2O2": "Li2O2",
             "Li2O": "Li2O",
             "HNO₃": "HNO₃",
             "AlSi₃": "AlSi₃",
             "TiO2": "TiO2",
             "BeF₂": "BeF₂",
             "PbCl₂": "PbCl₂",
             "C₄H₄": "C₄H₄",
             "CO)₆": "CO)₆",
             "TiH1": "TiH1",
             "Pb₃As₄": "Pb₃As₄",
             "C₆H₄": "C₆H₄",
             }
dash_pat = re.compile(r"^[a-zA-Z]+-[a-zA-Z]+$")


def is_com(token):
    token = str(token)
    pt = re.compile(r"\.[a-zA-Z]{2,}")
    return True if pt.search(token) else False


def is_year(token):
    token = str(token)
    return token.isdigit() and len(token) == 4 and 1000 <= int(token) <= 2099


def has_measure_string(token):
    token = str(token)
    mea_strs = ['years', 'year', 'months', 'month', 'weeks', 'week', 'days', 'day',
                'hours', 'minutes', 'min', 'seconds', 'nautical', 'acres', 'hectares',
                'tonnes', 'tons', 'kilobytes', 'nanobarns', 'square', 'miles', 'kilometres',
                'kilometre', 'kilometers', 'kilometer', 'meters', 'meter', 'metres', 'metre',
                'feet', 'yards', 'barrels', 'calories', 'watts', 'knots', 'inches', 'pounds',
                'degrees', 'bar', 'Cellos']
    for one in mea_strs:
        if one in token:
            return True
    return False


def ends_with_measure_string(token):
    token = str(token)
    mea_strs = ['years', 'year', 'months', 'month', 'weeks', 'week', 'days',
                'hours', 'minutes', 'min', 'seconds', 'nautical', 'acres', 'hectares',
                'tonnes', 'tons', 'kilobytes', 'nanobarns', 'square', 'miles', 'kilometres',
                'kilometre', 'kilometers', 'kilometer', 'meters', 'meter', 'metres', 'metre',
                'feet', 'yards', 'barrels', 'calories', 'watts', 'knots', 'inches', 'pounds',
                'degrees', 'bar', 'Cellos']
    for one in mea_strs:
        if token.endswith(one):
            return True
    return False


def has_dash(token):
    token = str(token)
    if dash_pat.search(token):
        return True
    else:
        return False


def patch():
    test_df = pd.read_csv(test_file)
    pred_df = pd.read_csv(pred_file)
    pred_df["before"] = test_df["before"]
    print("start iterating...")
    data_num = pred_df.shape[0]
    count = 0
    change_list = []
    s = time.time()
    for i, row in pred_df.iterrows():
        # 1.被误认为是cardinal的实际上的date的年份
        if index2label[row["class_pred"]] != "DATE" and is_year(row["before"]):
            # 不能直接修改row，因为row是副本
            pred_df.loc[i, "class_pred"] = label2index["DATE"]
            row["class_before"] = index2label[row["class_pred"]]
            row["class_pred"] = "DATE"
            change_list.append(row)
        elif index2label[row["class_pred"]] == "PLAIN":
            # 2.被误认为是plain的实际上的electronic的网站
            if is_com(row["before"]):
                pred_df.loc[i, "class_pred"] = label2index["ELECTRONIC"]
                row["class_pred"] = "ELECTRONIC"
                row["class_before"] = "PLAIN"
                change_list.append(row)
            # 3.被误认为是plain的实际上是letters
            elif row["before"] in letter_dict["LETTERS"]:
                if row["before"] not in letter_dict["PLAIN"]:
                    change = True
                elif letter_dict["LETTERS"][row["before"]] > letter_dict["PLAIN"][row["before"]]:
                    change = True
                else:
                    change = False
                if change:
                    pred_df.loc[i, "class_pred"] = label2index["LETTERS"]
                    row["class_pred"] = "LETTERS"
                    row["class_before"] = "PLAIN"
                    change_list.append(row)
        # 3.被误认为是letters的实际上是plain的
        elif index2label[row["class_pred"]] == "LETTERS":
            # if row["before"] not in letter_dict["LETTERS"] or letter_dict["LETTERS"][row["before"]] \
            #         < letter_dict["PLAIN"][row["before"]]:
            if row["before"] in chem_dict:
                pred_df.loc[i, "class_pred"] = label2index["PLAIN"]
                row["class_pred"] = "PLAIN"
                row["class_before"] = "LETTERS"
                change_list.append(row)
        # 4.被误认为是decimal的实际上是measured
        elif index2label[row["class_pred"]] == "DECIMAL":
            if has_measure_string(row["before"]):
                pred_df.loc[i, "class_pred"] = label2index["MEASURE"]
                row["class_pred"] = "MEASURE"
                row["class_before"] = "DECIMAL"
                change_list.append(row)
        # 5.被误认为是date的实际上是measured
        elif index2label[row["class_pred"]] == "DATE":
            if ends_with_measure_string(row["before"]):
                pred_df.loc[i, "class_pred"] = label2index["MEASURE"]
                row["class_pred"] = "MEASURE"
                row["class_before"] = "DATE"
                change_list.append(row)
        # 6.被误认为是money的实际上是measured
        elif index2label[row["class_pred"]] == "MONEY":
            if has_measure_string(row["before"]):
                pred_df.loc[i, "class_pred"] = label2index["MEASURE"]
                row["class_pred"] = "MEASURE"
                row["class_before"] = "MONEY"
                change_list.append(row)
        # 7.被误认为是cardinal的实际上是measured
        elif index2label[row["class_pred"]] == "CARDINAL":
            if ends_with_measure_string(row["before"]):
                pred_df.loc[i, "class_pred"] = label2index["MEASURE"]
                row["class_pred"] = "MEASURE"
                row["class_before"] = "CARDINAL"
                change_list.append(row)
        # 8.被误认为是electronic的实际上是plain
        elif index2label[row["class_pred"]] == "ELECTRONIC":
            if has_dash(row["before"]):
                pred_df.loc[i, "class_pred"] = label2index["PLAIN"]
                row["class_pred"] = "PLAIN"
                row["class_before"] = "ELECTRONIC"
                change_list.append(row)
    print("time costs: ", time.time() - s)
    print("changed row num: ", len(change_list))
    change_df = pd.DataFrame(change_list)
    change_df.to_csv(change_file, index=False)
    print("save change rows to file: ", change_file)
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

