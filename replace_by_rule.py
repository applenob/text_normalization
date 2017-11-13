# coding=utf-8
# @author: cer
# this script must run with python3
from __future__ import print_function
from num2words import num2words
import operator
import os
import pickle as pkl
import roman
from utils import *
import re
import inflect
from collections import OrderedDict
odd = "odd!~!"
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "output")
plain_dict_name = "plain_dict.pkl"
verbatim_dict_name = "verbatim_dict.pkl"
p = inflect.engine()


print("loading dicts...")
with open(os.path.join(OUTPUT_PATH, plain_dict_name), "rb") as f:
    plain_dict = pkl.load(f)
with open(os.path.join(OUTPUT_PATH, verbatim_dict_name), "rb") as f:
    verbatim_dict = pkl.load(f)
print("loading loaded.")


def replace_plain(token):
    """1.普通词汇"""
    if token not in plain_dict:
        res = token
    else:
        srtd = sorted(plain_dict[token].items(), key=operator.itemgetter(1), reverse=True)
        res = srtd[0][0]
    return res


def replace_puct(token):
    """2.标点符号，原样返回"""
    return token


def replace_date(token):
    """3.日期：年月日"""
    week_map = OrderedDict(
        [("monday,", "monday"),
         ("monday", "monday"),
         ("mon", "monday"),
         ("tuesday,", "tuesday"),
         ("tuesday", "tuesday"),
         ("tue", "tuesday"),
         ("wednesday,", "wednesday"),
         ("wednesday", "wednesday"),
         ("wed", "wednesday"),
         ("thursday,", "thursday"),
         ("thursday", "thursday"),
         ("thu", "thursday"),
         ("friday,", "friday"),
         ("friday", "friday"),
         ("fri", "friday"),
         ("saturday,", "saturday"),
         ("saturday", "saturday"),
         ("sat", "saturday"),
         ("sunday,", "sunday"),
         ("sunday", "sunday"),
         ("sun", "sunday"),
         ])
    year_map = OrderedDict(
        [("bce", "b c e"),
         ("b.c.", "b c"),
         ("bc.", "b c"),
         ("bc", "b c"),
         ("a.d.", "a d"),
         ("ad.", "a d"),
         ("ad", "a d"),
         ])
    token = token.strip().replace("'", "").lower()
    if token.endswith(","):
        token = token[:-1]
    if token.endswith(", "):
        token = token[:-2]
    measure = re.compile(r"|".join(week_map.keys()))
    matches = measure.findall(token)
    weeks = ""
    if len(matches) != 0:
        for one in matches:
            token = token.replace(one, "")
        token = token.strip()
        weeks = " ".join([week_map[one] for one in matches]) + " "
        weeks = weeks.replace(",", "")
    year_pat = r"{}".format("|".join(year_map.keys()))
    year_pat = year_pat.replace(".", r"\.")
    measure2 = re.compile(year_pat)
    match2 = measure2.search(token)
    years = ""
    if match2:
        # print(token)
        # print(year_pat)
        # print(match2.group())
        token = token.replace(match2.group(), "")
        token = token.strip()
        years = " " + year_map[match2.group()]
        years = years.replace(",", "")
    date_pt_l4 = re.compile(r"^\d{4}$")  # 2015
    date_pt_l3 = re.compile(r"^\d{3}$")  # 360
    date_pt_l2 = re.compile(r"^\d{3}$")  # 60
    date_pt_s = re.compile(r"^\d{4}s$")  # 2015s
    date_pt_s2 = re.compile(r"^\d{3}s$")  # 360s
    date_pt_s3 = re.compile(r"^\d{2}s$")  # 60s
    date_pt_slash = re.compile(r"^\d+/\d+/\d+$")  # 11/17/09
    date_pt_dash = re.compile(r"^\d+-\d+-\d+$")  # 2007-11-24
    date_pt_dot = re.compile(r"^\d+\.\d+\.\d+$")  # 2007.11.24
    res = token
    if date_pt_l4.match(token) or date_pt_l3.match(token) or date_pt_l2.match(token):  # 2015, 360, 60
        res = norm_year(token)
    elif date_pt_s.match(token):  # 2015s
        res = norm_year(token[:-1])
        arr = res.split()
        arr[-1] = p.plural(arr[-1])
        res = " ".join(arr)
    elif date_pt_s2.match(token):  # 360s
        res = norm_year(token[:-1])
        arr = res.split()
        arr[-1] = p.plural(arr[-1])
        res = " ".join(arr)
    elif date_pt_s3.match(token):  # 60s
        res = numstr2word(token[:-1])
        res = p.plural(res)
    elif date_pt_slash.match(token):
        arr = token.split("/")
        year_n, month_n, day_n, month_first = infer_year_month_day(arr, "/")
        res = norm_date(month_n, month_first=month_first, year_n=year_n, day_n=day_n)
    elif date_pt_dash.match(token):
        arr = token.split("-")
        year_n, month_n, day_n, month_first = infer_year_month_day(arr, "-")
        res = norm_date(month_n, month_first=month_first, year_n=year_n, day_n=day_n)
    elif date_pt_dot.match(token):
        arr = token.split(".")
        year_n, month_n, day_n, month_first = infer_year_month_day(arr, ".")
        res = norm_date(month_n, month_first=month_first, year_n=year_n, day_n=day_n)
    else:
        if token.endswith(","):
            token = token[:-1]
        token = token.replace(", ", " ").replace(",", " ").replace('"', "").replace("  ", " ")
        token = re.sub(r'(\d+)th', r'\g<1>', token)
        token = re.sub(r'(\d+)st', r'\g<1>', token)
        token = re.sub(r'(\d+)nd', r'\g<1>', token)
        token = re.sub(r'(\d+)rd', r'\g<1>', token)
        arr = token.split(" ")
        if len(arr) == 3:
            if arr[0].isdigit() and arr[2].isdigit():  # 21 September 2014
                year_n = arr[2]
                month_n = arr[1]
                day_n = arr[0]
                res = norm_date(month_n, month_first=False, year_n=year_n, day_n=day_n)
            elif arr[1].isdigit() and arr[2].isdigit():  # February 6, 2009
                year_n = arr[2]
                month_n = arr[0]
                day_n = arr[1]
                res = norm_date(month_n, month_first=True, year_n=year_n, day_n=day_n)
        elif len(arr) == 2:
            if arr[0].isdigit():  # 14 April
                month_n = arr[1]
                day_n = arr[0]
                res = norm_date(month_n, month_first=False, day_n=day_n)
            elif arr[1].isdigit() and len(arr[1]) > 2:  # June 2004
                year_n = arr[1]
                month_n = arr[0]
                res = norm_date(month_n, year_n=year_n)
            elif arr[1].isdigit() and len(arr[1]) <= 2:   # June 10
                month_n = arr[0]
                day_n = arr[1]
                res = norm_date(month_n, month_first=True, day_n=day_n)
    res = weeks + res + years
    return res


