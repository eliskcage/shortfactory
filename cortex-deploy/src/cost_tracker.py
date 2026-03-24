"""
CORTEX — API Cost Tracker
Tracks Grok and Pinata API calls with timestamps.
Estimates costs, tracks daily/hourly totals, 7-day rolling history.
Persists counters to cost_log.json hourly.

Usage: imported by online_server.py
"""
import time
import json
import os
import threading
from pathlib import Path
from collections import defaultdict

# Cost estimates per call type
COSTS = {
    'grok_enrich': 0.001,      # ~$0.001 per enrichment call (grok-3-mini-fast)
    'grok_judge': 0.002,       # ~$0.002 per judge call (longer prompt)
    'grok_chat': 0.001,        # ~$0.001 per user chat enrichment
    'pinata_save': 0.0005,     # ~$0.0005 per IPFS pin (tiny JSON)
    'wikipedia': 0.0,          # free
    'ddg': 0.0,                # free
}

# Alert thresholds (USD per day)
DEFAULT_ALERT_DAILY = 5.0
DEFAULT_ALERT_MONTHLY = 100.0


class CostTracker:
    def __init__(self, studio_dir):
        self.studio_dir = Path(studio_dir)
        self.log_file = self.studio_dir / 'cost_log.json'
        self.lock = threading.Lock()

        # In-memory counters
        self.calls = []  # [{type, time, cost}]
        self.total_calls = defaultdict(int)
        self.total_cost = 0.0
        self.boot_time = time.time()

        # Alert thresholds
        self.alert_daily = DEFAULT_ALERT_DAILY
        self.alert_monthly = DEFAULT_ALERT_MONTHLY

        # Load persisted data
        self._load()

        # Start hourly persist thread
        threading.Thread(target=self._persist_loop, daemon=True).start()

    def _load(self):
        """Load persisted cost data."""
        if self.log_file.exists():
            try:
                with open(self.log_file, 'r') as f:
                    data = json.load(f)
                self.total_calls = defaultdict(int, data.get('total_calls', {}))
                self.total_cost = data.get('total_cost', 0.0)
                # Load recent calls (last 24h only to keep memory small)
                cutoff = time.time() - 86400
                self.calls = [c for c in data.get('calls', []) if c.get('time', 0) > cutoff]
                print('[COST] Loaded cost data: $%.4f total, %d calls today' % (
                    self.total_cost, len(self.calls)))
            except Exception as e:
                print('[COST] Error loading cost data: %s' % e)

    def _save(self):
        """Persist cost data to disk."""
        try:
            # Keep only last 7 days of call records
            cutoff = time.time() - 604800
            recent = [c for c in self.calls if c.get('time', 0) > cutoff]

            data = {
                'total_calls': dict(self.total_calls),
                'total_cost': round(self.total_cost, 6),
                'calls': recent,
                'last_save': time.strftime('%Y-%m-%d %H:%M:%S'),
            }
            tmp = str(self.log_file) + '.tmp'
            with open(tmp, 'w') as f:
                json.dump(data, f)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp, str(self.log_file))
        except Exception as e:
            print('[COST] Error saving: %s' % e)

    def _persist_loop(self):
        """Save cost data every hour."""
        while True:
            time.sleep(3600)
            with self.lock:
                self._save()

    def record(self, call_type):
        """Record an API call."""
        cost = COSTS.get(call_type, 0.001)
        entry = {
            'type': call_type,
            'time': time.time(),
            'cost': cost,
        }
        with self.lock:
            self.calls.append(entry)
            self.total_calls[call_type] += 1
            self.total_cost += cost

    def get_stats(self):
        """Get cost statistics for the dashboard."""
        now = time.time()
        with self.lock:
            # Last 24h
            day_cutoff = now - 86400
            day_calls = [c for c in self.calls if c['time'] > day_cutoff]
            day_cost = sum(c['cost'] for c in day_calls)

            # Last hour
            hour_cutoff = now - 3600
            hour_calls = [c for c in self.calls if c['time'] > hour_cutoff]
            hour_cost = sum(c['cost'] for c in hour_calls)

            # By type (last 24h)
            by_type = defaultdict(lambda: {'count': 0, 'cost': 0.0})
            for c in day_calls:
                by_type[c['type']]['count'] += 1
                by_type[c['type']]['cost'] += c['cost']

            # Hourly breakdown (last 24h)
            hourly = defaultdict(lambda: {'count': 0, 'cost': 0.0})
            for c in day_calls:
                hour_key = time.strftime('%H:00', time.localtime(c['time']))
                hourly[hour_key]['count'] += 1
                hourly[hour_key]['cost'] += c['cost']

            # Projections
            uptime_hours = max((now - self.boot_time) / 3600, 0.1)
            total_recent = sum(self.total_calls.values())
            calls_per_hour = len(day_calls) / min(uptime_hours, 24)
            cost_per_hour = day_cost / min(uptime_hours, 24) if day_calls else 0
            projected_daily = cost_per_hour * 24
            projected_monthly = projected_daily * 30

            # Alerts
            alerts = []
            if day_cost >= self.alert_daily:
                alerts.append({'level': 'critical', 'msg': 'Daily spend $%.2f exceeds $%.2f limit' % (day_cost, self.alert_daily)})
            elif day_cost >= self.alert_daily * 0.8:
                alerts.append({'level': 'warning', 'msg': 'Daily spend $%.2f approaching $%.2f limit' % (day_cost, self.alert_daily)})
            if projected_monthly >= self.alert_monthly:
                alerts.append({'level': 'warning', 'msg': 'Projected monthly $%.2f exceeds $%.2f budget' % (projected_monthly, self.alert_monthly)})

            return {
                'total_cost': round(self.total_cost, 4),
                'total_calls': dict(self.total_calls),
                'day': {
                    'cost': round(day_cost, 4),
                    'calls': len(day_calls),
                    'by_type': {k: {'count': v['count'], 'cost': round(v['cost'], 4)} for k, v in by_type.items()},
                },
                'hour': {
                    'cost': round(hour_cost, 4),
                    'calls': len(hour_calls),
                },
                'hourly_breakdown': {k: {'count': v['count'], 'cost': round(v['cost'], 4)} for k, v in sorted(hourly.items())},
                'projections': {
                    'calls_per_hour': round(calls_per_hour, 1),
                    'cost_per_hour': round(cost_per_hour, 4),
                    'daily': round(projected_daily, 2),
                    'monthly': round(projected_monthly, 2),
                },
                'alerts': alerts,
                'uptime_hours': round(uptime_hours, 1),
                'boot_time': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.boot_time)),
            }
