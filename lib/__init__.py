import random
import datetime


class AddableTime(datetime.time):
    """
    add time with random span
    """
    def __init__(self, *args, **kwargs):
        datetime.time.__init__(*args, **kwargs)

    def _to_datetime(self):
        return datetime.datetime.combine(datetime.date.today(), self)

    def __add__(self, that):
        dt = self._to_datetime()
        dt += that
        return AddableTime._from_datetime(dt)

    def __sub__(self, that):
        dt = self._to_datetime()
        dt -= that
        return AddableTime._from_datetime(dt)

    @staticmethod
    def _from_datetime(dt):
        return AddableTime(dt.hour, dt.minute, dt.second)

    def random_before(self, span):
        return self - random_delta(span)

    def random_after(self, span):
        return self + random_delta(span)

    def __str__(self):
        return self.strftime('%H:%M')


def random_delta(span):
    return datetime.timedelta(minutes=random.randrange(span))