def test_replace_date():
    test_data = ["2006", "1987", "2000", "2005s", "4 March 2014", "50s", "7 August,2007",
                 "November 4, 2014", "11/17/09", "2007-11-24",
                 "25-08-2015", "14 April", "April 14", "June 2004", "17 November,"
                 "526 BC."]
    for one in test_data:
        print(one, " ", replace_date(one))


def replace_letters(token):
    """4.多个字母"""
    letter_map = {"é": "e acute",
                  "&": "and"}
    token = str(token).strip()
    if len(token) == 1:
        res = token
        for k, v in letter_map.items():
            res = res.replace(k, v)
        return res
    token = token.replace(",", "").replace(".", "").replace(" ", "")
    token = token.replace("-", "").replace("'", "").replace("/", "")
    ends = ""
    if len(token) > 1 and token.endswith("s") and has_upper(token):
        ends = "'s"
        token = token[:-1]
    res = " ".join(token.lower())
    for k, v in letter_map.items():
        res = res.replace(k, v)
    res += ends
    return res


def replace_cardinal(token):
    """5.普通数字"""
    token = token.replace('U.S.', "")
    token = token.replace(" ", "")
    token = token.replace('"', "")
    token = token.replace(',', "")
    token = token.replace('.', "")
    token = token.replace(':', "")
    minus = False
    if token[0] == "-":
        minus = True
        token = token[1:]
    token = token.replace('-', "")
    ends = ""
    if token.endswith("'s"):
        ends = "'s"
        token = token[:-2]
    if token.isdigit():
        res = numstr2word(token)
    else:
        # 可能是罗马数字
        try:
            num = roman.fromRoman(token)
            res = numstr2word(num)
        except roman.InvalidRomanNumeralError:
            res = token
    if minus:
        res = "minus " + res
    res = res + ends
    return res


def replace_verbatim(token):
    """6.逐字，大部分原样返回，先过一遍字典"""
    if token not in verbatim_dict:
        res = token
    else:
        srtd = sorted(verbatim_dict[token].items(), key=operator.itemgetter(1), reverse=True)
        res = srtd[0][0]
    return res


