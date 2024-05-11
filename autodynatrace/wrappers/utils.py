def func_name(view_func):
    if hasattr(view_func, "__name__"):
        return view_func.__name__
    return f"{view_func}"


def normalize_vendor(name):
    return name
