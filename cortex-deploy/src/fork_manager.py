"""
CORTEX — Fork Manager
Deploy brain to secondary server, sync data back.
Additive-only merge: MAX weights, primary wins on definitions.

Fork server: s1061738678.websitehome.co.uk
Doubles brain learning capacity by running two instances.

Usage: imported by online_server.py
"""
import time
import json
import os
import subprocess
import threading
from pathlib import Path


# Fork server config
FORK_HOST = 's1061738678.websitehome.co.uk'
FORK_USER = 'root'
FORK_DIR = '/var/www/cortex/'

# Sync protocol version
SYNC_VERSION = 1


class ForkManager:
    def __init__(self, studio_dir):
        self.studio_dir = Path(studio_dir)
        self.lock = threading.Lock()

        # Fork state
        self.fork_deployed = False
        self.last_deploy = None
        self.last_sync = None
        self.fork_status = 'not_deployed'  # not_deployed, deployed, syncing, error
        self.sync_count = 0
        self.nodes_merged = 0
        self.connections_merged = 0

        # Event log
        self.events = []
        self.max_events = 50

    def _log(self, msg):
        """Log a fork event."""
        entry = {
            'time': time.strftime('%Y-%m-%d %H:%M:%S'),
            'message': msg,
        }
        self.events.append(entry)
        if len(self.events) > self.max_events:
            self.events.pop(0)
        print('[FORK] %s' % msg)

    def deploy(self):
        """Deploy current brain to fork server.
        Copies brain.json files and server scripts."""
        with self.lock:
            self.fork_status = 'deploying'
            self._log('Starting deployment to %s...' % FORK_HOST)

        results = {'ok': False, 'files': []}

        try:
            # Files to deploy
            files = [
                ('left/brain.json', FORK_DIR + 'left/brain.json'),
                ('right/brain.json', FORK_DIR + 'right/brain.json'),
            ]

            for local_rel, remote in files:
                local = self.studio_dir / local_rel
                if not local.exists():
                    results['files'].append({'file': local_rel, 'ok': False, 'error': 'Not found'})
                    continue

                # Use scp (available on the Linux server)
                cmd = 'scp -o StrictHostKeyChecking=no "%s" %s@%s:"%s"' % (
                    local, FORK_USER, FORK_HOST, remote)

                try:
                    proc = subprocess.run(cmd, shell=True, capture_output=True, timeout=60, text=True)
                    ok = proc.returncode == 0
                    results['files'].append({
                        'file': local_rel, 'ok': ok,
                        'error': proc.stderr[:100] if not ok else None,
                    })
                except subprocess.TimeoutExpired:
                    results['files'].append({'file': local_rel, 'ok': False, 'error': 'Timeout'})

            all_ok = all(f['ok'] for f in results['files'])
            results['ok'] = all_ok

            with self.lock:
                if all_ok:
                    self.fork_deployed = True
                    self.last_deploy = time.strftime('%Y-%m-%d %H:%M:%S')
                    self.fork_status = 'deployed'
                    self._log('Deployment successful')
                else:
                    self.fork_status = 'error'
                    self._log('Deployment failed: %s' % str(results['files']))

        except Exception as e:
            results['error'] = str(e)
            with self.lock:
                self.fork_status = 'error'
                self._log('Deployment error: %s' % e)

        return results

    def sync(self, left_brain, right_brain):
        """Pull fork data back and merge using additive-only protocol.
        MAX weights for connections, primary wins on conflicting definitions."""
        with self.lock:
            self.fork_status = 'syncing'
            self._log('Starting sync from %s...' % FORK_HOST)

        results = {'ok': False, 'left_merged': 0, 'right_merged': 0}

        try:
            # Download fork brain.json files to temp
            temp_dir = self.studio_dir / 'fork_tmp'
            temp_dir.mkdir(exist_ok=True)

            for side in ['left', 'right']:
                remote = FORK_DIR + '%s/brain.json' % side
                local_tmp = temp_dir / ('%s_fork.json' % side)

                cmd = 'scp -o StrictHostKeyChecking=no %s@%s:"%s" "%s"' % (
                    FORK_USER, FORK_HOST, remote, local_tmp)

                try:
                    proc = subprocess.run(cmd, shell=True, capture_output=True, timeout=60, text=True)
                    if proc.returncode != 0:
                        self._log('Failed to download %s: %s' % (side, proc.stderr[:100]))
                        continue
                except subprocess.TimeoutExpired:
                    self._log('Timeout downloading %s' % side)
                    continue

                # Load fork data
                try:
                    with open(local_tmp, 'r') as f:
                        fork_data = json.load(f)
                except Exception as e:
                    self._log('Failed to parse %s fork data: %s' % (side, e))
                    continue

                # ADDITIVE-ONLY MERGE
                brain = left_brain if side == 'left' else right_brain
                merged = self._merge_additive(brain.data, fork_data)
                results['%s_merged' % side] = merged

                # Clean up
                try:
                    local_tmp.unlink()
                except Exception:
                    pass

            results['ok'] = True

            with self.lock:
                total = results.get('left_merged', 0) + results.get('right_merged', 0)
                self.nodes_merged += total
                self.sync_count += 1
                self.last_sync = time.strftime('%Y-%m-%d %H:%M:%S')
                self.fork_status = 'deployed'
                self._log('Sync complete: %d items merged' % total)

        except Exception as e:
            results['error'] = str(e)
            with self.lock:
                self.fork_status = 'error'
                self._log('Sync error: %s' % e)

        return results

    def _merge_additive(self, primary_data, fork_data):
        """Additive-only merge.
        - New nodes from fork are added
        - Connection weights: MAX of both
        - Definitions: primary wins on conflicts
        - Properties: merged (fork fills gaps, primary wins conflicts)
        """
        merged_count = 0
        primary_nodes = primary_data.get('nodes', {})
        fork_nodes = fork_data.get('nodes', {})

        for word, fork_node in fork_nodes.items():
            if word not in primary_nodes:
                # New word — add it entirely
                primary_nodes[word] = fork_node
                merged_count += 1
            else:
                primary_node = primary_nodes[word]

                # Merge connections: MAX weights
                fork_conns = fork_node.get('connections', {})
                prim_conns = primary_node.get('connections', {})
                for conn_word, weight in fork_conns.items():
                    if conn_word not in prim_conns:
                        prim_conns[conn_word] = weight
                        merged_count += 1
                    else:
                        prim_conns[conn_word] = max(prim_conns[conn_word], weight)

                # Fill gaps in properties (primary wins on conflicts)
                for key in ['means', 'emotion', 'role', 'source']:
                    if not primary_node.get(key) and fork_node.get(key):
                        primary_node[key] = fork_node[key]
                        merged_count += 1

                # Merge bigrams/trigrams
                for gram_type in ['bigrams', 'trigrams']:
                    fork_grams = fork_node.get(gram_type, {})
                    prim_grams = primary_node.get(gram_type, {})
                    for gram, count in fork_grams.items():
                        if gram not in prim_grams:
                            prim_grams[gram] = count
                        else:
                            prim_grams[gram] = max(prim_grams[gram], count)

        return merged_count

    def get_stats(self):
        """Get fork stats for dashboard."""
        with self.lock:
            return {
                'fork_host': FORK_HOST,
                'fork_status': self.fork_status,
                'fork_deployed': self.fork_deployed,
                'last_deploy': self.last_deploy,
                'last_sync': self.last_sync,
                'sync_count': self.sync_count,
                'total_nodes_merged': self.nodes_merged,
                'total_connections_merged': self.connections_merged,
                'recent_events': self.events[-20:],
            }
