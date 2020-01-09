


def float2int(x):
    for key, value in x.items():
        if type(value) == float:
            x[key] = int(value)
    return x