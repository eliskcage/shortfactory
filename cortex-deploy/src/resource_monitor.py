"""
CORTEX — Resource Monitor
CPU, memory, disk monitoring for the brain process.
Brain file sizes, growth projections, overclock analysis.

Usage: imported by online_server.py
"""
import os
import time
import threading
from pathlib import Path

# Try psutil, fallback to basic /proc parsing
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False
    print('[RESOURCE] psutil not available — using basic monitoring')


class ResourceMonitor:
    def __init__(self, studio_dir):
        self.studio_dir = Path(studio_dir)
        self.left_json = self.studio_dir / 'left' / 'brain.json'
        self.right_json = self.studio_dir / 'right' / 'brain.json'
        self.boot_time = time.time()
        self.lock = threading.Lock()

        # Track brain file size history for growth projections
        self.size_history = []  # [{time, left_mb, right_mb}]
        self._record_sizes()

        # Start size tracking thread (every 30 min)
        threading.Thread(target=self._size_track_loop, daemon=True).start()

    def _get_file_size_mb(self, path):
        """Get file size in MB."""
        try:
            return os.path.getsize(path) / (1024 * 1024) if path.exists() else 0
        except Exception:
            return 0

    def _record_sizes(self):
        """Record current brain file sizes."""
        entry = {
            'time': time.time(),
            'left_mb': round(self._get_file_size_mb(self.left_json), 2),
            'right_mb': round(self._get_file_size_mb(self.right_json), 2),
        }
        with self.lock:
            self.size_history.append(entry)
            # Keep last 336 entries (7 days at 30min intervals)
            if len(self.size_history) > 336:
                self.size_history = self.size_history[-336:]

    def _size_track_loop(self):
        """Record brain sizes every 30 minutes."""
        while True:
            time.sleep(1800)
            self._record_sizes()

    def _get_process_stats(self):
        """Get current process stats."""
        pid = os.getpid()
        if HAS_PSUTIL:
            try:
                proc = psutil.Process(pid)
                mem = proc.memory_info()
                return {
                    'pid': pid,
                    'cpu_percent': proc.cpu_percent(interval=0.5),
                    'memory_rss_mb': round(mem.rss / (1024 * 1024), 1),
                    'memory_vms_mb': round(mem.vms / (1024 * 1024), 1),
                    'threads': proc.num_threads(),
                    'open_files': len(proc.open_files()),
                    'uptime_hours': round((time.time() - self.boot_time) / 3600, 1),
                }
            except Exception as e:
                return {'pid': pid, 'error': str(e)}
        else:
            # Basic fallback
            return {
                'pid': pid,
                'uptime_hours': round((time.time() - self.boot_time) / 3600, 1),
                'note': 'Install psutil for detailed stats: pip3 install psutil',
            }

    def _get_system_stats(self):
        """Get system-wide stats."""
        if HAS_PSUTIL:
            try:
                mem = psutil.virtual_memory()
                disk = psutil.disk_usage('/')
                cpu_count = psutil.cpu_count()
                cpu_freq = psutil.cpu_freq()
                return {
                    'cpu_count': cpu_count,
                    'cpu_percent': psutil.cpu_percent(interval=0.5),
                    'cpu_freq_mhz': round(cpu_freq.current, 0) if cpu_freq else None,
                    'cpu_freq_max_mhz': round(cpu_freq.max, 0) if cpu_freq and cpu_freq.max else None,
                    'memory_total_mb': round(mem.total / (1024 * 1024), 0),
                    'memory_used_mb': round(mem.used / (1024 * 1024), 0),
                    'memory_percent': mem.percent,
                    'disk_total_gb': round(disk.total / (1024 ** 3), 1),
                    'disk_used_gb': round(disk.used / (1024 ** 3), 1),
                    'disk_free_gb': round(disk.free / (1024 ** 3), 1),
                    'disk_percent': round(disk.percent, 1),
                }
            except Exception as e:
                return {'error': str(e)}
        return {'note': 'Install psutil for system stats'}

    def _get_growth_projection(self):
        """Project brain growth rate and when limits will be hit."""
        with self.lock:
            history = list(self.size_history)

        if len(history) < 2:
            return {'note': 'Need more data points for projection'}

        first = history[0]
        last = history[-1]
        hours_elapsed = max((last['time'] - first['time']) / 3600, 0.1)

        left_growth = (last['left_mb'] - first['left_mb']) / hours_elapsed
        right_growth = (last['right_mb'] - first['right_mb']) / hours_elapsed
        total_growth = left_growth + right_growth

        current_total = last['left_mb'] + last['right_mb']

        # Projections
        projections = {
            'current_total_mb': round(current_total, 2),
            'left_mb': round(last['left_mb'], 2),
            'right_mb': round(last['right_mb'], 2),
            'growth_mb_per_hour': round(total_growth, 4),
            'growth_mb_per_day': round(total_growth * 24, 2),
        }

        # Time to milestones
        if total_growth > 0:
            milestones = [50, 100, 250, 500, 1000]  # MB
            for ms in milestones:
                if current_total < ms:
                    hours_to = (ms - current_total) / total_growth
                    days_to = hours_to / 24
                    projections['days_to_%dmb' % ms] = round(days_to, 1)

        # Overclock analysis
        projections['overclock'] = {
            '2x_speed': {
                'growth_mb_per_day': round(total_growth * 24 * 2, 2),
                'note': 'Doubling ramble speed doubles growth and API costs',
            },
            '4x_speed': {
                'growth_mb_per_day': round(total_growth * 24 * 4, 2),
                'note': 'Quadrupling speed — 4x API costs, ~4x memory growth',
            },
        }

        return projections

    def get_stats(self):
        """Get full resource stats for the dashboard."""
        return {
            'process': self._get_process_stats(),
            'system': self._get_system_stats(),
            'brain_files': {
                'left_mb': round(self._get_file_size_mb(self.left_json), 2),
                'right_mb': round(self._get_file_size_mb(self.right_json), 2),
                'total_mb': round(self._get_file_size_mb(self.left_json) + self._get_file_size_mb(self.right_json), 2),
            },
            'growth': self._get_growth_projection(),
            'size_history': [
                {'time': time.strftime('%H:%M', time.localtime(s['time'])),
                 'left': s['left_mb'], 'right': s['right_mb']}
                for s in self.size_history[-24:]  # Last 12 hours
            ],
        }
