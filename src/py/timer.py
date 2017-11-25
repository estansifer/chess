import time

class Timer:
    def __init__(self):
        self.intervals = []
        self.cur = None

    def __enter__(self):
        self.cur = time.perf_counter()

    def __exit__(self, *args, **kwargs):
        x = time.perf_counter() - self.cur
        self.intervals.append(x)

    go = __enter__
    stop = __exit__

    def last(self):
        return self.intervals[-1]

    def summary(self):
        i = list(self.intervals)
        i.sort()
        s = '{} instances, {:.3f} total seconds, {:.3f} average, {:.3f} median, {:.3f} max'
        s = s.format(len(i), sum(i), sum(i) / len(i), i[len(i) // 2], i[-1])
        return s
