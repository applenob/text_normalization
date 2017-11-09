# coding=utf-8
# @author: cer
# this script must run with python3
from __future__ import print_function
from num2words import num2words

odd = "odd!~!"


def norm_year(token):
    token = token.strip()
    if len(token) == 4:
        # 2015
        if token[2] == '0' and token[3] == '0' and token[1] != '0':
            y1 = token[:2]
            return num2words(float(y1)) + ' hundred'
        elif token[1] == '0' and token[2] == '0':
            y1 = token[0]
            y2 = token[3:]
            ys2 = " " + num2words(float(y2)) if y2 != "0" else ""
            return num2words(float(y1)) + ' thousand' + ys2
        else:
            y1 = token[: 2]
            y2 = token[2:]
            ys2 = num2words(float(y2)).replace("-", " ")
            if int(y2) < 10:
                ys2 = "o " + ys2
            return num2words(float(y1)).replace("-", " ") + ' ' + ys2
    elif len(token) == 2:
        # 09
        return " ".join(map(lambda x: 'o' if x == '0' else num2words(float(x)), list(token)))
    else:
        return odd


def test_norm_year():
    year = "2007"
    print(norm_year(year))


def norm_month(token):
    months = ["january", "february", "march", "april",
              "may", "june", "july", "august",
              "september", "october", "november", "december"]
    months_prefix = list(map(lambda m: m[:3], months))
    if token.isdigit():
        if int(token) > 12:
            return odd
        return months[int(token)-1]
    else:
        if token[:3].lower() not in months_prefix:
            return odd
        return months[months_prefix.index(token[:3].lower())]


def test_norm_month():
    mon = "Mar"
    print(norm_month(mon))


def norm_day(token):
    return num2words(float(token), ordinal=True).replace("-", " ")


def norm_date(month_n, month_first=True, year_n="", day_n=""):
    if year_n == "":
        year_s = ""
    else:
        year_s = " " + norm_year(year_n)
    if day_n == "":
        day_s = ""
        month_first = True
    else:
        day_s = " " + norm_day(day_n)
    if month_first:
        res = norm_month(month_n) + day_s \
              + year_s
    else:
        res = "the" + day_s + " of " + norm_month(month_n) \
              + year_s

    return res


def int2order_string(num):
    """暂时只支持31以内的"""
    ordinals = ["first", "second", "third", "fourth", "fifth",
                "sixth", "seventh", "eighth", "ninth", "tenth",
                "eleventh", "twelfth", "thirteenth", "fourteenth", "fifteenth",
                "sixteenth", "seventeenth", "eighteenth", "nineteenth", "twentieth",
                "twenty first", "twenty second", "twenty third", "twenty fourth", "twenty fifth",
                "twenty sixth", "twenty seventh", "twenty eighth", "twenty ninth", "thirtieth",
                "thirty-first"]
    return ordinals[int(num) - 1]


def norm_time(time, sufix):
    time = time.strip()
    sep = ""
    if ":" in time:
        sep = ":"
    elif "." in time:
        sep = "."
    if sep == "":
        if time.isdigit():
            return numstr2word(time)
        else:
            return time
    arr = time.split(sep)
    arr = [one.strip() for one in arr]
    if len(arr) == 2 and arr[0].isdigit() and arr[1].isdigit():
        min_s = " " + numstr2word(arr[1])
        if int(arr[1]) == 0:
            if sufix == "":
                min_s = " o'clock"
            else:
                min_s = ""
        elif int(arr[1]) < 10:
            min_s = ' o' + min_s
        return numstr2word(arr[0]) + min_s
    if len(arr) == 3 and arr[0].isdigit() and arr[1].isdigit() and arr[2].isdigit():
        return numstr2word(arr[0]) + " hours " + \
               numstr2word(arr[1]) + " minutes and " + \
               numstr2word(arr[2]) + " seconds"
    else:
        return time


def numstr2word(num, ordinal=False):
    """using num2word"""
    return num2words(float(num), ordinal=ordinal).replace("-", " ").replace(" and ", " ").replace(",", "")


def norm_digit(num):
    # print([num2words(float(one)) for one in num])
    return " ".join([num2words(float(one)) for one in num])


def has_upper(token):
    for c in token:
        if c.isupper():
            return True
    return False

if __name__ == '__main__':
    test_norm_month()
    # test_norm_year()