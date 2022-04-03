import random

import psutil

metric_specs = {
    "cpu",
    "ram",
}

static_specs = {
    "random",
}


def get_actual_specs(spec):
    begin, end, spec = spec
    args = spec.split(",")
    tp = args[0]

    if tp in metric_specs:
        getter = get_metric_spec
    elif tp in static_specs:
        getter = get_static_spec
    else:
        return []

    return getter(begin, end, tp, args)


def get_metric_spec(begin, end, tp, args):
    rev = "rev" in args
    if tp == "cpu":
        value = psutil.cpu_percent(1)
    elif tp == "ram":
        value = psutil.virtual_memory().percent

    if rev:
        empty_begin = begin
        empty_end = begin + int((end - begin) * (100 - value) / 100)
        fill_begin = empty_end
        fill_end = end
    else:
        fill_begin = begin
        fill_end = begin + int((end - begin) * value / 100)
        empty_begin = fill_end
        empty_end = end

    return [
        [fill_begin, fill_end, 255, 0, 0],
        [empty_begin, empty_end, 0, 255, 255],
    ]


def get_static_spec(begin, end, tp, args):
    result = []

    if tp == "random":
        for i in range(begin, end):
            result += [[
                i,
                i+1,
                random.randint(64, 255),
                random.randint(64, 255),
                random.randint(64, 255),
            ]]

    return result
