def ms_to_sec(ms):
    """Returns an Integer approximated value"""
    return int(ms / 1000)


def sec_to_ms(sec):
    """Returns an Integer approximated value"""
    if isinstance(sec, float):
        return float(sec * 1000)
    return int(sec * 1000)
