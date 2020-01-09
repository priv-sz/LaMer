config_path = 'config/config.txt'
with open(config_path, 'r') as conf:
    txt_conf = conf.readlines()
for i in txt_conf:
    print(eval(i))