def replace_decimal(token):
    """7.带小数点的数字"""
    res = token.strip()
    if res == '.0':
        return "point o"
    res = res.replace(",", "")
    minus = False
    if res[0] == "-":
        res = res[1:]
        minus = True
    decimal = re.compile(r"^\d*\.*\d+")
    match = decimal.match(res)
    if match:
        target = match.group()
        # print(target)
        if type(target) == str:
            if "." not in target:
                num = numstr2word(target)
            else:
                arr = target.split(".")
                small_part = norm_digit(arr[1]).replace("zero", "o")
                if arr[0] == "":
                    num = "point " + small_part
                else:
                    # print(arr[0])
                    num = numstr2word(arr[0]) + " point " + small_part
                if num.endswith("point o"):
                    num = num.replace("point o", "point zero")
            res = res.replace(target, num)
            # if res.endswith("point o"):
            #     res = num.replace("point o", "point zero")
        if minus:
            res = "minus " + res
    return res


def test_replace_decimal():
    test_cases = [".266", "1,195.9", "1.0"]
    for one in test_cases:
        print(replace_decimal(one))


def replace_measure(token):
    """8.衡量单位"""
    # 默认是复数
    measure_map = OrderedDict(
                  [("MHz", "megahertz"),
                   ("kHz", "kilohertz"),
                   ("KHz", "kilohertz"),
                   ("GHz", "gigahertz"),
                   ("Hz", "hertz"),
                   ("atm", "atmospheres"),
                   ("cwt", "hundredweight"),
                   ("in", "inches"),
                   ("MPa", "megapascals"),
                   ("kcal", "kilo calories"),
                   ("mol", "mole"),
                   ('percent', 'percent'),
                   ('pc', 'percent'),
                   ('yr', 'years'),
                   ("m²", "square meters"),
                   ("m2", "square meters"),
                   ("m³", "cubic meters"),
                   ("m3", "cubic meters"),
                   ("mi²", "square miles"),
                   ("mi", "miles"),
                   ("μm", "micrometers"),
                   ("km²", "square kilometers"),
                   ("km2", "square kilometers"),
                   ("km", "kilometers"),
                   ("Km", "kilometers"),
                   ("mm", "millimeters"),
                   ("cm", "centimeters"),
                   ("nm", "nanometers"),
                   ("rpm", "revolutions per minute"),
                   ("kph", "kilometers per hour"),
                   ("kg", "kilograms"),
                   ("sq", "square"),
                   ("lbs", "pounds"),
                   ("lb", "pounds"),
                   ("cc", "c c"),
                   ("PB", "petabytes"),
                   ("TB", "terabytes"),
                   ("GB", "gigabytes"),
                   ("MB", "megabytes"),
                   ("KB", "kilobytes"),
                   ("kB", "kilobytes"),
                   ("KC", "kilo coulombs"),
                   ("mL", "milliliters"),
                   ("ml", "milliliters"),
                   ("mA", "milli amperes"),
                   ("ma", "milli amperes"),
                   ("ha", "hectares"),
                   ("ft", "feet"),
                   ("ch", "chains"),
                   ("mph", "miles per hour"),
                   ("hp", "horsepower"),
                   ("kW", "kilowatts"),
                   ("MW", "megawatts"),
                   ("Gs", "giga seconds"),

                   ("B", "bytes"),
                   ("day", "day"),
                   ("yd", "yards"),
                   ("/", "per"),
                   ("%", "percent"),
                   ("s", "second"),
                   ("h", "hour"),
                   ("m", "meters"),
                   ("g", "grams"),
                   ])
    replace_dict = OrderedDict([('""', "inches"), ("'", "feet")])
    # print(measure_map.keys())
    res = token.strip()
    measure = re.compile(r"{}".format("|".join(measure_map.keys())))
    matches = measure.findall(res)
    for k in replace_dict:
        if k in res:
            matches.append(k)
    if len(matches) != 0:
        reps = [measure_map[one] if one in measure_map else replace_dict[one] for one in matches]
        for one in matches:
            res = res.replace(one, "")
        res = res.strip()
        if len(res) != 0:
            num = replace_decimal(res) + " "
        else:
            num = ""
        res = num + " ".join(reps)
    return res


def test_replace_measure():
    test_case = ["17.5/km²", "9%", "147 m", '12""']
    for one in test_case:
        print(replace_measure(one))


