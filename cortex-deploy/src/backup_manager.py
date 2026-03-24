"""
CORTEX — Backup Manager
Timestamped local JSON copies of brain data.
Atomic writes, auto-backup every 30 minutes, retention policy.
Keeps last 48 backups + 1 daily for last 7 days.

Usage: imported by online_server.py
"""
import os
import time
import json
import shutil
import threading
from pathlib import Path


class BackupManager:
    def __init__(self, studio_dir):
        self.studio_dir = Path(studio_dir)
        self.backup_dir = self.studio_dir / 'backups'
        self.backup_dir.mkdir(exist_ok=True)

        self.left_json = self.studio_dir / 'left' / 'brain.json'
        self.right_json = self.studio_dir / 'right' / 'brain.json'
        self.lock = threading.Lock()
        self.last_backup = None
        self.backup_count = 0

        # Count existing backups
        self.backup_count = len(list(self.backup_dir.glob('left_*.json')))
        print('[BACKUP] Backup dir: %s (%d existing)' % (self.backup_dir, self.backup_count))

        # Start auto-backup thread
        threading.Thread(target=self._auto_backup_loop, daemon=True).start()

    def _atomic_copy(self, src, dst):
        """Copy file atomically: write to .tmp, fsync, rename."""
        tmp = str(dst) + '.tmp'
        try:
            shutil.copy2(str(src), tmp)
            # fsync the tmp file
            fd = os.open(tmp, os.O_RDONLY)
            try:
                os.fsync(fd)
            finally:
                os.close(fd)
            os.replace(tmp, str(dst))
            return True
        except Exception as e:
            print('[BACKUP] Atomic copy failed: %s' % e)
            # Clean up tmp if it exists
            try:
                os.unlink(tmp)
            except Exception:
                pass
            return False

    def backup_now(self):
        """Create an immediate backup of both hemispheres."""
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        results = {'timestamp': timestamp, 'files': []}

        with self.lock:
            for name, src in [('left', self.left_json), ('right', self.right_json)]:
                if not src.exists():
                    results['files'].append({'name': name, 'ok': False, 'error': 'Source not found'})
                    continue

                dst = self.backup_dir / ('%s_%s.json' % (name, timestamp))
                ok = self._atomic_copy(src, dst)
                size_mb = round(os.path.getsize(str(dst)) / (1024 * 1024), 2) if ok and dst.exists() else 0

                results['files'].append({
                    'name': name,
                    'ok': ok,
                    'file': str(dst.name),
                    'size_mb': size_mb,
                })

            self.last_backup = timestamp
            self.backup_count += 1

        # Prune old backups
        self._prune()

        print('[BACKUP] Backup #%d created: %s' % (self.backup_count, timestamp))
        return results

    def _prune(self):
        """Enforce retention: keep last 48 + 1 daily for 7 days."""
        for prefix in ['left', 'right']:
            backups = sorted(self.backup_dir.glob('%s_*.json' % prefix))

            if len(backups) <= 48:
                continue

            # Keep the last 48
            keep = set(str(b) for b in backups[-48:])

            # Also keep 1 per day for last 7 days
            daily_kept = set()
            for b in reversed(backups):
                day = b.stem.split('_')[1][:8]  # YYYYMMDD
                if day not in daily_kept and len(daily_kept) < 7:
                    daily_kept.add(day)
                    keep.add(str(b))

            # Delete everything else
            for b in backups:
                if str(b) not in keep:
                    try:
                        b.unlink()
                    except Exception:
                        pass

    def _auto_backup_loop(self):
        """Auto-backup every 30 minutes."""
        # Wait 5 minutes before first backup (let brain load)
        time.sleep(300)
        while True:
            try:
                self.backup_now()
            except Exception as e:
                print('[BACKUP] Auto-backup error: %s' % e)
            time.sleep(1800)  # 30 minutes

    def list_backups(self):
        """List all available backups."""
        backups = []
        # Group by timestamp
        timestamps = set()
        for f in sorted(self.backup_dir.glob('*.json'), reverse=True):
            if f.name.endswith('.tmp'):
                continue
            parts = f.stem.split('_', 1)
            if len(parts) == 2:
                timestamps.add(parts[1])

        for ts in sorted(timestamps, reverse=True)[:50]:
            entry = {'timestamp': ts, 'files': {}}
            for prefix in ['left', 'right']:
                f = self.backup_dir / ('%s_%s.json' % (prefix, ts))
                if f.exists():
                    entry['files'][prefix] = {
                        'size_mb': round(os.path.getsize(str(f)) / (1024 * 1024), 2),
                        'file': f.name,
                    }
            if entry['files']:
                backups.append(entry)

        return backups

    def restore(self, timestamp, confirm=False):
        """Restore brain from a backup. Requires confirm=True."""
        if not confirm:
            return {'ok': False, 'error': 'Set confirm=true to actually restore. This overwrites current brain data!'}

        results = {'timestamp': timestamp, 'restored': []}

        # First, backup current state
        current_backup = self.backup_now()

        with self.lock:
            for prefix in ['left', 'right']:
                backup_file = self.backup_dir / ('%s_%s.json' % (prefix, timestamp))
                if not backup_file.exists():
                    results['restored'].append({'name': prefix, 'ok': False, 'error': 'Backup not found'})
                    continue

                target = self.studio_dir / prefix / 'brain.json'
                ok = self._atomic_copy(backup_file, target)
                results['restored'].append({'name': prefix, 'ok': ok})

        results['pre_restore_backup'] = current_backup['timestamp']
        results['note'] = 'Server restart required to load restored data'
        return results

    def get_stats(self):
        """Get backup stats for dashboard."""
        backups = self.list_backups()
        total_size = 0
        for b in backups:
            for f in b['files'].values():
                total_size += f.get('size_mb', 0)

        return {
            'backup_count': len(backups),
            'total_size_mb': round(total_size, 2),
            'last_backup': self.last_backup,
            'auto_interval_min': 30,
            'retention': '48 recent + 7 daily',
            'backups': backups[:20],  # Last 20 for display
        }
