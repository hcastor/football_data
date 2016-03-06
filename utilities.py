#Date created 2/20/15

def convertToInt(value):
    try:
        value = int(value)
    except ValueError:
        pass
    return value

def convertToNumber(value):
    try:
        return int(value)
    except ValueError:
        pass
    try:
        return float(value)
    except ValueError:
        pass
    return value

def cleanKey(value):
    return value.replace('.', '').replace('$', '')