def replace_money(token):
    """9.货币"""
    money_map = OrderedDict([
        ("usd", "united states dollars"),
        ("us$", "dollars"),
        ("a$", "dollars"),
        ("au$", "dollars"),
        ("nv$", "dollars"),
        ("hk$", "dollars"),
        ("r$", "reals"),
        ("rs", "rupees"),
        ("$", "dollars"),
        ("£", "pounds"),
        ("€", "euros"),
        ("¥", "yens")
    ])
    res = token.strip().lower()
    ends = ""
    if res.endswith("m"):
        res = res[:-1]
        ends = " million"
    elif res.endswith("b"):
        res = res[:-1]
        ends = " billion"
    elif res.endswith("bn"):
        res = res[:-2]
        ends = " billion"
    pattern_string = r"{}".format("|".join(money_map.keys())).replace("$", r"\$")
    money = re.compile(pattern_string)
    # print(money_map.keys())
    matches = money.findall(res)
    if len(matches) != 0:
        reps = [money_map[one] for one in matches]
        for one in matches:
            res = res.replace(one, "")
        res = res.strip()
        if len(res) != 0:
            num = replace_decimal(res)
        else:
            num = ""
        num += ends
        res = num + " " + " ".join(reps)
    return res


def test_replace_money():
    test_case = ["$247 million", "$44,583", "£1,000,000"]
    for one in test_case:
        print(replace_money(one))


def replace_ordinal(token):
    """10.序数词"""
    res = token.strip()
    replace_list = ["th", 'st', 'nd', 'rd', "."]
    for one in replace_list:
        res = res.replace(one, "")
    if res.isdigit():
        res = numstr2word(float(res), ordinal=True)
    else:
        # 可能是罗马数字
        try:
            num = roman.fromRoman(res)
            res = numstr2word(num, ordinal=True)
            res = "the " + res
        except roman.InvalidRomanNumeralError:
            pass
            # print("roman.InvalidRomanNumeralError", res)
    return res


def test_replace_ordinal():
    test_case = ["XXVth", "20th", "18th"]
    for one in test_case:
        print(replace_ordinal(one))


def replace_time(token):
    """11.时刻，如3:00 pm"""
    time_dict = OrderedDict([
        ("am", "a m"),
        ("AM", "a m"),
        ("a.m.", "a m"),
        ("A.M.", "a m"),
        ("pm", "p m"),
        ("PM", "p m"),
        ("p.m.", "p m"),
        ("P.M.", "p m"),
        ("IST", "i s t"),
        ("PST", "p s t"),
        ("CST", "c s t"),
        ("CET", "c e t"),
        ("EST", "e s t"),
        ("EDT", "e d t"),
        ("GMT", "g m t"),
        ("UTC", "u t c"),
        ("CEST", "c e s t"),
        ("KST", "k s t"),
        ("AEST", "a e s t"),
        ("PDT", "p d t"),
        ("ET", "e t"),
    ])
    res = token.strip()
    pattern_string = r"{}".format("|".join(time_dict.keys())).replace("$", r"\$")
    money = re.compile(pattern_string)
    # print(time_dict.keys())
    matches = money.findall(token)
    sufix = ''
    if len(matches) != 0:
        reps = [time_dict[one] for one in matches]
        for one in matches:
            res = res.replace(one, "")
        sufix = " " + " ".join(reps)
    res = res.strip()
    time = norm_time(res, sufix)
    res = time + sufix
    return res


def test_replace_time():
    test_case = ["2:37:42", "8:00 AM PST", "5:58 p.m.",
                 "2:11", "00  EDT"]
    for one in test_case:
        print(replace_time(one))


def replace_electronic(token):
    """12.网站地址"""
    electronic_map = {
        ".": "dot",
        "/": "slash",
        "-": "d a s h",
        ":": "colon",
    }
    res = token.strip()
    if res == "::":
        return res
    res = res.lower()
    if res[0] == "#":
        res = res.replace("#", "hash tag ")
        return res
    arr = []
    for c in res:
        if c in electronic_map:
            arr.append(electronic_map[c])
        elif c.isdigit():
            arr.append(" ".join(list(numstr2word(c))))
        else:
            arr.append(c)
    res = " ".join(arr)
    return res


def replace_digit(token):
    """13.单个数字"""
    res = token.strip()
    if res == "007":
        return "double o seven"
    res = res.replace("-", "")
    arr = []
    for c in res:
        if c.isdigit():
            if c == "0":
                arr.append("o")
            else:
                arr.append(numstr2word(c))
    res = " ".join(arr)
    return res


