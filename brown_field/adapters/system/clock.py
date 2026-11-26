"""The system clock, the default `Clock` (decision 0013)."""

import datetime


class SystemClock:
    def now(self) -> datetime.datetime:
        # Read at each call, through the module, so `time_machine` controls it
        # (decision 0008, kept by 0013).
        return datetime.datetime.now().astimezone()
