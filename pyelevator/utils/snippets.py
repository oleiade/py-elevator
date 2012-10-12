def ms_to_sec(ms):
    """Returns an Integer approximated value"""
    return int(ms / 1000)


def sec_to_ms(sec):
    """Returns an Integer approximated value"""
    if isinstance(sec, float):
        return float(sec * 1000)
    return int(sec * 1000)


# Enums beautiful python implementation
# Used like this :
# Numbers = enum('ZERO', 'ONE', 'TWO')
# >>> Numbers.ZERO
# 0
# >>> Numbers.ONE
# 1
# Found here: http://stackoverflow.com/questions/36932/whats-the-best-way-to-implement-an-enum-in-python
def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)