def replace_fraction(token):
    """14.分数，几分之几"""
    fraction_dict = {
        "½": "one half",
        "⅓": "one thirds",
        "⅔": "two thirds",
        "¼": "one quarter",
        "¾": "three quarters",
        "⅛": "one eighth",
        "⅝": "five eighths",
        "⅞": "seven eighths",
    }
    res = token.strip()
    res = res.replace(" / ", "/")
    res = res.replace("/ ", "/")
    res = res.replace(" /", "/")
    minus = False
    if res[0] == "-":
        minus = True
        res = res[1:]
    sufix = ""
    fraction = re.compile(r"{}".format("|".join(fraction_dict.keys())))
    matches = fraction.findall(token)
    if len(matches) != 0:
        reps = [fraction_dict[one] for one in matches]
        for one in matches:
            res = res.replace(one, "")
        res = res.strip()
        sufix = " " + " ".join(reps)
        if len(res) != 0:
            sufix = " and" + sufix
    prefix = ""
    if res.isdigit():
        res = numstr2word(res) + sufix
        res = res.replace(" and one ", " and a ")
        res = res.replace("halfs", "halves")
        return res
    if " " in res:
        arr = res.split()
        if arr[0].isdigit():
            prefix = numstr2word(arr[0]) + " and "
        res = arr[1]
    frac = res
    if "/" in res:
        arr = res.split("/")
        arr[0] = arr[0].replace(",", "")
        arr[1] = arr[1].replace(",", "")
        if arr[0].isdigit() and arr[1].isdigit():
            numerator = numstr2word(arr[0])
            denominator = numstr2word(arr[1], ordinal=True)
            if int(arr[1]) == 4:
                denominator = denominator.replace("fourth", "quarter")
            elif int(arr[1]) == 2:
                denominator = denominator.replace("second", "half")
            elif int(arr[1]) == 1:
                denominator = "over one"
            if int(arr[0]) == 1 or int(arr[1]) == 1:
                frac = numerator + " " + denominator
            else:
                frac = numerator + " " + denominator + "s"
    res = prefix + frac + sufix
    res = res.strip()
    if minus:
        res = "minus " + res
    res = res.replace(" and one ", " and a ")
    res = res.replace("halfs", "halves")
    return res


def replace_telephone(token):
    """15.电话号码"""
    res = token.strip().lower().replace("(", "").replace(" - ", "-")
    arr = []
    for c in res:
        if c.isdigit():
            if c == "0":
                arr.append("o")
            else:
                arr.append(numstr2word(c))
        elif c.isalpha():
            arr.append(c)
        else:
            arr.append("sil")
    res = " ".join(arr)
    res = re.sub(r'(sil )+', r'sil ', res)
    # pt = re.compile(r' (o )+')
    # match = pt.search(res)
    # if match:
    #     target = match.group()
    #     if type(target) == str:
    #         if len(target) == 7:
    #             res = res.replace(" o o o ", " thousand ")
    #         elif len(target) == 5:
    #             res = res.replace(" o o ", " hundred ")
    return res


def test_replace_telephone():
    test_case = ["01-312"]
    for one in test_case:
        print(replace_telephone(one))


def replace_address(token):
    """16.地址"""
    res = token.strip().lower()
    arr = []
    suffix = ""
    if len(res) > 1:
        if res.endswith("e"):
            res = res[:-1]
            suffix = " east"
        if res.endswith("w"):
            res = res[:-1]
            suffix = " west"
        if res.endswith("n"):
            res = res[:-1]
            suffix = " north"
        if res.endswith("e"):
            res = res[:-1]
            suffix = " south"
    for c in res:
        if c.isdigit():
            arr.append(c)
        elif c.isalpha():
            arr.append(c)
        else:
            continue
    res = "".join(arr)
    address = re.compile(r"[a-zA-Z]+\d+")  # A320
    match = address.match(res)
    if match:
        res = match.group()
        if type(res) == str:
            n_start = 0
            for i, c in enumerate(res):
                if c.isdigit():
                    n_start = i
                    break
            alphas = res[:n_start]
            nums = res[n_start:]
            if alphas == "interstate":  # Interstate 87
                alpha_str = alphas
            else:
                alpha_str = " ".join(alphas)
            if len(nums) <= 2:
                num_str = numstr2word(nums)
            elif len(nums) == 3 or len(nums) == 4:
                if int(nums[-2:]) < 10:
                    last_two = "o " + numstr2word(nums[-2:])
                else:
                    last_two = numstr2word(nums[-2:])
                num_str = numstr2word(nums[0: -2]) + " " + last_two
            else:
                num_str = " ".join(map(numstr2word, nums))
            num_str = num_str.replace("zero", "o")
            res = alpha_str + " " + num_str
    res += suffix
    return res

if __name__ == '__main__':
    test_replace_date()
    # test_replace_decimal()
    # test_replace_measure()
    # test_replace_money()
    # test_replace_ordinal()
    # test_replace_time()
    # test_replace_telephone()


