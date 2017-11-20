# coding=utf-8
# @author=cer
import pandas as pd

target_class = "TELEPHONE"
elec_file = target_class + ".csv"
new_elec_file = target_class + ".txt"
elec_df = pd.read_csv(elec_file)
with open(new_elec_file, "w") as f:
    for before, gold, my_replace in zip(elec_df["before"], elec_df["after"], elec_df["my_replaces"]):
        f.write(before + "\n")
        f.write(gold + "\n")
        f.write(my_replace + "\n")
        f.write("\n")


