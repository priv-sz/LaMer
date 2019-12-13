import yaml

config_path =  '/home/user/Program/ws/monitor_web/config/config.yaml'
with open(config_path, "r") as yaml_file:
    # yaml_obj = yaml_file.readlines()
    yaml_obj = yaml.load(yaml_file.read())
    # for i in yaml_obj:
    #     if eval(i)['host'] == '49.232.149.241':
    #         kk = eval(i)

    print(yaml_obj)