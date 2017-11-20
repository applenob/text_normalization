# coding=utf-8
# @author: cer
# this script must run with python3
from __future__ import print_function
from num2words import num2words
import os
import time
import pandas as pd
import numpy as np
import pickle as pkl
import operator

out_file_name = "output/res_16.v2.5.csv"
out_debug_name = "output/res_16.v2.5.debug.csv"
final_file_name = "output/res_16.v2.5.final.csv"
final_debug_name = "output/res_16.v2.5.debug.final.csv"
diff_file_name = "output/diff_with_shot.csv"
change_file_name = "output/patch_replace_change.csv"


def filter_func(row):
    return row["before"] not in ["-", ":", "~"] and row["class_pred"] != "LETTERS" \
            and row["class_pred"] != "DIGIT" and row["class_pred"] != "CARDINAL" \
            and "_letter" not in row["res"]


def get_diff(use_csv=False):
    if use_csv:
        diff_df = pd.read_csv(diff_file_name, index_col=0)
    else:
        with open("output/res_dict.pkl", "rb") as f:
            res = pkl.load(f)
        diffs = []
        for i, row in debug_df.iterrows():
            if row["before"] in res:
                srtd = sorted(res[row["before"]].items(), key=operator.itemgetter(1), reverse=True)
                if row["after"] != srtd[0][0]:
                    row["res"] = srtd[0][0]
                    row["hit_num"] = res[row["before"]][row["res"]]
                    diffs.append(row)
        diff_df = pd.DataFrame(diffs)
        diff_df.to_csv(diff_file_name)
    return diff_df


out_df = pd.read_csv(out_file_name)
debug_df = pd.read_csv(out_debug_name, index_col=0)

# print(debug_df.index)
# print(diff_df.index)

print("getting diff data frame ...")
diff_df = get_diff(use_csv=False)

print("patch replacing !!!")
changes = []

for ind in out_df.index:
    # if debug_df.loc[ind, "class_pred"] == "CARDINAL":
    if str(debug_df.loc[ind, "after"]).startswith("the "):
        if ind > 0 and debug_df.loc[ind - 1, "after"] == "the":
            change_row = debug_df.loc[ind].copy()
            out_df.loc[ind, "after"] = out_df.loc[ind, "after"][4:]
            debug_df.loc[ind, "after"] = debug_df.loc[ind, "after"][4:]
            change_row["patch"] = debug_df.loc[ind, "after"]
            changes.append(change_row)

letters_df = diff_df.loc[diff_df["class_pred"] == "LETTERS"]
filter_df = diff_df.loc[diff_df.apply(filter_func, axis=1)]

for ind in letters_df.index:
    change_row = debug_df.loc[ind].copy()
    out_df.loc[ind, "after"] = letters_df.loc[ind]["res"]
    debug_df.loc[ind, "after"] = letters_df.loc[ind]["res"]
    change_row["patch"] = letters_df.loc[ind]["res"]
    changes.append(change_row)
for ind in filter_df.index:
    change_row = debug_df.loc[ind].copy()
    out_df.loc[ind, "after"] = filter_df.loc[ind]["res"]
    debug_df.loc[ind, "after"] = filter_df.loc[ind]["res"]
    change_row["patch"] = filter_df.loc[ind]["res"]
    changes.append(change_row)

# 手动
hands = [(951379, "eight million square meters"),
         (76840, "the twelfth of november eighteen seventy four"),
         (92722, "the first of october twenty fifteen"),
         (143256, "the first december"),
         (146855, "three thirty seven thousand five hundred sixths"),
         (153008, "the sixteenth june"),
         (187150, "november nineteen fifty nine"),
         (280902, "the twelfth of june nineteen forty two"),
         (287914, "eighty nine a d"),
         (326168, "the first of december"),
         (333277, "point seven acre"),
         (345670, "the tenth of october twenty eleven"),
         (384677, "the second of december twenty fifteen"),
         (390645, "the nineteenth of may"),
         (414951, "zero dollars"),
         (436624, "PHP387M"),
         (540441, "the fifth of may twenty seventeen"),
         (552852, "april third"),
         (587815, "point seven metre"),
         (668987, "minus two thousand per hectares"),
         (734463, "twenty million dollars"),
         (737333, "thursday the seventeenth of november twenty sixteen"),
         (791053, "the twenty third of march nineteen ninety eight"),
         (822943, "the tenth of april twenty fourteen"),
         (892611, "point none mile"),
         (939175, "point seven kilometer"),
         (822943, "the tenth of april twenty fourteen"),
         ]
for hand in hands:
    change_row = debug_df.loc[hand[0]].copy()
    out_df.loc[hand[0], "after"] = hand[1]
    debug_df.loc[hand[0], "after"] = hand[1]
    change_row["patch"] = hand[1]
    changes.append(change_row)


print("change nums: ", len(changes))
change_df = pd.DataFrame(changes)
change_df.to_csv(change_file_name)
out_df.to_csv(final_file_name, index=False)
debug_df.to_csv(final_debug_name, index=False)
print("patch change file save to: ", change_file_name)
print("final out file save to: ", final_file_name)
print("final debug file save to: ", final_debug_name)


