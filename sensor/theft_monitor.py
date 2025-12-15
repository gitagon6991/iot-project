# sensor/theft_monitor.py
from collections import deque
from datetime import datetime, timedelta, UTC
import math

class TheftMonitor:
    def __init__(self,
                 window_seconds=600,            # keep last 10 minutes
                 check_seconds=60,              # evaluate drops over last 60s
                 abs_drop_m=0.10,               # alert if >0.10 m drop
                 pct_drop=0.05,                 # or >5% drop
                 require_consecutive=1,         # consecutive detections to confirm
                 smoothing_alpha=0.3):          # EMA smoothing for level
        self.window = timedelta(seconds=window_seconds)
        self.check_seconds = timedelta(seconds=check_seconds)
        self.abs_drop_m = abs_drop_m
        self.pct_drop = pct_drop
        self.require_consecutive = require_consecutive
        self.smoothed = None
        self.alpha = smoothing_alpha
        self.history = deque()  # elements = (timestamp, level_m)
        self.pending_count = 0

    def _add_reading(self, timestamp, level_m):
        self.history.append((timestamp, level_m))
        # drop old
        cutoff = timestamp - self.window
        while self.history and self.history[0][0] < cutoff:
            self.history.popleft()

    def update(self, level_m, when=None):
        """Call this on each new level reading.
        Returns alert dict if theft suspected, else None."""
        if when is None:
            # when = datetime.utcnow() deprecated: use explicit timestamp
            when = datetime.now(UTC)
        # smoothing (EMA)
        if self.smoothed is None:
            self.smoothed = level_m
        else:
            self.smoothed = self.alpha * level_m + (1-self.alpha) * self.smoothed

        self._add_reading(when, self.smoothed)

        # find reading ~ check_seconds ago (nearest)
        threshold_time = when - self.check_seconds
        # find last reading before or at threshold_time
        older = None
        for t, lv in reversed(self.history):
            if t <= threshold_time:
                older = (t, lv)
                break
        # if no older reading exists, we can use earliest in window
        if older is None and self.history:
            older = self.history[0]

        if not older:
            return None  # not enough history

        older_time, older_level = older
        drop_m = older_level - self.smoothed
        # avoid negative (increase)
        if drop_m <= 0:
            self.pending_count = 0
            return None

        # percent drop relative to older_level
        pct = drop_m / older_level if older_level and older_level > 0 else 0.0

        # compute rate (m per minute)
        secs = max((when - older_time).total_seconds(), 1)
        m_per_min = drop_m / secs * 60.0

        # detection rules
        abrupt_by_abs = drop_m >= self.abs_drop_m
        abrupt_by_pct = pct >= self.pct_drop

        if abrupt_by_abs or abrupt_by_pct:
            self.pending_count += 1
        else:
            self.pending_count = 0

        if self.pending_count >= self.require_consecutive:
            # compose alert
            alert = {
                "type": "theft_detected",
                "detected_at": when.isoformat(),
                "drop_m": round(drop_m, 4),
                "drop_pct": round(pct*100, 3),
                "duration_seconds": secs,
                "rate_m_per_min": round(m_per_min, 4),
                "older_time": older_time.isoformat(),
                "older_level": older_level,
                "current_level": round(self.smoothed, 4)
            }
            # reset pending to avoid duplicate alerts for same event
            self.pending_count = 0
            return alert

        return None

    # utility to force clear
    def reset(self):
        self.history.clear()
        self.smoothed = None
        self.pending_count = 0
