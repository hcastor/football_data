def convertToInt(value):
    try:
        value = int(value)
    except ValueError:
        pass
    return value