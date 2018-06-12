""" This File contains helper functions.
"""
import datetime
import re


def parse_date(date_str):
    """This function returns a datetime.date object parsed from 
    the passed value or False if the passed string was not a date
    also it checks if date is already in the past and returns false as well."""
    type_one = re.compile('.{4}-.{2}-.{2}')
    type_two = re.compile('.{2}\..{2}\..{4}')
    type_three = re.compile('.{2}/.{2}/.{4}')
    type_four = re.compile('.{4}/.{2}/.{2}')
    if type_one.match(date_str):
        date_arr = re.split("-", date_str, 2)
        try:
            date_arr = [int(d) for d in date_arr]
        except Exception as e:
            return False
        try:
            date = datetime.date(date_arr[0], date_arr[1], date_arr[2])
        except:
            return False
        if (date-datetime.date.today()).days < 0:
            return False
        else:
            return date

    if type_two.match(date_str):
        date_arr = re.split("\.", date_str, 2)
        try:
            date_arr = [int(d) for d in date_arr]
        except Exception as e:
            return False
        try:
            date = datetime.date(date_arr[2], date_arr[1], date_arr[0])
        except:
            return False
        if (date-datetime.date.today()).days < 0:
            return False
        else:
            return date

    if type_three.match(date_str):
        date_arr = re.split("/", date_str, 2)
        try:
            date_arr = [int(d) for d in date_arr]
        except Exception as e:
            return False
        try:
            date = datetime.date(date_arr[2], date_arr[1], date_arr[0])
        except:
            return False
        if (date-datetime.date.today()).days < 0:
            return False
        else:
            return date

    if type_four.match(date_str):
        date_arr = re.split("/", date_str, 2)
        try:
            date_arr = [int(d) for d in date_arr]
        except Exception as e:
            return False
        try:
            date = datetime.date(date_arr[0], date_arr[1], date_arr[2])
        except:
            return False
        if (date-datetime.date.today()).days < 0:
            return False
        else:
            return date

    return False


def array_max_val(arr, division="None"):
    val = 0
    if division.lower() == "sdi":
        arr = filter(lambda v: v >= 10000, arr)
    elif division.lower() == "ipe":
        arr = filter(lambda v: v < 10000, arr)
    for v in arr:
        if int(v) > val:
            val = int(v)

    return val


def isNum(val):
    """Returns true if val is a number that can  be parsed as an integer"""
    try:
        int(val)
    except:
        return False
    return True


def read_bom(_file: str):
    rows = _file.strip("b'").replace("\\r\\n", '\n').split("\n")
    exb = []
    a5e = []
    gwe = []
    failed = []
    # with open(_file) as file:
        # rows = file.readlines()
    header = rows[0].split(";")

    rows = rows[1:-1]

    for row in rows:
        temp = dict()
        row = row.strip("\n").strip("\r").split(";")
        for i, head in enumerate(header):
            try:
                temp[str(head)] = row[i]
            except Exception as e:
                print("""__1__ :{0}\\{2}: {1}""".format(head, e, i), "\n\n {}".format(row))
        if "exb" in temp["EXB"].lower():
            exb.append(temp)
        elif "a5e" in temp["EXB"].lower():
            a5e.append(temp)
        elif "gwe" in temp["EXB"].lower():
            gwe.append(temp)
        else:
            failed.append(temp)
  
    return exb, a5e, gwe, failed


def clean_exb_scan(exb_scan):
    expr = re.compile("EXB\d\d\d\d\d\d")
    res = expr.search(exb_scan)
    return res.group()


def is_ids(word):
    expr = re.compile("IDS\d*")
    res = expr.search(word)
    try:
        if res:
            ids = res.group().strip("IDS")
            ids = int(ids)
        else:
            return None
    except:
        return None
    return ids
    

def is_exb(word):
    expr = re.compile("EXB\d\d\d\d\d\d")
    res = expr.search(word)
    return res


def is_container(word):
    expr = re.compile("container\d*")
    res = expr.search(word)
    try:
        if res:
            id = res.group().strip("container")
            id = int(id)
        else:
            id = int(word)
    except:
        return None
    return id
    

def recommend_containers(part, amount):
    containers = sorted(part.containers, key=lambda c: c.in_stock())
    ret = []
    for c in containers:
        if c.in_stock() <= 0:
            continue
        if amount <= c.in_stock():
            ret.append([c, amount])
            # print(ret, "first")
            return ret
        else:
            for c in containers:
                if amount <= c.in_stock():
                    ret.append([c, amount])
                    # print(ret, "second")
                    return ret
                else:
                    # print(ret, "third")
                    ret.append([c, c.in_stock()])
                    # if c.place():
                    #     c.place().clear()
                    amount = amount-c.in_stock()
    # print(ret)
    return ret


def parse_board_abbr(code):
    for i, c in enumerate(code[::-1]):
        last = 0
        try:
            c = int(c)
        except:
            last = len(code)-i
            print(code[last])
            break
    return code[:last]


def parse_code(word):
    expr = re.compile("[a-zA-Z0-9]*.\d+")
    res = expr.search(word)
    if res:
        return res.group()
    else:
        return None
