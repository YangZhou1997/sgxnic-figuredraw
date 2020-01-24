import json

def write_to_file(dict_obj, filename):
    with open(filename, 'w') as f:
        json.dump(dict_obj, f, indent=2)

def read_from_file(filename):
    with open(filename, 'r') as f:
        dict_obj = json.load(f)
    return dict_obj

def encode_list(list_obj):
    list_obj.sort()
    res = ''
    for ele in list_obj:
        res += str(ele) + '+'
    res = res.strip('+')
    return res

def decode_list(str_obj):
    ind = str_obj.split('+')
    return ind