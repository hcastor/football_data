#Date created 2/20/15

def convertToNumber(value):
    """
    Used to blindly convert any mongo value to either an int or float.
    """
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
    """
    Used to provide consistent key formats in mongo
    """
    return value.replace('.', '').replace('$', '').replace(' ', '_').lower().strip()
