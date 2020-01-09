import json


a_list = list(map(lambda x: eval(x), a))

with open('aaa.json', 'w') as f:
    json.dump(a_list, f, ensure_ascii=False, indent=4)
